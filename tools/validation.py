#!/usr/bin/env python3
"""
NetLab V2 - Topology Validation Utility
Validates topology files for correctness and completeness
"""

import argparse
import yaml
import ipaddress
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple

class TopologyValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
        
    def validate_file(self, topology_file: str) -> bool:
        """Validate a topology file"""
        print(f"🔍 Validating topology: {topology_file}")
        
        try:
            with open(topology_file, 'r') as f:
                topology = yaml.safe_load(f)
        except Exception as e:
            self.errors.append(f"Failed to parse YAML: {e}")
            return False
        
        # Run all validation checks
        self._validate_required_fields(topology)
        self._validate_constraints(topology)
        self._validate_networks(topology)
        self._validate_vms(topology)
        self._validate_resource_allocation(topology)
        self._validate_network_assignments(topology)
        self._validate_ip_assignments(topology)
        
        return len(self.errors) == 0
    
    def _validate_required_fields(self, topology: Dict):
        """Validate required top-level fields"""
        required_fields = ["name", "description", "version", "constraints", "networks", "vms"]
        
        for field in required_fields:
            if field not in topology:
                self.errors.append(f"Missing required field: {field}")
        
        # Validate version format
        if "version" in topology:
            version = topology["version"]
            if not isinstance(version, str) or not version.count('.') >= 1:
                self.errors.append(f"Invalid version format: {version}")
    
    def _validate_constraints(self, topology: Dict):
        """Validate resource constraints"""
        if "constraints" not in topology:
            return
        
        constraints = topology["constraints"]
        required_constraints = ["max_ram", "max_disk", "max_cpu"]
        
        for constraint in required_constraints:
            if constraint not in constraints:
                self.errors.append(f"Missing constraint: {constraint}")
                continue
            
            value = constraints[constraint]
            if not isinstance(value, (int, float)) or value <= 0:
                self.errors.append(f"Invalid {constraint} value: {value}")
        
        # Check reasonable limits
        if "max_ram" in constraints and constraints["max_ram"] > 128000:
            self.warnings.append(f"Very high RAM allocation: {constraints['max_ram']}MB")
        
        if "max_disk" in constraints and constraints["max_disk"] > 1000000:
            self.warnings.append(f"Very high disk allocation: {constraints['max_disk']}MB")
    
    def _validate_networks(self, topology: Dict):
        """Validate network definitions"""
        if "networks" not in topology:
            return
        
        networks = topology["networks"]
        if not networks:
            self.errors.append("No networks defined")
            return
        
        for net_name, net_config in networks.items():
            if not isinstance(net_config, dict):
                self.errors.append(f"Network {net_name} must be a dictionary")
                continue
            
            # Validate required network fields
            required_fields = ["subnet", "gateway"]
            for field in required_fields:
                if field not in net_config:
                    self.errors.append(f"Network {net_name} missing {field}")
            
            # Validate subnet format
            if "subnet" in net_config:
                try:
                    network = ipaddress.ip_network(net_config["subnet"], strict=False)
                    self.info.append(f"Network {net_name}: {network}")
                    
                    # Validate gateway is in subnet
                    if "gateway" in net_config:
                        gateway = ipaddress.ip_address(net_config["gateway"])
                        if gateway not in network:
                            self.errors.append(f"Gateway {gateway} not in subnet {network}")
                            
                except ValueError as e:
                    self.errors.append(f"Invalid subnet in network {net_name}: {e}")
    
    def _validate_vms(self, topology: Dict):
        """Validate VM definitions"""
        if "vms" not in topology:
            return
        
        vms = topology["vms"]
        if not vms:
            self.errors.append("No VMs defined")
            return
        
        vm_names = []
        vm_ips = []
        vnc_ports = []
        
        for i, vm in enumerate(vms):
            if not isinstance(vm, dict):
                self.errors.append(f"VM {i} must be a dictionary")
                continue
            
            # Validate required VM fields
            required_fields = ["name", "type", "network", "ip", "memory"]
            for field in required_fields:
                if field not in vm:
                    self.errors.append(f"VM {vm.get('name', i)} missing {field}")
            
            # Check for duplicate names
            vm_name = vm.get("name")
            if vm_name in vm_names:
                self.errors.append(f"Duplicate VM name: {vm_name}")
            else:
                vm_names.append(vm_name)
            
            # Validate IP address format
            if "ip" in vm:
                try:
                    ip = ipaddress.ip_address(vm["ip"])
                    if str(ip) in vm_ips:
                        self.errors.append(f"Duplicate IP address: {ip}")
                    else:
                        vm_ips.append(str(ip))
                except ValueError:
                    self.errors.append(f"Invalid IP address in VM {vm_name}: {vm['ip']}")
            
            # Check VNC port conflicts
            if "vnc_port" in vm:
                vnc_port = vm["vnc_port"]
                if vnc_port in vnc_ports:
                    self.errors.append(f"Duplicate VNC port: {vnc_port}")
                else:
                    vnc_ports.append(vnc_port)
                
                # Check port range
                if not (5900 <= vnc_port <= 5999):
                    self.warnings.append(f"VNC port {vnc_port} outside standard range (5900-5999)")
            
            # Validate memory allocation
            if "memory" in vm:
                memory = vm["memory"]
                if not isinstance(memory, int) or memory <= 0:
                    self.errors.append(f"Invalid memory allocation in VM {vm_name}: {memory}")
                elif memory < 256:
                    self.warnings.append(f"Low memory allocation in VM {vm_name}: {memory}MB")
    
    def _validate_resource_allocation(self, topology: Dict):
        """Validate total resource allocation against constraints"""
        if "vms" not in topology or "constraints" not in topology:
            return
        
        vms = topology["vms"]
        constraints = topology["constraints"]
        
        total_memory = sum(vm.get("memory", 512) for vm in vms)
        total_cpu = sum(vm.get("cpu", 1) for vm in vms)
        
        if "max_ram" in constraints and total_memory > constraints["max_ram"]:
            self.errors.append(f"Total memory allocation ({total_memory}MB) exceeds constraint ({constraints['max_ram']}MB)")
        
        if "max_cpu" in constraints and total_cpu > constraints["max_cpu"]:
            self.errors.append(f"Total CPU allocation ({total_cpu}) exceeds constraint ({constraints['max_cpu']})")
        
        # Calculate estimated disk usage
        total_disk = sum(
            int(vm.get("disk", "4GB").replace("GB", "")) * 1000 
            for vm in vms
        )
        
        if "max_disk" in constraints and total_disk > constraints["max_disk"]:
            self.errors.append(f"Total disk allocation (~{total_disk}MB) exceeds constraint ({constraints['max_disk']}MB)")
    
    def _validate_network_assignments(self, topology: Dict):
        """Validate VM network assignments"""
        if "vms" not in topology or "networks" not in topology:
            return
        
        networks = topology["networks"]
        vms = topology["vms"]
        
        for vm in vms:
            vm_name = vm.get("name", "unknown")
            network = vm.get("network")
            
            if network and network not in networks:
                self.errors.append(f"VM {vm_name} assigned to undefined network: {network}")
    
    def _validate_ip_assignments(self, topology: Dict):
        """Validate IP address assignments are within correct subnets"""
        if "vms" not in topology or "networks" not in topology:
            return
        
        networks = topology["networks"]
        vms = topology["vms"]
        
        for vm in vms:
            vm_name = vm.get("name", "unknown")
            network_name = vm.get("network")
            vm_ip = vm.get("ip")
            
            if not all([network_name, vm_ip, network_name in networks]):
                continue
            
            try:
                network = ipaddress.ip_network(networks[network_name]["subnet"], strict=False)
                ip = ipaddress.ip_address(vm_ip)
                
                if ip not in network:
                    self.errors.append(f"VM {vm_name} IP {ip} not in network {network_name} subnet {network}")
                    
            except ValueError as e:
                # Already caught in other validations
                pass
    
    def print_results(self):
        """Print validation results"""
        print("\n" + "="*50)
        print("🔍 VALIDATION RESULTS")
        print("="*50)
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        if self.info:
            print(f"\n📋 INFO ({len(self.info)}):")
            for info in self.info:
                print(f"  • {info}")
        
        print(f"\n📊 SUMMARY:")
        print(f"  Errors: {len(self.errors)}")
        print(f"  Warnings: {len(self.warnings)}")
        print(f"  Status: {'❌ INVALID' if self.errors else '✅ VALID'}")

def main():
    parser = argparse.ArgumentParser(description="NetLab V2 Topology Validator")
    parser.add_argument("topology", help="Topology YAML file to validate")
    parser.add_argument("--strict", action="store_true", 
                       help="Treat warnings as errors")
    
    args = parser.parse_args()
    
    if not Path(args.topology).exists():
        print(f"❌ Topology file not found: {args.topology}")
        sys.exit(1)
    
    validator = TopologyValidator()
    is_valid = validator.validate_file(args.topology)
    validator.print_results()
    
    if args.strict and validator.warnings:
        print("\n⚠️  Strict mode: Treating warnings as errors")
        is_valid = False
    
    sys.exit(0 if is_valid else 1)

if __name__ == "__main__":
    main()