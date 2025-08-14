"""Topology loading and parsing for NetLab."""

import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.backends import NetworkSpec, VmSpec, CtrSpec


@dataclass
class DeviceConfig:
    """Device configuration from topology."""
    name: str
    device_type: str
    backend_type: str = "vm"  # vm or container
    cpu_cores: int = 1
    memory_mb: int = 512
    disk_size_gb: int = 20
    image: Optional[str] = None
    networks: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass  
class NetworkConfig:
    """Network configuration from topology."""
    name: str
    subnet: str
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NetworkTopology:
    """Complete network topology specification."""
    name: str
    description: Optional[str]
    devices: List[DeviceConfig]
    networks: List[NetworkConfig]
    metadata: Dict[str, Any] = field(default_factory=dict)


class TopologyLoader:
    """Loads and parses topology files."""
    
    @staticmethod
    def load_from_file(topology_file: Path) -> NetworkTopology:
        """Load topology from YAML file."""
        if not topology_file.exists():
            raise FileNotFoundError(f"Topology file not found: {topology_file}")
        
        with open(topology_file, 'r') as f:
            data = yaml.safe_load(f)
        
        return TopologyLoader.parse_topology(data, topology_file.stem)
    
    @staticmethod
    def parse_topology(data: Dict[str, Any], name: str) -> NetworkTopology:
        """Parse topology data structure."""
        # Parse networks
        networks = []
        for net_name, net_config in data.get("networks", {}).items():
            network = NetworkConfig(
                name=net_name,
                subnet=net_config.get("subnet", "192.168.1.0/24"),
                description=net_config.get("description"),
                metadata=net_config.get("metadata", {})
            )
            networks.append(network)
        
        # Parse devices
        devices = []
        for device_name, device_config in data.get("devices", {}).items():
            # Parse device networks
            device_networks = []
            for net_config in device_config.get("networks", []):
                device_networks.append({
                    "name": net_config.get("name", "eth0"),
                    "network": net_config.get("network", "default"),
                    "ip_address": net_config.get("ip"),
                    "mac_address": net_config.get("mac")
                })
            
            device = DeviceConfig(
                name=device_name,
                device_type=device_config.get("device_type", "ubuntu-server"),
                backend_type=device_config.get("backend_type", "vm"),
                cpu_cores=device_config.get("cpu_cores", 1),
                memory_mb=device_config.get("memory_mb", 512),
                disk_size_gb=device_config.get("disk_size_gb", 20),
                image=device_config.get("image"),
                networks=device_networks,
                metadata=device_config.get("metadata", {})
            )
            devices.append(device)
        
        return NetworkTopology(
            name=name,
            description=data.get("description"),
            devices=devices,
            networks=networks,
            metadata=data.get("metadata", {})
        )
    
    @staticmethod
    def create_vm_spec(device: DeviceConfig, image_path: Path = None) -> VmSpec:
        """Create VmSpec from DeviceConfig."""
        # Convert device networks to NetworkSpec objects
        network_specs = []
        for net_config in device.networks:
            network_spec = NetworkSpec(
                name=net_config.get("name", "eth0"),
                network_id=net_config.get("network", "default"),
                ip_address=net_config.get("ip_address"),
                mac_address=net_config.get("mac_address")
            )
            network_specs.append(network_spec)
        
        # Default image path if not provided
        if not image_path and device.image:
            image_path = Path(device.image)
        elif not image_path:
            # Use default image based on device type
            image_path = Path(f"/tmp/netlab-images/{device.device_type}.iso")
        
        return VmSpec(
            name=device.name,
            image_path=image_path,
            cpu_cores=device.cpu_cores,
            memory_mb=device.memory_mb,
            disk_size_gb=device.disk_size_gb,
            networks=network_specs,
            metadata=device.metadata
        )
    
    @staticmethod
    def create_container_spec(device: DeviceConfig) -> CtrSpec:
        """Create CtrSpec from DeviceConfig."""
        # Convert device networks to NetworkSpec objects
        network_specs = []
        for net_config in device.networks:
            network_spec = NetworkSpec(
                name=net_config.get("name", "eth0"),
                network_id=net_config.get("network", "default"),
                ip_address=net_config.get("ip_address"),
                mac_address=net_config.get("mac_address")
            )
            network_specs.append(network_spec)
        
        # Default image based on device type
        image = device.image or TopologyLoader._get_default_container_image(device.device_type)
        
        return CtrSpec(
            name=device.name,
            image=image,
            networks=network_specs,
            metadata={
                **device.metadata,
                "memory_limit": f"{device.memory_mb}m",
                "cpu_limit": str(device.cpu_cores)
            }
        )
    
    @staticmethod
    def _get_default_container_image(device_type: str) -> str:
        """Get default container image for device type."""
        image_mapping = {
            "ubuntu-server": "ubuntu:22.04",
            "ubuntu-desktop": "ubuntu:22.04",
            "debian": "debian:12",
            "alpine": "alpine:latest",
            "nginx": "nginx:alpine",
            "apache": "httpd:alpine",
            "mysql": "mysql:8.0",
            "postgres": "postgres:15",
            "redis": "redis:alpine",
            "mongodb": "mongo:7.0",
        }
        
        return image_mapping.get(device_type, "ubuntu:22.04")