#!/usr/bin/env python3
"""
NetLab V2 - Comprehensive Network Testing Module
Performs automated testing of all devices in the enterprise network
"""

import subprocess
import json
import time
import threading
from datetime import datetime
import os

class NetLabNetworkTester:
    def __init__(self):
        self.test_results = {}
        self.devices = {
            "gateways": [
                {"name": "DMZ Gateway", "ip": "192.168.10.1", "type": "gateway", "network": "DMZ"},
                {"name": "Corporate Gateway", "ip": "192.168.20.1", "type": "gateway", "network": "Corporate"},
                {"name": "Security Gateway", "ip": "192.168.40.1", "type": "gateway", "network": "Security"}
            ],
            "vms": [
                {"name": "Edge Firewall", "ip": "192.168.10.10", "type": "firewall", "network": "DMZ", "vnc": "5920"},
                {"name": "Web Server 1", "ip": "192.168.10.20", "type": "server", "network": "DMZ", "vnc": "5921"},
                {"name": "Core Router 1", "ip": "192.168.20.2", "type": "router", "network": "Corporate", "vnc": "5922"},
                {"name": "Database Server 1", "ip": "192.168.20.10", "type": "server", "network": "Corporate", "vnc": "5923"},
                {"name": "SIEM Server", "ip": "192.168.40.10", "type": "server", "network": "Security", "vnc": "5924"},
                {"name": "IDS/IPS", "ip": "192.168.40.11", "type": "security", "network": "Security", "vnc": "5925"}
            ],
            "infrastructure": [
                {"name": "Core Switch 1", "ip": "192.168.20.100", "type": "switch", "network": "Corporate"},
                {"name": "Core Switch 2", "ip": "192.168.20.101", "type": "switch", "network": "Corporate"},
                {"name": "Edge Router", "ip": "192.168.10.2", "type": "router", "network": "DMZ"},
                {"name": "Internal Firewall", "ip": "192.168.20.254", "type": "firewall", "network": "Corporate"}
            ]
        }
    
    def ping_test(self, ip, count=3, timeout=2):
        """Perform ping test to a device"""
        try:
            cmd = f"ping -c {count} -W {timeout} {ip}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # Parse ping statistics
                lines = result.stdout.strip().split('\n')
                stats_line = [line for line in lines if 'packet loss' in line]
                if stats_line:
                    loss_percent = stats_line[0].split(',')[2].strip().split('%')[0]
                    return {
                        "status": "success",
                        "packet_loss": f"{loss_percent}%",
                        "response_time": self._extract_avg_time(result.stdout),
                        "raw_output": result.stdout
                    }
                else:
                    return {"status": "success", "packet_loss": "0%", "response_time": "< 1ms"}
            else:
                return {
                    "status": "failed", 
                    "error": "Host unreachable",
                    "packet_loss": "100%",
                    "raw_output": result.stderr
                }
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "error": "Ping timeout", "packet_loss": "100%"}
        except Exception as e:
            return {"status": "error", "error": str(e), "packet_loss": "100%"}
    
    def _extract_avg_time(self, ping_output):
        """Extract average response time from ping output"""
        try:
            for line in ping_output.split('\n'):
                if 'avg' in line and 'min/avg/max' in line:
                    return line.split('=')[1].split('/')[1].strip() + "ms"
            return "< 1ms"
        except:
            return "N/A"
    
    def traceroute_test(self, ip, max_hops=10):
        """Perform traceroute to a device"""
        try:
            # Try traceroute, fallback to tracepath if not available
            for cmd in [f"traceroute -m {max_hops} {ip}", f"tracepath -m {max_hops} {ip}"]:
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        return {"status": "success", "hops": result.stdout.strip().split('\n')}
                    break
                except:
                    continue
            return {"status": "failed", "error": "Traceroute command not available"}
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "error": "Traceroute timeout"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def port_scan(self, ip, ports=[22, 80, 443, 8080]):
        """Perform basic port scan on common ports"""
        try:
            open_ports = []
            for port in ports:
                cmd = f"timeout 2 bash -c '</dev/tcp/{ip}/{port}' 2>/dev/null"
                result = subprocess.run(cmd, shell=True)
                if result.returncode == 0:
                    open_ports.append(port)
            
            return {"status": "success", "open_ports": open_ports}
        except Exception as e:
            return {"status": "error", "error": str(e), "open_ports": []}
    
    def network_discovery(self, network="192.168.10.0/24"):
        """Discover active devices on network"""
        try:
            # Use nmap for network discovery if available
            cmd = f"nmap -sn {network}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                active_ips = []
                for line in result.stdout.split('\n'):
                    if 'Nmap scan report for' in line:
                        ip = line.split()[-1].strip('()')
                        active_ips.append(ip)
                return {"status": "success", "active_devices": active_ips}
            else:
                return {"status": "failed", "error": "Network scan failed"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def comprehensive_device_test(self, device):
        """Run comprehensive test on a single device"""
        test_result = {
            "device": device,
            "timestamp": datetime.now().isoformat(),
            "tests": {}
        }
        
        # Ping test
        print(f"Testing {device['name']} ({device['ip']})...")
        test_result["tests"]["ping"] = self.ping_test(device["ip"])
        
        # Port scan for servers and network devices
        if device["type"] in ["server", "firewall", "router"]:
            test_result["tests"]["ports"] = self.port_scan(device["ip"])
        
        # Traceroute for cross-network devices
        if device["network"] != "DMZ":  # Trace to non-DMZ devices
            test_result["tests"]["traceroute"] = self.traceroute_test(device["ip"])
        
        return test_result
    
    def test_all_devices(self):
        """Test all devices in the network"""
        print("🧪 Starting Comprehensive Network Tests...")
        print("=" * 50)
        
        all_results = {
            "test_session": {
                "start_time": datetime.now().isoformat(),
                "total_devices": 0,
                "devices_tested": 0,
                "success_rate": 0
            },
            "results": {
                "gateways": [],
                "vms": [],
                "infrastructure": []
            },
            "summary": {
                "total_success": 0,
                "total_failed": 0,
                "total_timeout": 0,
                "networks_tested": ["DMZ", "Corporate", "Security"]
            }
        }
        
        # Count total devices
        total_devices = sum(len(devices) for devices in self.devices.values())
        all_results["test_session"]["total_devices"] = total_devices
        
        # Test each category
        for category, devices in self.devices.items():
            print(f"\n📊 Testing {category.upper()} ({len(devices)} devices)")
            print("-" * 40)
            
            for device in devices:
                result = self.comprehensive_device_test(device)
                all_results["results"][category].append(result)
                all_results["test_session"]["devices_tested"] += 1
                
                # Update summary counts
                ping_status = result["tests"]["ping"]["status"]
                if ping_status == "success":
                    all_results["summary"]["total_success"] += 1
                    print(f"✅ {device['name']} - REACHABLE")
                elif ping_status == "timeout":
                    all_results["summary"]["total_timeout"] += 1
                    print(f"⏱️  {device['name']} - TIMEOUT")
                else:
                    all_results["summary"]["total_failed"] += 1
                    print(f"❌ {device['name']} - FAILED")
        
        # Calculate success rate
        success_rate = (all_results["summary"]["total_success"] / total_devices * 100) if total_devices > 0 else 0
        all_results["test_session"]["success_rate"] = round(success_rate, 2)
        all_results["test_session"]["end_time"] = datetime.now().isoformat()
        
        return all_results
    
    def test_network_connectivity_matrix(self):
        """Test connectivity between different network segments"""
        print("\n🌐 Testing Inter-Network Connectivity...")
        print("-" * 40)
        
        connectivity_matrix = {}
        networks = ["DMZ", "Corporate", "Security"]
        
        # Test from each network to others
        for source_net in networks:
            connectivity_matrix[source_net] = {}
            source_gw = f"192.168.{10 if source_net == 'DMZ' else 20 if source_net == 'Corporate' else 40}.1"
            
            for target_net in networks:
                if source_net == target_net:
                    connectivity_matrix[source_net][target_net] = {"status": "local", "latency": "0ms"}
                else:
                    target_gw = f"192.168.{10 if target_net == 'DMZ' else 20 if target_net == 'Corporate' else 40}.1"
                    result = self.ping_test(target_gw, count=2)
                    connectivity_matrix[source_net][target_net] = {
                        "status": result["status"],
                        "latency": result.get("response_time", "N/A"),
                        "packet_loss": result.get("packet_loss", "100%")
                    }
                    
                    status_icon = "✅" if result["status"] == "success" else "❌"
                    print(f"{status_icon} {source_net} → {target_net}: {result['status']}")
        
        return connectivity_matrix
    
    def generate_test_report(self, results, connectivity_matrix):
        """Generate comprehensive test report"""
        report = {
            "report_header": {
                "title": "NetLab V2 - Comprehensive Network Test Report",
                "generated": datetime.now().isoformat(),
                "lab_name": "Enterprise Network Laboratory"
            },
            "executive_summary": {
                "total_devices": results["test_session"]["total_devices"],
                "devices_tested": results["test_session"]["devices_tested"],
                "overall_success_rate": f"{results['test_session']['success_rate']}%",
                "test_duration": self._calculate_duration(
                    results["test_session"]["start_time"],
                    results["test_session"]["end_time"]
                )
            },
            "detailed_results": results,
            "connectivity_matrix": connectivity_matrix,
            "recommendations": self._generate_recommendations(results, connectivity_matrix)
        }
        
        return report
    
    def _calculate_duration(self, start_time, end_time):
        """Calculate test duration"""
        try:
            start = datetime.fromisoformat(start_time)
            end = datetime.fromisoformat(end_time)
            duration = end - start
            return f"{duration.total_seconds():.1f} seconds"
        except:
            return "N/A"
    
    def _generate_recommendations(self, results, connectivity_matrix):
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check for failed devices
        failed_count = results["summary"]["total_failed"]
        timeout_count = results["summary"]["total_timeout"]
        
        if failed_count > 0:
            recommendations.append({
                "priority": "high",
                "issue": f"{failed_count} devices are unreachable",
                "recommendation": "Check VM status, network configuration, and ensure devices are powered on"
            })
        
        if timeout_count > 0:
            recommendations.append({
                "priority": "medium",
                "issue": f"{timeout_count} devices are timing out",
                "recommendation": "Investigate network latency, firewall rules, or device performance"
            })
        
        # Check connectivity matrix for issues
        for source, targets in connectivity_matrix.items():
            for target, result in targets.items():
                if source != target and result["status"] != "success":
                    recommendations.append({
                        "priority": "medium",
                        "issue": f"No connectivity from {source} to {target}",
                        "recommendation": "Check inter-VLAN routing and firewall rules"
                    })
        
        if not recommendations:
            recommendations.append({
                "priority": "info",
                "issue": "All network tests passed",
                "recommendation": "Network is operating optimally"
            })
        
        return recommendations

def main():
    """Main testing function"""
    tester = NetLabNetworkTester()
    
    # Run comprehensive tests
    test_results = tester.test_all_devices()
    
    # Test connectivity matrix
    connectivity_matrix = tester.test_network_connectivity_matrix()
    
    # Generate report
    report = tester.generate_test_report(test_results, connectivity_matrix)
    
    # Save report
    os.makedirs("/netlab/state/reports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"/netlab/state/reports/network_test_{timestamp}.json"
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Also save latest report
    with open("/netlab/state/latest_network_test.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📋 Test Report Generated: {report_file}")
    print(f"📊 Overall Success Rate: {report['executive_summary']['overall_success_rate']}")
    print("✅ Network testing complete!")
    
    return report

if __name__ == "__main__":
    main()