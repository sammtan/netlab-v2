"""Docker container backend for NetLab device management."""

import json
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import (
    BackendType, ComputeBackend, DeviceHandle, DeviceState, VmSpec, CtrSpec,
    generate_device_id
)


class DockerBackend(ComputeBackend):
    """Docker container backend."""
    
    def __init__(self):
        self.docker_cmd = self._find_docker()
        self._devices: Dict[str, DeviceHandle] = {}
    
    def _find_docker(self) -> Optional[str]:
        """Find Docker executable."""
        import shutil
        return shutil.which("docker")
    
    def get_backend_type(self) -> BackendType:
        """Return backend type."""
        return BackendType.CTR_DOCKER
    
    def is_available(self) -> bool:
        """Check if Docker is available."""
        if not self.docker_cmd:
            return False
        try:
            result = subprocess.run(
                [self.docker_cmd, "--version"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0:
                return False
            
            # Test Docker daemon connectivity
            result = subprocess.run(
                [self.docker_cmd, "info"],
                capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _run_docker_command(self, args: List[str]) -> subprocess.CompletedProcess:
        """Run Docker command."""
        if not self.docker_cmd:
            raise RuntimeError("Docker not available")
        
        cmd = [self.docker_cmd] + args
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Docker command failed: {' '.join(cmd)}\\n"
                             f"Error: {result.stderr}")
        
        return result
    
    def create_vm(self, spec: VmSpec) -> DeviceHandle:
        """Docker doesn't support VMs directly."""
        raise NotImplementedError("Docker backend doesn't support VMs. Use create_ctr instead.")
    
    def create_ctr(self, spec: CtrSpec) -> DeviceHandle:
        """Create Docker container."""
        container_name = f"netlab-{spec.name}-{generate_device_id()[-8:]}"
        
        # Build docker run command
        cmd = ["run", "-d", "--name", container_name]
        
        # Add resource limits (if specified in metadata)
        if spec.metadata and "memory_limit" in spec.metadata:
            cmd.extend(["--memory", spec.metadata["memory_limit"]])
        
        if spec.metadata and "cpu_limit" in spec.metadata:
            cmd.extend(["--cpus", spec.metadata["cpu_limit"]])
        
        # Add environment variables
        for key, value in spec.environment.items():
            cmd.extend(["-e", f"{key}={value}"])
        
        # Add volume mounts
        for host_path, container_path in spec.volumes.items():
            cmd.extend(["-v", f"{host_path}:{container_path}"])
        
        # Add network configurations
        for net_spec in spec.networks:
            if net_spec.network_id != "default":
                cmd.extend(["--network", net_spec.network_id])
        
        # Add capabilities for network devices
        if spec.metadata and spec.metadata.get("privileged", False):
            cmd.append("--privileged")
        
        if spec.metadata and spec.metadata.get("network_admin", False):
            cmd.extend(["--cap-add", "NET_ADMIN"])
            cmd.extend(["--cap-add", "SYS_ADMIN"])
        
        # Add image and command
        cmd.append(spec.image)
        if spec.command:
            cmd.extend(spec.command)
        
        # Create container
        result = self._run_docker_command(cmd)
        container_id = result.stdout.strip()
        
        # Create device handle
        handle = DeviceHandle(
            id=container_id,
            name=spec.name,
            backend_type=BackendType.CTR_DOCKER,
            state=DeviceState.RUNNING,  # Docker containers start by default
            spec=spec,
            metadata={
                "container_name": container_name,
                "container_id": container_id
            }
        )
        
        self._devices[container_id] = handle
        return handle
    
    def start_device(self, handle: DeviceHandle) -> None:
        """Start container."""
        container_id = handle.id
        self._run_docker_command(["start", container_id])
        
        # Wait for container to start
        for _ in range(10):  # 10 second timeout
            state = self.get_device_state(handle)
            if state == DeviceState.RUNNING:
                break
            time.sleep(1)
        
        handle.state = self.get_device_state(handle)
    
    def stop_device(self, handle: DeviceHandle) -> None:
        """Stop container."""
        container_id = handle.id
        
        try:
            # Try graceful stop first (10 second timeout)
            self._run_docker_command(["stop", "-t", "10", container_id])
        except RuntimeError:
            # Container might already be stopped
            pass
        
        handle.state = self.get_device_state(handle)
    
    def get_device_state(self, handle: DeviceHandle) -> DeviceState:
        """Get container state."""
        container_id = handle.id
        
        try:
            result = self._run_docker_command([
                "inspect", "--format", "{{.State.Status}}", container_id
            ])
            
            docker_state = result.stdout.strip()
            return self._map_docker_state(docker_state)
            
        except RuntimeError:
            return DeviceState.ERROR
    
    def _map_docker_state(self, docker_state: str) -> DeviceState:
        """Map Docker state to NetLab state."""
        state_mapping = {
            "created": DeviceState.STOPPED,
            "running": DeviceState.RUNNING,
            "paused": DeviceState.PAUSED,
            "restarting": DeviceState.CREATING,
            "removing": DeviceState.CREATING,
            "exited": DeviceState.STOPPED,
            "dead": DeviceState.ERROR,
        }
        return state_mapping.get(docker_state, DeviceState.ERROR)
    
    def destroy_device(self, handle: DeviceHandle) -> None:
        """Destroy container."""
        container_id = handle.id
        
        # Stop container if running
        try:
            self.stop_device(handle)
        except:
            pass
        
        # Remove container
        try:
            self._run_docker_command(["rm", "-f", container_id])
        except RuntimeError:
            # Container might already be removed
            pass
        
        # Remove from tracking
        if container_id in self._devices:
            del self._devices[container_id]
        
        handle.state = DeviceState.DESTROYED
    
    def list_devices(self) -> List[DeviceHandle]:
        """List managed devices."""
        # Refresh states from Docker
        for handle in self._devices.values():
            handle.state = self.get_device_state(handle)
        
        return list(self._devices.values())
    
    def create_network(self, name: str, subnet: Optional[str] = None) -> str:
        """Create Docker network."""
        cmd = ["network", "create"]
        
        if subnet:
            cmd.extend(["--subnet", subnet])
        
        cmd.append(name)
        
        result = self._run_docker_command(cmd)
        return result.stdout.strip()
    
    def remove_network(self, network_name: str) -> None:
        """Remove Docker network."""
        try:
            self._run_docker_command(["network", "rm", network_name])
        except RuntimeError:
            # Network might not exist
            pass
    
    def list_networks(self) -> List[Dict[str, Any]]:
        """List Docker networks."""
        try:
            result = self._run_docker_command([
                "network", "ls", "--format", "json"
            ])
            
            networks = []
            for line in result.stdout.strip().split('\\n'):
                if line:
                    networks.append(json.loads(line))
            
            return networks
            
        except (RuntimeError, json.JSONDecodeError):
            return []
    
    def connect_container_to_network(self, container_id: str, network_name: str,
                                   ip_address: Optional[str] = None) -> None:
        """Connect container to network."""
        cmd = ["network", "connect"]
        
        if ip_address:
            cmd.extend(["--ip", ip_address])
        
        cmd.extend([network_name, container_id])
        
        self._run_docker_command(cmd)
    
    def disconnect_container_from_network(self, container_id: str, 
                                        network_name: str) -> None:
        """Disconnect container from network."""
        try:
            self._run_docker_command([
                "network", "disconnect", network_name, container_id
            ])
        except RuntimeError:
            # Container might not be connected to network
            pass