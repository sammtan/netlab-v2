"""VirtualBox backend for NetLab VM management."""

import json
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import (
    BackendType, ComputeBackend, DeviceHandle, DeviceState, VmSpec, CtrSpec,
    generate_device_id
)


class VirtualBoxBackend(ComputeBackend):
    """VirtualBox virtualization backend."""
    
    def __init__(self):
        self.vboxmanage = self._find_vboxmanage()
        self._devices: Dict[str, DeviceHandle] = {}
    
    def _find_vboxmanage(self) -> Optional[str]:
        """Find VBoxManage executable."""
        import shutil
        vboxmanage = shutil.which("VBoxManage")
        if not vboxmanage:
            # Try common installation paths
            paths = [
                r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe",
                "/usr/bin/VBoxManage",
                "/usr/local/bin/VBoxManage",
            ]
            for path in paths:
                if Path(path).exists():
                    return path
        return vboxmanage
    
    def get_backend_type(self) -> BackendType:
        """Return backend type."""
        return BackendType.VM_VIRTUALBOX
    
    def is_available(self) -> bool:
        """Check if VirtualBox is available."""
        if not self.vboxmanage:
            return False
        try:
            result = subprocess.run(
                [self.vboxmanage, "--version"],
                capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _run_vbox_command(self, args: List[str]) -> subprocess.CompletedProcess:
        """Run VBoxManage command."""
        if not self.vboxmanage:
            raise RuntimeError("VBoxManage not available")
        
        cmd = [self.vboxmanage] + args
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"VBoxManage command failed: {' '.join(cmd)}\\n"
                             f"Error: {result.stderr}")
        
        return result
    
    def create_vm(self, spec: VmSpec) -> DeviceHandle:
        """Create VirtualBox VM."""
        vm_name = f"netlab-{spec.name}-{generate_device_id()[-8:]}"
        
        # Create VM
        self._run_vbox_command([
            "createvm", "--name", vm_name, "--register",
            "--ostype", self._detect_os_type(spec.image_path)
        ])
        
        try:
            # Configure VM
            self._run_vbox_command([
                "modifyvm", vm_name,
                "--memory", str(spec.memory_mb),
                "--cpus", str(spec.cpu_cores),
                "--acpi", "on",
                "--ioapic", "on",
                "--rtcuseutc", "on",
                "--boot1", "dvd",
                "--boot2", "disk",
                "--boot3", "none",
                "--boot4", "none"
            ])
            
            # Create storage controller
            self._run_vbox_command([
                "storagectl", vm_name,
                "--name", "SATA",
                "--add", "sata",
                "--controller", "IntelAHCI"
            ])
            
            # Create and attach disk
            vm_folder = self._get_vm_folder(vm_name)
            disk_path = vm_folder / f"{vm_name}.vdi"
            
            self._run_vbox_command([
                "createhd", "--filename", str(disk_path),
                "--size", str(spec.disk_size_gb * 1024)
            ])
            
            self._run_vbox_command([
                "storageattach", vm_name,
                "--storagectl", "SATA",
                "--port", "0",
                "--device", "0",
                "--type", "hdd",
                "--medium", str(disk_path)
            ])
            
            # Attach ISO if provided
            if spec.image_path.suffix.lower() == '.iso':
                self._run_vbox_command([
                    "storageattach", vm_name,
                    "--storagectl", "SATA",
                    "--port", "1",
                    "--device", "0",
                    "--type", "dvddrive",
                    "--medium", str(spec.image_path)
                ])
            
            # Configure network interfaces
            for i, net_spec in enumerate(spec.networks):
                self._configure_network_interface(vm_name, i + 1, net_spec)
            
            # Create device handle
            handle = DeviceHandle(
                id=vm_name,
                name=spec.name,
                backend_type=BackendType.VM_VIRTUALBOX,
                state=DeviceState.STOPPED,
                spec=spec,
                metadata={"vm_name": vm_name, "vm_folder": str(vm_folder)}
            )
            
            self._devices[vm_name] = handle
            return handle
            
        except Exception:
            # Cleanup on error
            try:
                self._run_vbox_command(["unregistervm", vm_name, "--delete"])
            except:
                pass
            raise
    
    def create_ctr(self, spec: CtrSpec) -> DeviceHandle:
        """VirtualBox doesn't support containers."""
        raise NotImplementedError("VirtualBox backend doesn't support containers")
    
    def _detect_os_type(self, image_path: Path) -> str:
        """Detect OS type from image path."""
        name_lower = image_path.name.lower()
        
        if "ubuntu" in name_lower:
            return "Ubuntu_64"
        elif "debian" in name_lower:
            return "Debian_64" 
        elif "centos" in name_lower or "rhel" in name_lower:
            return "RedHat_64"
        elif "windows" in name_lower:
            if "server" in name_lower:
                return "Windows2019_64"
            else:
                return "Windows10_64"
        elif "vyos" in name_lower:
            return "Debian_64"
        elif "pfsense" in name_lower:
            return "FreeBSD_64"
        else:
            return "Other_64"
    
    def _get_vm_folder(self, vm_name: str) -> Path:
        """Get VM storage folder."""
        result = self._run_vbox_command(["list", "systemproperties"])
        
        for line in result.stdout.splitlines():
            if "Default machine folder:" in line:
                folder = line.split(":", 1)[1].strip()
                return Path(folder) / vm_name
        
        # Fallback
        return Path.home() / "VirtualBox VMs" / vm_name
    
    def _configure_network_interface(self, vm_name: str, nic_num: int, 
                                   net_spec) -> None:
        """Configure network interface."""
        args = ["modifyvm", vm_name, f"--nic{nic_num}", "bridged"]
        
        if net_spec.bridge_name:
            args.extend([f"--bridgeadapter{nic_num}", net_spec.bridge_name])
        
        if net_spec.mac_address:
            # Remove colons and make uppercase
            mac = net_spec.mac_address.replace(":", "").upper()
            args.extend([f"--macaddress{nic_num}", mac])
        
        self._run_vbox_command(args)
    
    def start_device(self, handle: DeviceHandle) -> None:
        """Start VM."""
        vm_name = handle.id
        self._run_vbox_command(["startvm", vm_name, "--type", "headless"])
        
        # Wait for VM to start
        for _ in range(30):  # 30 second timeout
            state = self.get_device_state(handle)
            if state == DeviceState.RUNNING:
                break
            time.sleep(1)
        
        handle.state = self.get_device_state(handle)
    
    def stop_device(self, handle: DeviceHandle) -> None:
        """Stop VM."""
        vm_name = handle.id
        
        try:
            # Try graceful shutdown first
            self._run_vbox_command(["controlvm", vm_name, "acpipowerbutton"])
            
            # Wait for graceful shutdown
            for _ in range(60):  # 60 second timeout
                state = self.get_device_state(handle)
                if state == DeviceState.STOPPED:
                    break
                time.sleep(1)
            else:
                # Force power off if graceful shutdown failed
                self._run_vbox_command(["controlvm", vm_name, "poweroff"])
                
        except RuntimeError:
            # VM might already be stopped
            pass
        
        handle.state = self.get_device_state(handle)
    
    def get_device_state(self, handle: DeviceHandle) -> DeviceState:
        """Get VM state."""
        vm_name = handle.id
        
        try:
            result = self._run_vbox_command(["showvminfo", vm_name, "--machinereadable"])
            
            for line in result.stdout.splitlines():
                if line.startswith("VMState="):
                    vbox_state = line.split("=", 1)[1].strip('"')
                    return self._map_vbox_state(vbox_state)
                    
        except RuntimeError:
            return DeviceState.ERROR
        
        return DeviceState.ERROR
    
    def _map_vbox_state(self, vbox_state: str) -> DeviceState:
        """Map VirtualBox state to NetLab state."""
        state_mapping = {
            "poweroff": DeviceState.STOPPED,
            "saved": DeviceState.STOPPED,
            "running": DeviceState.RUNNING,
            "paused": DeviceState.PAUSED,
            "starting": DeviceState.CREATING,
            "stopping": DeviceState.CREATING,
        }
        return state_mapping.get(vbox_state, DeviceState.ERROR)
    
    def destroy_device(self, handle: DeviceHandle) -> None:
        """Destroy VM."""
        vm_name = handle.id
        
        # Stop VM if running
        try:
            self.stop_device(handle)
        except:
            pass
        
        # Delete VM
        try:
            self._run_vbox_command(["unregistervm", vm_name, "--delete"])
        except RuntimeError:
            # Try without --delete if that fails
            try:
                self._run_vbox_command(["unregistervm", vm_name])
            except:
                pass
        
        # Remove from tracking
        if vm_name in self._devices:
            del self._devices[vm_name]
        
        handle.state = DeviceState.DESTROYED
    
    def list_devices(self) -> List[DeviceHandle]:
        """List managed devices."""
        return list(self._devices.values())