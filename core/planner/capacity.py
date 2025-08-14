"""Host resource detection and capacity planning for NetLab deployments."""

import platform
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import psutil


@dataclass
class HostResources:
    """Host system resources."""
    
    # CPU
    cpu_cores: int
    cpu_threads: int
    cpu_architecture: str
    cpu_frequency_mhz: float
    
    # Memory
    ram_total_mb: int
    ram_available_mb: int
    ram_used_mb: int
    
    # Storage
    disk_total_gb: float
    disk_free_gb: float
    disk_used_gb: float
    
    # System
    platform: str
    os_version: str
    
    # Virtualization capabilities
    virtualization_enabled: bool
    kvm_available: bool
    virtualbox_available: bool
    docker_available: bool
    
    # Network capabilities
    network_interfaces: List[str]


@dataclass
class ResourceConstraints:
    """Resource allocation constraints and limits."""
    
    max_cpu_ratio: float = 0.7  # Use at most 70% of CPU
    max_ram_ratio: float = 0.7  # Use at most 70% of available RAM
    min_disk_free_gb: float = 20.0  # Keep at least 20GB free
    
    # VM overhead factors
    vm_ram_overhead_factor: float = 0.12  # 12% RAM overhead per VM
    container_ram_overhead_factor: float = 0.03  # 3% RAM overhead per container
    
    # Disk buffer for snapshots and logs
    disk_buffer_factor: float = 1.2  # 20% extra disk space


class HostResourceScanner:
    """Scans and analyzes host system resources."""
    
    def scan_resources(self) -> HostResources:
        """Scan current host resources and capabilities."""
        
        # CPU information
        cpu_count = psutil.cpu_count(logical=False)
        cpu_threads = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()
        cpu_freq_mhz = cpu_freq.current if cpu_freq else 0.0
        
        # Memory information
        memory = psutil.virtual_memory()
        ram_total_mb = memory.total // (1024 * 1024)
        ram_available_mb = memory.available // (1024 * 1024)
        ram_used_mb = memory.used // (1024 * 1024)
        
        # Disk information (for root filesystem)
        disk_usage = psutil.disk_usage('/' if platform.system() != 'Windows' else 'C:\\')
        disk_total_gb = disk_usage.total / (1024**3)
        disk_free_gb = disk_usage.free / (1024**3)
        disk_used_gb = disk_usage.used / (1024**3)
        
        # System information
        system_platform = platform.system().lower()
        os_version = platform.version()
        
        # Architecture
        cpu_arch = platform.machine().lower()
        
        # Network interfaces
        network_interfaces = list(psutil.net_if_addrs().keys())
        
        return HostResources(
            cpu_cores=cpu_count or 1,
            cpu_threads=cpu_threads or 1,
            cpu_architecture=cpu_arch,
            cpu_frequency_mhz=cpu_freq_mhz,
            ram_total_mb=ram_total_mb,
            ram_available_mb=ram_available_mb,
            ram_used_mb=ram_used_mb,
            disk_total_gb=disk_total_gb,
            disk_free_gb=disk_free_gb,
            disk_used_gb=disk_used_gb,
            platform=system_platform,
            os_version=os_version,
            virtualization_enabled=self._check_virtualization_support(),
            kvm_available=self._check_kvm_support(),
            virtualbox_available=self._check_virtualbox_support(),
            docker_available=self._check_docker_support(),
            network_interfaces=network_interfaces,
        )
    
    def _check_virtualization_support(self) -> bool:
        """Check if hardware virtualization is available."""
        system = platform.system().lower()
        
        if system == "linux":
            # Check for KVM support
            kvm_path = Path("/dev/kvm")
            if kvm_path.exists():
                return True
            
            # Check CPU flags
            try:
                with open("/proc/cpuinfo", "r") as f:
                    cpu_info = f.read()
                    # Intel VT-x or AMD-V
                    return "vmx" in cpu_info or "svm" in cpu_info
            except (OSError, IOError):
                pass
        
        elif system == "windows":
            # Check Hyper-V capability
            try:
                result = subprocess.run(
                    ["systeminfo"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    output = result.stdout.lower()
                    return "hyper-v" in output or "virtualization enabled in firmware" in output
            except (subprocess.SubprocessError, FileNotFoundError):
                pass
        
        elif system == "darwin":  # macOS
            try:
                result = subprocess.run(
                    ["sysctl", "-n", "kern.hv_support"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                return result.returncode == 0 and "1" in result.stdout
            except (subprocess.SubprocessError, FileNotFoundError):
                pass
        
        return False
    
    def _check_kvm_support(self) -> bool:
        """Check if KVM is available (Linux only)."""
        if platform.system().lower() != "linux":
            return False
        
        # Check if KVM device exists and is accessible
        kvm_path = Path("/dev/kvm")
        return kvm_path.exists() and kvm_path.is_char_device()
    
    def _check_virtualbox_support(self) -> bool:
        """Check if VirtualBox is available."""
        # Check for VBoxManage command
        vbox_paths = [
            "VBoxManage",
            "/usr/bin/VBoxManage",
            "/Applications/VirtualBox.app/Contents/MacOS/VBoxManage",
            "C:\\Program Files\\Oracle\\VirtualBox\\VBoxManage.exe",
        ]
        
        for vbox_path in vbox_paths:
            if shutil.which(vbox_path) or Path(vbox_path).exists():
                try:
                    result = subprocess.run(
                        [vbox_path, "--version"],
                        capture_output=True,
                        timeout=10
                    )
                    return result.returncode == 0
                except (subprocess.SubprocessError, FileNotFoundError):
                    continue
        
        return False
    
    def _check_docker_support(self) -> bool:
        """Check if Docker is available and running."""
        if not shutil.which("docker"):
            return False
        
        try:
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False


@dataclass
class DeviceResourceRequirements:
    """Resource requirements for a network device."""
    
    device_ref: str
    device_type: str
    runtime: str  # "vm" or "container"
    
    # Resource requirements
    vcpu: int
    ram_mb: int
    disk_gb: int
    nics: int
    
    # Optional GPU requirements
    requires_gpu: bool = False
    gpu_memory_mb: int = 0


class ResourcePlanner:
    """Plans and validates resource allocation for network topologies."""
    
    def __init__(self, constraints: Optional[ResourceConstraints] = None):
        self.constraints = constraints or ResourceConstraints()
        self.scanner = HostResourceScanner()
    
    def validate_deployment(
        self, 
        devices: List[DeviceResourceRequirements],
        host_resources: Optional[HostResources] = None
    ) -> Tuple[bool, List[str]]:
        """Validate if a deployment fits within host constraints.
        
        Returns:
            Tuple of (is_feasible, list_of_issues)
        """
        if host_resources is None:
            host_resources = self.scanner.scan_resources()
        
        issues = []
        
        # Calculate total resource requirements
        total_vcpu = sum(device.vcpu for device in devices)
        
        vm_devices = [d for d in devices if d.runtime == "vm"]
        container_devices = [d for d in devices if d.runtime == "container"]
        
        vm_ram = sum(device.ram_mb for device in vm_devices)
        container_ram = sum(device.ram_mb for device in container_devices)
        
        # Add overhead
        vm_ram_with_overhead = vm_ram * (1 + self.constraints.vm_ram_overhead_factor)
        container_ram_with_overhead = container_ram * (1 + self.constraints.container_ram_overhead_factor)
        total_ram_mb = vm_ram_with_overhead + container_ram_with_overhead
        
        total_disk_gb = sum(device.disk_gb for device in devices) * self.constraints.disk_buffer_factor
        
        # Check CPU constraints
        max_cpu = int(host_resources.cpu_threads * self.constraints.max_cpu_ratio)
        if total_vcpu > max_cpu:
            issues.append(
                f"CPU allocation exceeds limit: need {total_vcpu} vCPUs, "
                f"max allowed: {max_cpu} (host: {host_resources.cpu_threads})"
            )
        
        # Check RAM constraints
        max_ram_mb = int(host_resources.ram_available_mb * self.constraints.max_ram_ratio)
        if total_ram_mb > max_ram_mb:
            issues.append(
                f"RAM allocation exceeds limit: need {total_ram_mb:.0f} MB, "
                f"max allowed: {max_ram_mb} MB (available: {host_resources.ram_available_mb} MB)"
            )
        
        # Check disk constraints
        required_free_gb = total_disk_gb + self.constraints.min_disk_free_gb
        if required_free_gb > host_resources.disk_free_gb:
            issues.append(
                f"Disk space insufficient: need {required_free_gb:.1f} GB, "
                f"available: {host_resources.disk_free_gb:.1f} GB"
            )
        
        # Check virtualization requirements
        has_vm_devices = len(vm_devices) > 0
        if has_vm_devices and not host_resources.virtualization_enabled:
            issues.append("VM devices require hardware virtualization support (VT-x/AMD-V)")
        
        # Check backend availability
        if has_vm_devices and not (host_resources.kvm_available or host_resources.virtualbox_available):
            issues.append("VM devices require KVM or VirtualBox support")
        
        has_container_devices = len(container_devices) > 0
        if has_container_devices and not host_resources.docker_available:
            issues.append("Container devices require Docker support")
        
        return len(issues) == 0, issues
    
    def suggest_optimizations(
        self,
        devices: List[DeviceResourceRequirements],
        host_resources: Optional[HostResources] = None
    ) -> List[str]:
        """Suggest optimizations to make deployment feasible."""
        if host_resources is None:
            host_resources = self.scanner.scan_resources()
        
        is_feasible, issues = self.validate_deployment(devices, host_resources)
        if is_feasible:
            return ["✅ Deployment is already feasible"]
        
        suggestions = []
        
        # Analyze resource usage patterns
        vm_devices = [d for d in devices if d.runtime == "vm"]
        heavy_ram_devices = [d for d in devices if d.ram_mb > 2048]
        
        if any("CPU allocation exceeds" in issue for issue in issues):
            suggestions.extend([
                "• Reduce vCPU allocation for non-critical devices",
                "• Convert some VMs to containers (lower CPU overhead)",
                f"• Consider increasing max_cpu_ratio above {self.constraints.max_cpu_ratio}",
            ])
        
        if any("RAM allocation exceeds" in issue for issue in issues):
            suggestions.extend([
                "• Use lighter base images (e.g., Alpine Linux instead of Ubuntu)",
                "• Convert heavy VMs to containers where possible",
                "• Reduce RAM allocation for development/testing scenarios",
                f"• Consider upgrading system RAM (current: {host_resources.ram_total_mb // 1024} GB)",
            ])
            
            if heavy_ram_devices:
                heavy_names = [d.device_ref for d in heavy_ram_devices]
                suggestions.append(f"• Consider reducing RAM for: {', '.join(heavy_names)}")
        
        if any("Disk space insufficient" in issue for issue in issues):
            suggestions.extend([
                "• Free up disk space or add storage",
                "• Use thin-provisioned disk images",
                "• Reduce disk allocation for non-storage devices",
                "• Clean up old VM images and snapshots",
            ])
        
        if any("virtualization support" in issue for issue in issues):
            suggestions.extend([
                "• Enable VT-x/AMD-V in BIOS settings",
                "• Install KVM support (Linux) or VirtualBox",
                "• Use container-only deployment as fallback",
            ])
        
        return suggestions
    
    def calculate_deployment_metrics(
        self,
        devices: List[DeviceResourceRequirements],
        host_resources: Optional[HostResources] = None
    ) -> Dict[str, float]:
        """Calculate deployment resource utilization metrics."""
        if host_resources is None:
            host_resources = self.scanner.scan_resources()
        
        # Calculate totals
        total_vcpu = sum(device.vcpu for device in devices)
        
        vm_devices = [d for d in devices if d.runtime == "vm"]
        container_devices = [d for d in devices if d.runtime == "container"]
        
        vm_ram = sum(device.ram_mb for device in vm_devices)
        container_ram = sum(device.ram_mb for device in container_devices)
        
        # Add overhead
        vm_ram_with_overhead = vm_ram * (1 + self.constraints.vm_ram_overhead_factor)
        container_ram_with_overhead = container_ram * (1 + self.constraints.container_ram_overhead_factor)
        total_ram_mb = vm_ram_with_overhead + container_ram_with_overhead
        
        total_disk_gb = sum(device.disk_gb for device in devices) * self.constraints.disk_buffer_factor
        
        # Calculate utilization percentages
        cpu_utilization = (total_vcpu / host_resources.cpu_threads) * 100
        ram_utilization = (total_ram_mb / host_resources.ram_available_mb) * 100
        disk_utilization = (total_disk_gb / host_resources.disk_free_gb) * 100
        
        return {
            "total_devices": len(devices),
            "vm_devices": len(vm_devices),
            "container_devices": len(container_devices),
            "total_vcpu": total_vcpu,
            "total_ram_mb": total_ram_mb,
            "total_disk_gb": total_disk_gb,
            "cpu_utilization_percent": cpu_utilization,
            "ram_utilization_percent": ram_utilization,
            "disk_utilization_percent": disk_utilization,
            "is_feasible": cpu_utilization <= (self.constraints.max_cpu_ratio * 100) and
                          ram_utilization <= (self.constraints.max_ram_ratio * 100) and
                          total_disk_gb <= (host_resources.disk_free_gb - self.constraints.min_disk_free_gb),
        }