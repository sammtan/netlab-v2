"""Backend manager for coordinating NetLab backends."""

from typing import Dict, List, Optional, Type, Union
import logging

from . import BackendType, ComputeBackend, NetworkBackend, DeviceHandle
from .vm_virtualbox import VirtualBoxBackend
from .ctr_docker import DockerBackend
from .net_bridge import BridgeNetworkBackend


logger = logging.getLogger(__name__)


class BackendManager:
    """Manages and coordinates NetLab backends."""
    
    def __init__(self):
        self.compute_backends: Dict[BackendType, ComputeBackend] = {}
        self.network_backends: Dict[BackendType, NetworkBackend] = {}
        
        # Register available backends
        self._register_backends()
        
        # Detect and initialize available backends
        self._initialize_backends()
    
    def _register_backends(self) -> None:
        """Register available backend implementations."""
        self._compute_backend_classes: Dict[BackendType, Type[ComputeBackend]] = {
            BackendType.VM_VIRTUALBOX: VirtualBoxBackend,
            BackendType.CTR_DOCKER: DockerBackend,
        }
        
        self._network_backend_classes: Dict[BackendType, Type[NetworkBackend]] = {
            BackendType.NET_BRIDGE: BridgeNetworkBackend,
        }
    
    def _initialize_backends(self) -> None:
        """Initialize available backends."""
        # Initialize compute backends
        for backend_type, backend_class in self._compute_backend_classes.items():
            try:
                backend = backend_class()
                if backend.is_available():
                    self.compute_backends[backend_type] = backend
                    logger.info(f"Initialized compute backend: {backend_type.value}")
                else:
                    logger.debug(f"Compute backend not available: {backend_type.value}")
            except Exception as e:
                logger.warning(f"Failed to initialize {backend_type.value}: {e}")
        
        # Initialize network backends
        for backend_type, backend_class in self._network_backend_classes.items():
            try:
                backend = backend_class()
                if backend.is_available():
                    self.network_backends[backend_type] = backend
                    logger.info(f"Initialized network backend: {backend_type.value}")
                else:
                    logger.debug(f"Network backend not available: {backend_type.value}")
            except Exception as e:
                logger.warning(f"Failed to initialize {backend_type.value}: {e}")
    
    def get_available_compute_backends(self) -> List[BackendType]:
        """Get list of available compute backends."""
        return list(self.compute_backends.keys())
    
    def get_available_network_backends(self) -> List[BackendType]:
        """Get list of available network backends."""
        return list(self.network_backends.keys())
    
    def get_compute_backend(self, backend_type: BackendType) -> Optional[ComputeBackend]:
        """Get compute backend by type."""
        return self.compute_backends.get(backend_type)
    
    def get_network_backend(self, backend_type: BackendType) -> Optional[NetworkBackend]:
        """Get network backend by type."""
        return self.network_backends.get(backend_type)
    
    def get_preferred_compute_backend(self, device_type: str = None) -> Optional[ComputeBackend]:
        """Get preferred compute backend based on device type and availability."""
        # Define preference order based on device type
        if device_type and "container" in device_type.lower():
            # Prefer containers for lightweight devices
            preferences = [BackendType.CTR_DOCKER, BackendType.VM_VIRTUALBOX]
        else:
            # Prefer VMs for full OS devices
            preferences = [BackendType.VM_VIRTUALBOX, BackendType.CTR_DOCKER]
        
        for backend_type in preferences:
            if backend_type in self.compute_backends:
                return self.compute_backends[backend_type]
        
        return None
    
    def get_preferred_network_backend(self) -> Optional[NetworkBackend]:
        """Get preferred network backend."""
        # For now, we only have bridge networking
        if BackendType.NET_BRIDGE in self.network_backends:
            return self.network_backends[BackendType.NET_BRIDGE]
        
        return None
    
    def list_all_devices(self) -> List[DeviceHandle]:
        """List devices from all compute backends."""
        devices = []
        
        for backend in self.compute_backends.values():
            try:
                devices.extend(backend.list_devices())
            except Exception as e:
                logger.warning(f"Failed to list devices from {backend.get_backend_type().value}: {e}")
        
        return devices
    
    def find_device(self, device_id: str) -> Optional[DeviceHandle]:
        """Find device by ID across all backends."""
        for backend in self.compute_backends.values():
            try:
                devices = backend.list_devices()
                for device in devices:
                    if device.id == device_id:
                        return device
            except Exception as e:
                logger.warning(f"Error searching devices in {backend.get_backend_type().value}: {e}")
        
        return None
    
    def get_backend_for_device(self, device_handle: DeviceHandle) -> Optional[ComputeBackend]:
        """Get the backend that manages a specific device."""
        return self.compute_backends.get(device_handle.backend_type)
    
    def get_system_capabilities(self) -> Dict[str, any]:
        """Get comprehensive system capabilities."""
        capabilities = {
            "compute_backends": {},
            "network_backends": {},
            "available_features": []
        }
        
        # Compute backend capabilities
        for backend_type, backend in self.compute_backends.items():
            capabilities["compute_backends"][backend_type.value] = {
                "available": True,
                "type": backend_type.value
            }
        
        # Network backend capabilities  
        for backend_type, backend in self.network_backends.items():
            capabilities["network_backends"][backend_type.value] = {
                "available": True,
                "type": backend_type.value
            }
        
        # Available features
        if BackendType.VM_VIRTUALBOX in self.compute_backends:
            capabilities["available_features"].append("vm_deployment")
            capabilities["available_features"].append("full_os_support")
        
        if BackendType.CTR_DOCKER in self.compute_backends:
            capabilities["available_features"].append("container_deployment")
            capabilities["available_features"].append("lightweight_devices")
        
        if BackendType.NET_BRIDGE in self.network_backends:
            capabilities["available_features"].append("bridge_networking")
            capabilities["available_features"].append("network_isolation")
        
        return capabilities
    
    def validate_deployment_requirements(self, topology_requirements: Dict) -> Dict[str, any]:
        """Validate if system can support deployment requirements."""
        validation = {
            "can_deploy": True,
            "missing_backends": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Check compute requirements
        vm_required = topology_requirements.get("requires_vms", False)
        container_required = topology_requirements.get("requires_containers", False)
        
        if vm_required and BackendType.VM_VIRTUALBOX not in self.compute_backends:
            validation["can_deploy"] = False
            validation["missing_backends"].append("vm_virtualbox")
        
        if container_required and BackendType.CTR_DOCKER not in self.compute_backends:
            validation["can_deploy"] = False
            validation["missing_backends"].append("ctr_docker")
        
        # Check network requirements
        if not self.network_backends:
            validation["can_deploy"] = False
            validation["missing_backends"].append("network_backend")
        
        # Add recommendations
        if not self.compute_backends:
            validation["recommendations"].append("Install VirtualBox or Docker for device deployment")
        elif len(self.compute_backends) == 1:
            validation["recommendations"].append("Consider installing additional backends for flexibility")
        
        return validation