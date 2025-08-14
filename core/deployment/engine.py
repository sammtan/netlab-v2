"""NetLab deployment engine for orchestrating device and network deployment."""

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core.backends.manager import BackendManager
from core.backends import BackendType, DeviceHandle, DeviceState
from .topology import TopologyLoader, NetworkTopology, DeviceConfig, NetworkConfig


logger = logging.getLogger(__name__)


class DeploymentEngine:
    """Orchestrates NetLab topology deployments."""
    
    def __init__(self, backend_manager: Optional[BackendManager] = None):
        self.backend_manager = backend_manager or BackendManager()
        self._deployments: Dict[str, Dict[str, Any]] = {}
    
    def plan_deployment(self, topology: NetworkTopology) -> Dict[str, Any]:
        """Plan a topology deployment and validate requirements."""
        plan = {
            "topology_name": topology.name,
            "can_deploy": True,
            "networks": [],
            "devices": [],
            "resource_requirements": {},
            "warnings": [],
            "errors": []
        }
        
        # Validate backends are available
        requires_vms = any(d.backend_type == "vm" for d in topology.devices)
        requires_containers = any(d.backend_type == "container" for d in topology.devices)
        
        validation = self.backend_manager.validate_deployment_requirements({
            "requires_vms": requires_vms,
            "requires_containers": requires_containers
        })
        
        if not validation["can_deploy"]:
            plan["can_deploy"] = False
            plan["errors"].extend([f"Missing backend: {b}" for b in validation["missing_backends"]])
        
        # Plan networks
        network_backend = self.backend_manager.get_preferred_network_backend()
        if not network_backend:
            plan["can_deploy"] = False
            plan["errors"].append("No network backend available")
        else:
            for network in topology.networks:
                plan["networks"].append({
                    "name": network.name,
                    "subnet": network.subnet,
                    "backend": network_backend.get_backend_type().value
                })
        
        # Plan devices
        total_memory_mb = 0
        total_cpu_cores = 0
        
        for device in topology.devices:
            backend = None
            if device.backend_type == "vm":
                backend = self.backend_manager.get_compute_backend(BackendType.VM_VIRTUALBOX)
            elif device.backend_type == "container":
                backend = self.backend_manager.get_compute_backend(BackendType.CTR_DOCKER)
            
            if not backend:
                plan["can_deploy"] = False
                plan["errors"].append(f"No backend available for device {device.name} (type: {device.backend_type})")
                continue
            
            plan["devices"].append({
                "name": device.name,
                "device_type": device.device_type,
                "backend_type": device.backend_type,
                "backend": backend.get_backend_type().value,
                "cpu_cores": device.cpu_cores,
                "memory_mb": device.memory_mb,
                "disk_size_gb": device.disk_size_gb
            })
            
            total_memory_mb += device.memory_mb
            total_cpu_cores += device.cpu_cores
        
        # Resource requirements summary
        plan["resource_requirements"] = {
            "total_memory_mb": total_memory_mb,
            "total_memory_gb": total_memory_mb / 1024,
            "total_cpu_cores": total_cpu_cores,
            "device_count": len(topology.devices),
            "network_count": len(topology.networks)
        }
        
        return plan
    
    def deploy_topology(self, topology: NetworkTopology, 
                       workspace_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Deploy a complete topology."""
        deployment_id = f"{topology.name}-{int(time.time())}"
        
        logger.info(f"Starting deployment: {deployment_id}")
        
        deployment = {
            "id": deployment_id,
            "topology_name": topology.name,
            "status": "deploying",
            "networks": {},
            "devices": {},
            "start_time": time.time(),
            "errors": []
        }
        
        self._deployments[deployment_id] = deployment
        
        try:
            # Step 1: Create networks
            logger.info("Creating networks...")
            network_backend = self.backend_manager.get_preferred_network_backend()
            if not network_backend:
                raise RuntimeError("No network backend available")
            
            for network in topology.networks:
                try:
                    network_id = network_backend.create_network(network.name, network.subnet)
                    deployment["networks"][network.name] = {
                        "network_id": network_id,
                        "subnet": network.subnet,
                        "status": "created"
                    }
                    logger.info(f"Created network: {network.name} -> {network_id}")
                except Exception as e:
                    error_msg = f"Failed to create network {network.name}: {e}"
                    deployment["errors"].append(error_msg)
                    logger.error(error_msg)
            
            # Step 2: Create devices
            logger.info("Creating devices...")
            for device in topology.devices:
                try:
                    device_handle = self._create_device(device, deployment["networks"], workspace_dir)
                    deployment["devices"][device.name] = {
                        "handle": device_handle,
                        "status": device_handle.state.value,
                        "backend": device_handle.backend_type.value
                    }
                    logger.info(f"Created device: {device.name} -> {device_handle.id}")
                except Exception as e:
                    error_msg = f"Failed to create device {device.name}: {e}"
                    deployment["errors"].append(error_msg)
                    logger.error(error_msg)
            
            # Step 3: Start devices
            logger.info("Starting devices...")
            for device_name, device_info in deployment["devices"].items():
                try:
                    device_handle = device_info["handle"]
                    backend = self.backend_manager.get_backend_for_device(device_handle)
                    if backend:
                        backend.start_device(device_handle)
                        device_info["status"] = device_handle.state.value
                        logger.info(f"Started device: {device_name}")
                except Exception as e:
                    error_msg = f"Failed to start device {device_name}: {e}"
                    deployment["errors"].append(error_msg)
                    logger.error(error_msg)
            
            # Update final status
            if deployment["errors"]:
                deployment["status"] = "partial"
                logger.warning(f"Deployment {deployment_id} completed with errors")
            else:
                deployment["status"] = "running"
                logger.info(f"Deployment {deployment_id} completed successfully")
            
        except Exception as e:
            deployment["status"] = "failed"
            error_msg = f"Deployment failed: {e}"
            deployment["errors"].append(error_msg)
            logger.error(error_msg)
        
        deployment["end_time"] = time.time()
        deployment["duration"] = deployment["end_time"] - deployment["start_time"]
        
        return deployment
    
    def _create_device(self, device: DeviceConfig, networks: Dict[str, Any],
                      workspace_dir: Optional[Path] = None) -> DeviceHandle:
        """Create a single device."""
        if device.backend_type == "vm":
            backend = self.backend_manager.get_compute_backend(BackendType.VM_VIRTUALBOX)
            if not backend:
                raise RuntimeError(f"VirtualBox backend not available for {device.name}")
            
            # Find or create image path
            image_path = self._resolve_image_path(device, workspace_dir)
            spec = TopologyLoader.create_vm_spec(device, image_path)
            return backend.create_vm(spec)
            
        elif device.backend_type == "container":
            backend = self.backend_manager.get_compute_backend(BackendType.CTR_DOCKER)
            if not backend:
                raise RuntimeError(f"Docker backend not available for {device.name}")
            
            spec = TopologyLoader.create_container_spec(device)
            return backend.create_ctr(spec)
            
        else:
            raise ValueError(f"Unsupported backend type: {device.backend_type}")
    
    def _resolve_image_path(self, device: DeviceConfig, workspace_dir: Optional[Path] = None) -> Path:
        """Resolve device image path."""
        if device.image:
            image_path = Path(device.image)
            if image_path.is_absolute() and image_path.exists():
                return image_path
        
        # Look in workspace images directory
        if workspace_dir:
            images_dir = workspace_dir / "images"
            potential_paths = [
                images_dir / f"{device.device_type}.iso",
                images_dir / f"{device.device_type}.ova",
                images_dir / f"{device.device_type}.vmdk"
            ]
            
            for path in potential_paths:
                if path.exists():
                    return path
        
        # Return a placeholder path (deployment will fail if image doesn't exist)
        return Path(f"/tmp/netlab-images/{device.device_type}.iso")
    
    def destroy_deployment(self, deployment_id: str) -> bool:
        """Destroy a complete deployment."""
        if deployment_id not in self._deployments:
            logger.warning(f"Deployment {deployment_id} not found")
            return False
        
        deployment = self._deployments[deployment_id]
        logger.info(f"Destroying deployment: {deployment_id}")
        
        # Stop and destroy devices
        for device_name, device_info in deployment["devices"].items():
            try:
                device_handle = device_info["handle"]
                backend = self.backend_manager.get_backend_for_device(device_handle)
                if backend:
                    backend.destroy_device(device_handle)
                    logger.info(f"Destroyed device: {device_name}")
            except Exception as e:
                logger.error(f"Failed to destroy device {device_name}: {e}")
        
        # Destroy networks
        network_backend = self.backend_manager.get_preferred_network_backend()
        if network_backend:
            for network_name, network_info in deployment["networks"].items():
                try:
                    network_backend.delete_network(network_info["network_id"])
                    logger.info(f"Destroyed network: {network_name}")
                except Exception as e:
                    logger.error(f"Failed to destroy network {network_name}: {e}")
        
        # Remove from tracking
        del self._deployments[deployment_id]
        return True
    
    def get_deployment_status(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """Get deployment status."""
        if deployment_id not in self._deployments:
            return None
        
        deployment = self._deployments[deployment_id].copy()
        
        # Refresh device states
        for device_name, device_info in deployment["devices"].items():
            try:
                device_handle = device_info["handle"]
                backend = self.backend_manager.get_backend_for_device(device_handle)
                if backend:
                    current_state = backend.get_device_state(device_handle)
                    device_info["status"] = current_state.value
            except Exception:
                device_info["status"] = "unknown"
        
        return deployment
    
    def list_deployments(self) -> List[Dict[str, Any]]:
        """List all deployments."""
        deployments = []
        for deployment_id, deployment in self._deployments.items():
            deployments.append({
                "id": deployment_id,
                "topology_name": deployment["topology_name"],
                "status": deployment["status"],
                "device_count": len(deployment["devices"]),
                "network_count": len(deployment["networks"]),
                "start_time": deployment["start_time"],
                "duration": deployment.get("duration", time.time() - deployment["start_time"])
            })
        return deployments