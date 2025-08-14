"""NetLab Backend Infrastructure.

This module provides the backend abstraction layer for NetLab's virtualization
and networking capabilities. Backends implement device provisioning, networking,
and lifecycle management across different platforms.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import uuid


class BackendType(Enum):
    """Supported backend types."""
    VM_LIBVIRT = "vm_libvirt"
    VM_VIRTUALBOX = "vm_virtualbox"
    CTR_DOCKER = "ctr_docker"
    NET_OVS = "net_ovs"
    NET_BRIDGE = "net_bridge"


class DeviceState(Enum):
    """Device lifecycle states."""
    PENDING = "pending"
    CREATING = "creating"
    RUNNING = "running"
    STOPPED = "stopped"
    PAUSED = "paused"
    ERROR = "error"
    DESTROYED = "destroyed"


@dataclass
class NetworkSpec:
    """Network interface specification."""
    name: str
    network_id: str
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    bridge_name: Optional[str] = None
    vlan_id: Optional[int] = None


@dataclass
class VmSpec:
    """Virtual machine specification."""
    name: str
    image_path: Path
    cpu_cores: int
    memory_mb: int
    disk_size_gb: int
    networks: List[NetworkSpec]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class CtrSpec:
    """Container specification."""
    name: str
    image: str
    command: Optional[List[str]] = None
    environment: Dict[str, str] = None
    volumes: Dict[Path, Path] = None
    networks: List[NetworkSpec] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.environment is None:
            self.environment = {}
        if self.volumes is None:
            self.volumes = {}
        if self.networks is None:
            self.networks = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class DeviceHandle:
    """Handle for managing device lifecycle."""
    id: str
    name: str
    backend_type: BackendType
    state: DeviceState
    spec: Union[VmSpec, CtrSpec]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ComputeBackend(ABC):
    """Abstract base class for compute backends."""
    
    @abstractmethod
    def get_backend_type(self) -> BackendType:
        """Return the backend type."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if backend is available on this system."""
        pass
    
    @abstractmethod
    def create_vm(self, spec: VmSpec) -> DeviceHandle:
        """Create a virtual machine."""
        pass
    
    @abstractmethod
    def create_ctr(self, spec: CtrSpec) -> DeviceHandle:
        """Create a container."""
        pass
    
    @abstractmethod
    def start_device(self, handle: DeviceHandle) -> None:
        """Start a device."""
        pass
    
    @abstractmethod
    def stop_device(self, handle: DeviceHandle) -> None:
        """Stop a device."""
        pass
    
    @abstractmethod
    def get_device_state(self, handle: DeviceHandle) -> DeviceState:
        """Get current device state."""
        pass
    
    @abstractmethod
    def destroy_device(self, handle: DeviceHandle) -> None:
        """Destroy a device."""
        pass
    
    @abstractmethod
    def list_devices(self) -> List[DeviceHandle]:
        """List all managed devices."""
        pass


class NetworkBackend(ABC):
    """Abstract base class for network backends."""
    
    @abstractmethod
    def get_backend_type(self) -> BackendType:
        """Return the backend type."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if backend is available on this system."""
        pass
    
    @abstractmethod
    def create_network(self, name: str, subnet: str) -> str:
        """Create a network and return network ID."""
        pass
    
    @abstractmethod
    def delete_network(self, network_id: str) -> None:
        """Delete a network."""
        pass
    
    @abstractmethod
    def attach_device(self, network_id: str, device_handle: DeviceHandle, 
                     interface_spec: NetworkSpec) -> None:
        """Attach device to network."""
        pass
    
    @abstractmethod
    def detach_device(self, network_id: str, device_handle: DeviceHandle,
                     interface_spec: NetworkSpec) -> None:
        """Detach device from network."""
        pass
    
    @abstractmethod
    def list_networks(self) -> List[Dict[str, Any]]:
        """List all managed networks."""
        pass


def generate_device_id() -> str:
    """Generate unique device ID."""
    return f"netlab-{uuid.uuid4().hex[:8]}"


def generate_network_id() -> str:
    """Generate unique network ID."""
    return f"netlab-net-{uuid.uuid4().hex[:8]}"