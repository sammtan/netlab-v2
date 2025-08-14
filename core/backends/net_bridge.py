"""Bridge networking backend for NetLab network management."""

import subprocess
import platform
from typing import Any, Dict, List, Optional

from . import BackendType, NetworkBackend, DeviceHandle, NetworkSpec, generate_network_id


class BridgeNetworkBackend(NetworkBackend):
    """Bridge-based networking backend."""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self._networks: Dict[str, Dict[str, Any]] = {}
    
    def get_backend_type(self) -> BackendType:
        """Return backend type."""
        return BackendType.NET_BRIDGE
    
    def is_available(self) -> bool:
        """Check if bridge networking is available."""
        try:
            if self.platform == "linux":
                # Check for bridge utilities
                result = subprocess.run(["brctl", "--version"], 
                             capture_output=True, timeout=5)
                return result.returncode == 0
            elif self.platform == "windows":
                # For Windows, we'll use basic networking (no Hyper-V requirement)
                # Just check if we can run basic networking commands
                result = subprocess.run(
                    ["ping", "-n", "1", "127.0.0.1"],
                    capture_output=True, text=True, timeout=5
                )
                return result.returncode == 0
            elif self.platform == "darwin":
                # macOS - limited bridge support, mainly through VMs
                return True
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return False
    
    def create_network(self, name: str, subnet: str) -> str:
        """Create a bridge network."""
        network_id = f"{name}-{generate_network_id()[-8:]}"
        
        try:
            if self.platform == "linux":
                self._create_linux_bridge(network_id, subnet)
            elif self.platform == "windows":
                self._create_windows_switch(network_id)
            elif self.platform == "darwin":
                self._create_macos_bridge(network_id)
            
            # Store network metadata
            self._networks[network_id] = {
                "name": name,
                "network_id": network_id,
                "subnet": subnet,
                "platform": self.platform,
                "devices": []
            }
            
            return network_id
            
        except Exception as e:
            raise RuntimeError(f"Failed to create network {name}: {e}")
    
    def _create_linux_bridge(self, network_id: str, subnet: str) -> None:
        """Create Linux bridge."""
        bridge_name = f"br-{network_id[:12]}"
        
        # Create bridge
        subprocess.run(["brctl", "addbr", bridge_name], check=True)
        
        # Configure bridge IP if subnet provided
        if subnet:
            # Extract first IP from subnet for bridge
            import ipaddress
            network = ipaddress.IPv4Network(subnet, strict=False)
            bridge_ip = str(list(network.hosts())[0])
            
            subprocess.run(["ip", "addr", "add", f"{bridge_ip}/{network.prefixlen}", 
                          "dev", bridge_name], check=True)
        
        # Bring bridge up
        subprocess.run(["ip", "link", "set", bridge_name, "up"], check=True)
    
    def _create_windows_switch(self, network_id: str) -> None:
        """Create Windows Hyper-V virtual switch."""
        switch_name = f"netlab-{network_id[:12]}"
        
        cmd = [
            "powershell", "-Command",
            f"New-VMSwitch -Name '{switch_name}' -SwitchType Internal"
        ]
        
        subprocess.run(cmd, check=True)
    
    def _create_macos_bridge(self, network_id: str) -> None:
        """Create macOS bridge (limited functionality)."""
        # macOS bridge creation is complex and typically handled by VM software
        # For now, we'll just track the network logically
        pass
    
    def delete_network(self, network_id: str) -> None:
        """Delete a bridge network."""
        if network_id not in self._networks:
            return
        
        network_info = self._networks[network_id]
        
        try:
            if self.platform == "linux":
                self._delete_linux_bridge(network_id)
            elif self.platform == "windows":
                self._delete_windows_switch(network_id)
            elif self.platform == "darwin":
                self._delete_macos_bridge(network_id)
                
        except Exception:
            # Continue cleanup even if deletion fails
            pass
        
        # Remove from tracking
        del self._networks[network_id]
    
    def _delete_linux_bridge(self, network_id: str) -> None:
        """Delete Linux bridge."""
        bridge_name = f"br-{network_id[:12]}"
        
        try:
            # Bring bridge down
            subprocess.run(["ip", "link", "set", bridge_name, "down"], 
                          check=False)
            
            # Delete bridge
            subprocess.run(["brctl", "delbr", bridge_name], check=False)
            
        except subprocess.CalledProcessError:
            # Bridge might not exist
            pass
    
    def _delete_windows_switch(self, network_id: str) -> None:
        """Delete Windows Hyper-V virtual switch."""
        switch_name = f"netlab-{network_id[:12]}"
        
        cmd = [
            "powershell", "-Command",
            f"Remove-VMSwitch -Name '{switch_name}' -Force -ErrorAction SilentlyContinue"
        ]
        
        subprocess.run(cmd, check=False)
    
    def _delete_macos_bridge(self, network_id: str) -> None:
        """Delete macOS bridge."""
        # Logical cleanup only
        pass
    
    def attach_device(self, network_id: str, device_handle: DeviceHandle,
                     interface_spec: NetworkSpec) -> None:
        """Attach device to network."""
        if network_id not in self._networks:
            raise ValueError(f"Network {network_id} not found")
        
        network_info = self._networks[network_id]
        
        # Add device to network's device list
        device_info = {
            "device_id": device_handle.id,
            "device_name": device_handle.name,
            "interface_name": interface_spec.name,
            "ip_address": interface_spec.ip_address,
            "mac_address": interface_spec.mac_address
        }
        
        network_info["devices"].append(device_info)
        
        # Platform-specific attachment logic would go here
        # This is typically handled by the compute backend (VirtualBox, Docker, etc.)
        # The network backend mainly tracks connections
    
    def detach_device(self, network_id: str, device_handle: DeviceHandle,
                     interface_spec: NetworkSpec) -> None:
        """Detach device from network."""
        if network_id not in self._networks:
            return
        
        network_info = self._networks[network_id]
        
        # Remove device from network's device list
        network_info["devices"] = [
            device for device in network_info["devices"]
            if device["device_id"] != device_handle.id or 
               device["interface_name"] != interface_spec.name
        ]
    
    def list_networks(self) -> List[Dict[str, Any]]:
        """List all managed networks."""
        networks = []
        
        for network_id, network_info in self._networks.items():
            networks.append({
                "id": network_id,
                "name": network_info["name"],
                "subnet": network_info["subnet"],
                "platform": network_info["platform"],
                "device_count": len(network_info["devices"]),
                "devices": network_info["devices"]
            })
        
        return networks
    
    def get_bridge_name(self, network_id: str) -> Optional[str]:
        """Get platform-specific bridge name for network."""
        if network_id not in self._networks:
            return None
        
        if self.platform == "linux":
            return f"br-{network_id[:12]}"
        elif self.platform == "windows":
            return f"netlab-{network_id[:12]}"
        else:
            return network_id