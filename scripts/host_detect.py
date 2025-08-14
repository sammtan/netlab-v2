"""Host capability detection for NetLab."""

import json
import platform
import sys
from pathlib import Path
from typing import Any, Dict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.planner.capacity import HostResourceScanner


def detect_host_capabilities() -> Dict[str, Any]:
    """Detect and return host capabilities as a dictionary."""
    scanner = HostResourceScanner()
    resources = scanner.scan_resources()
    
    return {
        "system": {
            "platform": resources.platform,
            "os_version": resources.os_version,
            "architecture": resources.cpu_architecture,
        },
        "cpu": {
            "cores": resources.cpu_cores,
            "threads": resources.cpu_threads,
            "frequency_mhz": resources.cpu_frequency_mhz,
        },
        "memory": {
            "total_mb": resources.ram_total_mb,
            "available_mb": resources.ram_available_mb,
            "used_mb": resources.ram_used_mb,
            "total_gb": round(resources.ram_total_mb / 1024, 1),
            "available_gb": round(resources.ram_available_mb / 1024, 1),
        },
        "storage": {
            "total_gb": round(resources.disk_total_gb, 1),
            "free_gb": round(resources.disk_free_gb, 1),
            "used_gb": round(resources.disk_used_gb, 1),
        },
        "virtualization": {
            "hardware_support": resources.virtualization_enabled,
            "kvm_available": resources.kvm_available,
            "virtualbox_available": resources.virtualbox_available,
            "docker_available": resources.docker_available,
        },
        "network": {
            "interfaces": resources.network_interfaces,
            "interface_count": len(resources.network_interfaces),
        },
        "netlab_capacity": {
            "max_cpu_allocation": int(resources.cpu_threads * 0.7),
            "max_ram_allocation_gb": int((resources.ram_available_mb * 0.7) // 1024),
            "max_disk_allocation_gb": int(resources.disk_free_gb * 0.8),
            "estimated_small_vms": max(1, int((resources.ram_available_mb * 0.7) // 1024)),
            "estimated_medium_vms": max(1, int((resources.ram_available_mb * 0.7) // 2048)),
            "estimated_large_vms": max(1, int((resources.ram_available_mb * 0.7) // 4096)),
        },
        "recommendations": _generate_recommendations(resources),
    }


def _generate_recommendations(resources) -> Dict[str, Any]:
    """Generate recommendations based on detected resources."""
    recommendations = {
        "suitability": "good",  # good, limited, poor
        "warnings": [],
        "suggestions": [],
    }
    
    ram_gb = resources.ram_total_mb // 1024
    
    # RAM recommendations
    if ram_gb < 4:
        recommendations["suitability"] = "poor"
        recommendations["warnings"].append("Insufficient RAM for NetLab deployments")
        recommendations["suggestions"].append("Upgrade to at least 8GB RAM")
    elif ram_gb < 8:
        recommendations["suitability"] = "limited"
        recommendations["warnings"].append("Limited RAM for complex network scenarios")
        recommendations["suggestions"].append("Consider upgrading to 16GB+ RAM for better capacity")
    
    # Disk recommendations
    if resources.disk_free_gb < 50:
        recommendations["warnings"].append("Low disk space for VM images")
        recommendations["suggestions"].append("Free up disk space or add storage")
    
    # Virtualization recommendations
    if not resources.virtualization_enabled:
        recommendations["suitability"] = "poor"
        recommendations["warnings"].append("Hardware virtualization not available")
        recommendations["suggestions"].append("Enable VT-x/AMD-V in BIOS settings")
    
    if not (resources.kvm_available or resources.virtualbox_available):
        recommendations["warnings"].append("No VM backend available")
        if resources.platform == "linux":
            recommendations["suggestions"].append("Install KVM/libvirt or VirtualBox")
        else:
            recommendations["suggestions"].append("Install VirtualBox or VMware")
    
    if not resources.docker_available:
        recommendations["warnings"].append("Docker not available")
        recommendations["suggestions"].append("Install Docker for container-based devices")
    
    # CPU recommendations
    if resources.cpu_cores < 4:
        recommendations["warnings"].append("Limited CPU cores for concurrent VMs")
        recommendations["suggestions"].append("Consider using container-based devices")
    
    # Positive recommendations
    if (ram_gb >= 16 and 
        resources.disk_free_gb >= 200 and 
        resources.virtualization_enabled and
        (resources.kvm_available or resources.virtualbox_available)):
        recommendations["suggestions"].append("Excellent system for NetLab deployments!")
        recommendations["suggestions"].append("You can run complex multi-device scenarios")
    
    return recommendations


def main() -> None:
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Detect NetLab host capabilities")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    
    args = parser.parse_args()
    
    capabilities = detect_host_capabilities()
    
    if args.json:
        if args.pretty:
            print(json.dumps(capabilities, indent=2, sort_keys=True))
        else:
            print(json.dumps(capabilities))
    else:
        # Human-readable output
        print("NetLab Host Capability Detection")
        print("=" * 40)
        
        # System info
        sys_info = capabilities["system"]
        print(f"\nSystem: {sys_info['platform']} {sys_info['architecture']}")
        print(f"OS Version: {sys_info['os_version']}")
        
        # Hardware
        cpu_info = capabilities["cpu"]
        mem_info = capabilities["memory"]
        storage_info = capabilities["storage"]
        
        print(f"\nCPU: {cpu_info['cores']} cores ({cpu_info['threads']} threads)")
        print(f"RAM: {mem_info['total_gb']} GB total, {mem_info['available_gb']} GB available")
        print(f"Disk: {storage_info['free_gb']} GB free of {storage_info['total_gb']} GB total")
        
        # Virtualization
        virt_info = capabilities["virtualization"]
        print(f"\nVirtualization:")
        print(f"  Hardware Support: {'✅' if virt_info['hardware_support'] else '❌'}")
        print(f"  KVM Available: {'✅' if virt_info['kvm_available'] else '❌'}")
        print(f"  VirtualBox Available: {'✅' if virt_info['virtualbox_available'] else '❌'}")
        print(f"  Docker Available: {'✅' if virt_info['docker_available'] else '❌'}")
        
        # Capacity estimates
        capacity = capabilities["netlab_capacity"]
        print(f"\nNetLab Capacity Estimates:")
        print(f"  Small VMs (1GB): ~{capacity['estimated_small_vms']} devices")
        print(f"  Medium VMs (2GB): ~{capacity['estimated_medium_vms']} devices")
        print(f"  Large VMs (4GB): ~{capacity['estimated_large_vms']} devices")
        
        # Recommendations
        rec = capabilities["recommendations"]
        print(f"\nSuitability: {rec['suitability'].upper()}")
        
        if rec["warnings"]:
            print("\nWarnings:")
            for warning in rec["warnings"]:
                print(f"  ⚠️  {warning}")
        
        if rec["suggestions"]:
            print("\nSuggestions:")
            for suggestion in rec["suggestions"]:
                print(f"  💡 {suggestion}")


if __name__ == "__main__":
    main()