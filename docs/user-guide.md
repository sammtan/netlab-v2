# NetLab V2 - Complete User Guide

[![Guide](https://img.shields.io/badge/User%20Guide-Complete-green.svg)](user-guide.md)
[![Difficulty](https://img.shields.io/badge/Difficulty-Beginner%20to%20Advanced-blue.svg)](user-guide.md)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey.svg)](user-guide.md)

> **Your comprehensive guide to mastering NetLab V2 - From first deployment to advanced network scenarios**

## 🎯 Introduction

NetLab V2 is a powerful, containerized cyber range platform designed for cybersecurity professionals, educators, and researchers. This guide will walk you through everything you need to know to become productive with NetLab V2.

### **What You'll Learn**
- ✅ Complete installation and setup process
- ✅ Deploying your first network laboratory
- ✅ Managing virtual machines and networks
- ✅ Running network tests and validations  
- ✅ Advanced topology customization
- ✅ Troubleshooting common issues
- ✅ Best practices for production use

### **Prerequisites**
- **Basic Linux/Windows knowledge**: Command line comfort
- **Docker familiarity**: Understanding containers and volumes
- **Network concepts**: IP addressing, VLANs, basic routing
- **Hardware**: 8+ CPU cores, 16GB+ RAM, 100GB+ storage recommended

---

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [First Deployment](#first-deployment)
3. [Understanding the Interface](#understanding-the-interface)
4. [VM Management](#vm-management)
5. [Network Configuration](#network-configuration)
6. [Testing & Validation](#testing--validation)
7. [Advanced Usage](#advanced-usage)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)
10. [FAQ](#frequently-asked-questions)

---

## 🚀 Getting Started

### **Step 1: System Requirements Check**

Before installing NetLab V2, verify your system meets the requirements:

```bash
# Check system resources
echo "=== System Requirements Check ==="
echo "CPU Cores: $(nproc)"
echo "Total RAM: $(free -h | awk '/^Mem:/ {print $2}')"
echo "Available Disk: $(df -h . | awk 'NR==2 {print $4}')"
echo "Docker Version: $(docker --version 2>/dev/null || echo 'Not installed')"

# Minimum requirements:
# CPU: 4+ cores (8+ recommended)
# RAM: 8GB+ (16GB+ recommended)  
# Disk: 50GB+ available (100GB+ recommended)
# Docker: 20.10+ with WSL2 on Windows
```

### **Step 2: Installation**

Clone the repository and run the setup:

```bash
# Clone NetLab V2
git clone https://github.com/sammtan/netlab-v2.git
cd netlab-v2

# Run installation and setup
python3 netlab-bridge.py setup

# Expected output:
# 🐳 Building IDEV container...
# 🐳 Building ODRE container...
# ✅ NetLab V2 installation complete!
```

### **Step 3: Verify Installation**

```bash
# Check system status
python3 netlab-bridge.py status

# Expected output:
# ✅ IDEV Container: Ready
# ✅ ODRE Container: Ready  
# ✅ Docker Images: Built
# ✅ System Status: Ready for deployment
```

---

## 🏗️ First Deployment

### **Deploy Your First Network Lab**

Let's deploy the enterprise network topology with guided steps:

```bash
# Step 1: Enter the development environment
python3 netlab-bridge.py dev

# You're now inside the IDEV container
# Step 2: Examine available topologies
ls topologies/

# Output: enterprise-network-lab.yaml, basic-security.yaml, ...

# Step 3: Deploy the enterprise lab
netlab-deploy enterprise-network-lab.yaml

# Expected deployment process:
# 🌐 Parsing topology configuration...
# 🔧 Creating network bridges...
# 💾 Preparing VM disk images...
# 🚀 Deploying virtual machines...
# ✅ Enterprise network lab deployed successfully!
```

### **Understanding Deployment Output**

```bash
Deployment Summary:
==================
✅ Network Bridges: 3 created
   • netlab-dmz (192.168.10.0/24)
   • netlab-corp (192.168.20.0/24)  
   • netlab-sec (192.168.40.0/24)

✅ Virtual Machines: 17 deployed
   • Edge Firewall (VNC: 5920)
   • Web Server (VNC: 5921)
   • Core Router (VNC: 5922)
   • [... 14 more VMs ...]

✅ Management Interface: 
   • Web Dashboard: http://localhost:9000
   • API Endpoint: http://localhost:9000/api/

Next Steps:
===========
1. Open web dashboard: http://localhost:9000
2. Access VM consoles via VNC
3. Run network tests: python3 network-tester.py
```

### **Accessing Your Lab**

**Option 1: Web Dashboard** (Recommended for beginners)
```bash
# Open in your browser
http://localhost:9000

# Features:
# • Real-time network topology visualization
# • One-click VNC access to VMs
# • Interactive network testing
# • System monitoring and logs
```

**Option 2: VNC Clients** (Direct VM access)
```bash
# Connect to VMs using your VNC client:
# Edge Firewall: localhost:5920
# Web Server: localhost:5921
# Core Router: localhost:5922
# ... (additional VMs on sequential ports)
```

**Option 3: Command Line Tools**
```bash
# Inside IDEV container:
netlab-status          # Show deployment status
network-tester.py      # Run network connectivity tests
vm-manager.py          # Manage individual VMs
```

---

## 🖥️ Understanding the Interface

### **Web Dashboard Overview**

The NetLab V2 web dashboard provides a comprehensive interface for managing your cyber range:

```
┌─────────────────────────────────────────────────────────────────┐
│ NetLab V2 - Network Management Dashboard                       │
├─────────────────────────────────────────────────────────────────┤
│ Status: ✅ Online | VMs: 17/17 | Networks: 3 | Tests: Ready    │
├─────────────────┬───────────────────────────┬───────────────────┤
│ 🧪 Test Panel  │ 🌐 Network Topology      │ 📊 Results Panel │
│                │                           │                   │
│ • Full Test     │ [Interactive Topology]   │ • Live Results    │
│ • Connectivity  │                           │ • Test History    │
│ • Discovery     │ Click devices for VNC    │ • Performance     │
│ • Ping Test     │ Real-time status         │ • Export Data     │
│                │                           │                   │
├─────────────────┼───────────────────────────┼───────────────────┤
│ 📈 Statistics  │ Network Information       │ 🎮 Quick Actions │
│                │                           │                   │
│ Success: 95%    │ DMZ: 192.168.10.0/24     │ • VM Control      │
│ Failed: 2       │ Corp: 192.168.20.0/24    │ • Settings        │
│ Avg Latency:1ms │ Sec: 192.168.40.0/24     │ • Documentation   │
└─────────────────┴───────────────────────────┴───────────────────┘
```

### **Key Dashboard Features**

1. **Real-time Topology View**
   - Visual representation of your network
   - Color-coded status indicators (green=running, red=failed)
   - Click-to-connect VNC access
   - Network connection visualization

2. **Testing Panel**
   - Automated network connectivity tests
   - Performance benchmarking
   - Security validation
   - Custom test scenarios

3. **Live Results**
   - Real-time test execution
   - Historical test data
   - Performance metrics
   - Export capabilities

### **Navigation Tips**

```bash
Dashboard Navigation:
====================
🖱️ Click on VM nodes → Opens VNC console
🧪 Test buttons → Runs network tests
📊 Metrics → Shows performance data
⚙️ Settings → Configuration options
❓ Help → Documentation links

Keyboard Shortcuts:
==================
Ctrl + R → Refresh dashboard
Ctrl + T → Run quick test
Ctrl + H → Show/hide help
Escape → Close modals/popups
```

---

## 🖥️ VM Management

### **Understanding VM Types**

NetLab V2 deploys different types of VMs for specific network functions:

```yaml
VM_Types:
  firewall:
    purpose: "Network security and filtering"
    examples: "Edge Firewall, Internal Firewalls"
    typical_config:
      - IP forwarding enabled
      - iptables/nftables configured
      - Multi-interface networking
      - Security monitoring tools

  server:
    purpose: "Application and service hosting"
    examples: "Web Server, Database Server, File Server"
    typical_config:
      - Web services (nginx, apache)
      - Database services (mysql, postgresql)
      - Application runtimes
      - Monitoring agents

  router:
    purpose: "Network routing and switching"
    examples: "Core Router, Distribution Router"
    typical_config:
      - Routing protocols (OSPF, BGP)
      - Multi-homed networking
      - VLAN support
      - Network management

  security:
    purpose: "Security monitoring and analysis"
    examples: "SIEM Server, IDS/IPS, SOC Workstation"
    typical_config:
      - Security tools (Suricata, ELK stack)
      - Log aggregation
      - Threat detection
      - Forensics capabilities
```

### **VM Lifecycle Management**

**Starting VMs**
```bash
# Via Web Dashboard:
# 1. Open dashboard: http://localhost:9000
# 2. Click on stopped VM (red status)
# 3. Click "Start VM" button

# Via Command Line (inside IDEV):
vm-manager.py start edge-firewall
vm-manager.py start --all-stopped

# Expected output:
# 🚀 Starting edge-firewall...
# ✅ VM started successfully (PID: 1234)
# 🌐 VNC console available on port 5920
```

**Stopping VMs**
```bash
# Graceful shutdown (recommended):
vm-manager.py stop edge-firewall --graceful

# Force shutdown (if needed):
vm-manager.py stop edge-firewall --force

# Stop all VMs:
vm-manager.py stop --all
```

**VM Status Monitoring**
```bash
# Check status of all VMs
vm-manager.py status

# Sample output:
# VM Status Report
# ================
# ✅ edge-firewall    | Running  | PID: 1234 | VNC: 5920
# ✅ web-server       | Running  | PID: 1235 | VNC: 5921  
# ❌ core-router      | Stopped  | -         | -
# ⚠️ database-server  | Starting | PID: 1236 | -
```

### **VM Console Access**

**Method 1: Web Dashboard VNC**
```bash
# Easiest method - no additional software needed
1. Open http://localhost:9000
2. Click on any running VM node
3. Browser-based VNC opens automatically
4. Login with VM credentials (see documentation)
```

**Method 2: VNC Client**
```bash
# Using dedicated VNC client (better performance)
# Windows: Use TightVNC, RealVNC, or UltraVNC
# Linux: Use vncviewer, remmina, or tiger-vnc
# macOS: Use built-in Screen Sharing or VNC Viewer

# Connection details:
Host: localhost
Port: 5920 (edge-firewall), 5921 (web-server), etc.
Password: netlab123 (default, configurable)
```

**Method 3: SSH Access** (Advanced)
```bash
# Once VMs are network-configured, SSH is available
ssh admin@192.168.10.10  # Edge firewall
ssh admin@192.168.10.20  # Web server
# Default password: netlab123 (change immediately!)
```

### **VM Configuration**

**Automatic Configuration**
```bash
# NetLab V2 provides automated VM configuration
# Inside IDEV container:
vm-configurator.py --all

# This process:
# 1. Mounts configuration ISOs to each VM
# 2. Executes network setup scripts
# 3. Configures IP addresses and routing
# 4. Installs required packages
# 5. Starts essential services
```

**Manual Configuration** (if needed)
```bash
# Connect to VM via VNC
# Mount configuration ISO:
sudo mount /dev/cdrom /mnt

# Run configuration script:
sudo sh /mnt/network-config.sh

# Verify configuration:
ip addr show eth0
ping 8.8.8.8
```

### **VM Troubleshooting**

**Common Issues and Solutions**

1. **VM Won't Start**
```bash
# Check system resources:
free -h && df -h
# Solution: Free up memory/disk space

# Check for port conflicts:
netstat -tulpn | grep 592
# Solution: Kill conflicting processes

# Check container status:
docker ps | grep netlab
# Solution: Restart containers if needed
```

2. **No Network Connectivity**
```bash
# Check bridge networks:
sudo ip link show type bridge | grep netlab
# Solution: Restart network deployment

# Check VM network config:
# Connect via VNC and verify IP settings
ip addr show && ip route show
```

3. **VNC Connection Issues**
```bash
# Check VNC ports:
netstat -tulpn | grep 592
# Solution: Ensure VNC service is running in VM

# Test local connectivity:
telnet localhost 5920
# Solution: Restart VM if port is not accessible
```

---

## 🌐 Network Configuration

### **Understanding Network Architecture**

NetLab V2 implements a realistic enterprise network with proper VLAN segmentation:

```
Network Architecture:
====================
                    [Internet Simulation]
                            |
                    [Edge Firewall]
                      192.168.10.10
                            |
        ┌──────────────────┼──────────────────┐
        |                  |                  |
   [DMZ Network]    [Corporate Network]  [Security Network]
  192.168.10.0/24    192.168.20.0/24     192.168.40.0/24
        |                  |                  |
   • Web Server         • Core Router      • SIEM Server
   • Load Balancer      • Database Srv     • IDS/IPS
   • DNS Server         • File Server      • SOC Workstation
```

### **Network Bridges**

Each network segment is implemented as a Linux bridge:

```bash
# View network bridges
sudo ip link show type bridge

# Expected output:
# netlab-dmz: DMZ network bridge
# netlab-corp: Corporate network bridge  
# netlab-sec: Security network bridge

# Bridge details:
sudo ip addr show netlab-dmz

# Output:
# netlab-dmz: <BROADCAST,MULTICAST,UP,LOWER_UP>
#     inet 192.168.10.1/24 brd 192.168.10.255 scope global
#     Connected interfaces: tap0, tap1, tap2
```

### **Network Testing**

**Comprehensive Network Tests**
```bash
# Run complete network validation
network-tester.py --full

# Test output:
# 🌐 NetLab V2 Network Testing Suite
# ===================================
# 
# 🔍 Testing Network Infrastructure...
# ✅ Bridge netlab-dmz: UP (192.168.10.1/24)
# ✅ Bridge netlab-corp: UP (192.168.20.1/24)
# ✅ Bridge netlab-sec: UP (192.168.40.1/24)
# 
# 🖥️ Testing VM Connectivity...
# ✅ edge-firewall (192.168.10.10): Reachable (1.2ms)
# ✅ web-server (192.168.10.20): Reachable (0.8ms)
# ✅ core-router (192.168.20.2): Reachable (1.1ms)
# [... more VMs ...]
# 
# 🔗 Testing Inter-VLAN Connectivity...
# ✅ DMZ → Corporate: Routed via firewall
# ✅ Corporate → Security: Routed via core router
# ❌ DMZ → Security: Blocked (security policy)
# 
# 📊 Test Summary:
# Total Tests: 45
# Passed: 42 (93.3%)
# Failed: 3 (6.7%)
# Average Latency: 1.1ms
```

**Specific Network Tests**
```bash
# Test specific components:
network-tester.py --bridges      # Test bridge connectivity
network-tester.py --vms         # Test all VM connectivity
network-tester.py --routing     # Test inter-VLAN routing
network-tester.py --performance # Test network performance

# Test individual VMs:
network-tester.py --target 192.168.10.10 --detailed

# Performance benchmarking:
network-tester.py --performance --duration 60
```

### **Network Troubleshooting**

**Common Network Issues**

1. **Bridge Not Created**
```bash
# Symptom: VMs can't reach network
# Check: Bridge existence
sudo ip link show type bridge | grep netlab

# Solution: Recreate bridges
netlab-deploy enterprise-network-lab.yaml --network-only
```

2. **IP Address Conflicts**
```bash
# Symptom: Some VMs unreachable
# Check: IP address assignments
network-tester.py --scan

# Solution: Reconfigure VM networking
vm-configurator.py --fix-networking
```

3. **Inter-VLAN Routing Issues**
```bash
# Symptom: VMs in different VLANs can't communicate
# Check: Routing table
ip route show

# Check firewall VM routing:
# Connect to edge-firewall via VNC
cat /proc/sys/net/ipv4/ip_forward  # Should be 1

# Solution: Enable IP forwarding and configure routes
```

### **Custom Network Configuration**

**Adding Custom Routes**
```bash
# Add static routes for special requirements
# Example: Route security network traffic through DMZ
sudo ip route add 192.168.40.0/24 via 192.168.10.10 dev netlab-dmz
```

**Creating Additional Networks**
```bash
# Create custom bridge network
sudo ip link add name netlab-custom type bridge
sudo ip addr add 192.168.50.1/24 dev netlab-custom
sudo ip link set netlab-custom up

# Connect VM to custom network
# Modify VM configuration to add second interface
```

---

## 🧪 Testing & Validation

### **Built-in Testing Suite**

NetLab V2 includes comprehensive testing capabilities to validate your network deployments:

**Test Categories**
```bash
Infrastructure Tests:
====================
• Bridge Network Validation
• VM Deployment Verification
• Container Health Checks
• Resource Utilization Monitoring

Connectivity Tests:
===================
• Ping Tests (ICMP reachability)
• Port Scanning (Service availability)
• Throughput Testing (Network performance)
• Latency Measurements

Security Tests:
===============
• Network Segmentation Validation
• Access Control Testing
• Configuration Compliance
• Vulnerability Scanning (basic)

Performance Tests:
==================
• Network Throughput Benchmarking
• VM Resource Usage Monitoring
• Concurrent Connection Testing
• Stress Testing Scenarios
```

### **Running Tests**

**Quick Network Test**
```bash
# Basic connectivity test (recommended first step)
network-tester.py --quick

# Output:
# 🚀 Quick Network Test
# =====================
# ✅ All bridges operational
# ✅ 15/17 VMs responding
# ⚠️ 2 VMs need configuration
# ✅ Basic connectivity working
# 
# Issues Found:
# • database-server: Not configured
# • siem-server: Service starting
```

**Comprehensive Test**
```bash
# Full test suite (takes 5-10 minutes)
network-tester.py --comprehensive

# This runs:
# 1. Infrastructure validation
# 2. All VM connectivity tests
# 3. Inter-VLAN routing verification
# 4. Performance benchmarks
# 5. Security configuration checks
```

**Security-Focused Testing**
```bash
# Test network segmentation and security
security-tester.py --network-isolation

# Test output:
# 🔒 Security Configuration Test
# ==============================
# ✅ DMZ isolation: Properly configured
# ✅ Corporate network: Isolated from DMZ
# ✅ Security network: Management access only
# ⚠️ Web server: HTTP service exposed (expected)
# ❌ Database server: MySQL port open to DMZ (review needed)
```

### **Test Automation**

**Scheduled Testing**
```bash
# Set up automated testing (inside IDEV)
crontab -e

# Add entries for regular testing:
# Test every hour
0 * * * * /netlab/tools/network-tester.py --quick --log

# Full test daily at 2 AM
0 2 * * * /netlab/tools/network-tester.py --comprehensive --report

# Security check weekly
0 2 * * 0 /netlab/tools/security-tester.py --full --email
```

**Custom Test Scripts**
```bash
# Create custom test scenario
cat > custom-test.py << 'EOF'
#!/usr/bin/env python3
"""
Custom NetLab V2 Test Scenario
Test specific application functionality
"""

import requests
import time
from netlab_testing import NetworkTester, VMTester

def test_web_application():
    """Test web server functionality"""
    print("🌐 Testing Web Application...")
    
    # Test web server response
    try:
        response = requests.get('http://192.168.10.20', timeout=5)
        if response.status_code == 200:
            print("✅ Web server responding")
        else:
            print(f"❌ Web server error: {response.status_code}")
    except:
        print("❌ Web server unreachable")

def test_database_connectivity():
    """Test database server connectivity"""
    print("🗄️ Testing Database Connectivity...")
    # Add your database tests here
    
if __name__ == "__main__":
    test_web_application()
    test_database_connectivity()
EOF

chmod +x custom-test.py
python3 custom-test.py
```

### **Test Reporting**

**Generate Test Reports**
```bash
# Generate detailed HTML report
network-tester.py --report --format html --output network-report.html

# Generate JSON data for external systems
network-tester.py --report --format json --output test-results.json

# Generate executive summary
network-tester.py --summary --email admin@company.com
```

**Understanding Test Results**
```bash
Test Result Interpretation:
===========================
✅ PASS: Test completed successfully
⚠️ WARNING: Test passed with minor issues
❌ FAIL: Test failed, requires attention
🔄 RUNNING: Test currently in progress
⏸️ SKIPPED: Test skipped due to dependencies

Performance Metrics:
===================
Latency: < 5ms = Excellent, < 10ms = Good, > 10ms = Review needed
Throughput: > 100Mbps = Good for lab environment
Packet Loss: 0% = Perfect, < 1% = Acceptable, > 1% = Issue
Success Rate: > 95% = Excellent, > 90% = Good, < 90% = Review needed
```

---

## 🔧 Advanced Usage

### **Custom Topology Creation**

**Understanding Topology Files**
```yaml
# topology-template.yaml
name: my-custom-topology
description: Custom network lab for specific training
version: "2.0"

# Resource constraints
constraints:
  max_ram: 16000    # MB
  max_disk: 60000   # MB  
  max_cpu: 8        # cores

# Network definitions
networks:
  dmz:
    subnet: "192.168.10.0/24"
    gateway: "192.168.10.1" 
    purpose: "External services"
  
  internal:
    subnet: "192.168.20.0/24"
    gateway: "192.168.20.1"
    purpose: "Internal services"

# VM definitions
vms:
  - name: "custom-firewall"
    type: "firewall"
    network: "dmz"
    ip: "192.168.10.10"
    memory: 512
    disk: "4GB"
    vnc_port: 5920
    
  - name: "web-app"
    type: "server"
    network: "dmz" 
    ip: "192.168.10.20"
    memory: 1024
    disk: "8GB"
    vnc_port: 5921
    packages:
      - nginx
      - php-fpm
      - mysql-client
```

**Deploying Custom Topologies**
```bash
# Validate topology before deployment
netlab-validate my-custom-topology.yaml

# Deploy custom topology
netlab-deploy my-custom-topology.yaml

# Monitor deployment progress
netlab-status --follow
```

### **Advanced VM Customization**

**Custom VM Images**
```bash
# Create base VM image
qemu-img create -f qcow2 custom-vm.qcow2 8G

# Install OS (connect via VNC during installation)
qemu-system-x86_64 \
  -hda custom-vm.qcow2 \
  -cdrom alpine-linux.iso \
  -boot d \
  -vnc :20 \
  -m 1024

# Convert to NetLab format
vm-manager.py import-image custom-vm.qcow2 --name custom-server
```

**VM Automation Scripts**
```bash
# Create automated VM configuration
cat > vm-automation.sh << 'EOF'
#!/bin/sh
# Custom VM setup automation

# Install additional packages
apk update
apk add docker nodejs npm python3

# Configure services
rc-update add docker default
service docker start

# Create user accounts
adduser -D -s /bin/sh labuser
echo "labuser:labpass123" | chpasswd

# Custom application setup
git clone https://github.com/your-org/lab-app.git /opt/lab-app
cd /opt/lab-app && npm install

echo "✅ Custom VM configuration complete"
EOF
```

### **Network Monitoring Integration**

**External Monitoring Setup**
```bash
# Export network data to external systems
# Install monitoring agents in VMs

# Example: Prometheus monitoring
cat > prometheus-config.yml << 'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'netlab-vms'
    static_configs:
      - targets: 
        - '192.168.10.10:9100'  # Node exporter on firewall
        - '192.168.10.20:9100'  # Node exporter on web server
        - '192.168.20.10:9100'  # Node exporter on database

  - job_name: 'netlab-api'
    static_configs:
      - targets: ['localhost:9000']
EOF

# Start monitoring stack
docker run -d -p 9090:9090 \
  -v $(pwd)/prometheus-config.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

### **API Integration**

**Automation via REST API**
```python
#!/usr/bin/env python3
"""
NetLab V2 API Integration Example
Automate lab management via REST API
"""

import requests
import time

class NetLabAPI:
    def __init__(self, base_url="http://localhost:9000"):
        self.base_url = base_url
        
    def get_status(self):
        """Get system status"""
        response = requests.get(f"{self.base_url}/api/status")
        return response.json()
    
    def list_vms(self):
        """List all VMs"""
        response = requests.get(f"{self.base_url}/api/vms")
        return response.json()
    
    def start_vm(self, vm_id):
        """Start specific VM"""
        response = requests.post(f"{self.base_url}/api/vms/{vm_id}/start")
        return response.json()
    
    def run_network_test(self):
        """Run connectivity test"""
        response = requests.post(f"{self.base_url}/api/test/connectivity")
        return response.json()

# Example usage
def automate_lab_startup():
    api = NetLabAPI()
    
    # Check system status
    status = api.get_status()
    print(f"System Status: {status['data']['odre_status']}")
    
    # Start all stopped VMs
    vms = api.list_vms()
    for vm in vms['data']['vms']:
        if vm['status'] == 'stopped':
            print(f"Starting {vm['name']}...")
            api.start_vm(vm['id'])
    
    # Wait for VMs to boot
    time.sleep(60)
    
    # Run network test
    test_result = api.run_network_test()
    print(f"Network Test: {test_result['data']['summary']['success_rate']}% success")

if __name__ == "__main__":
    automate_lab_startup()
```

---

## 🔧 Troubleshooting

### **Common Issues and Solutions**

**1. Installation Problems**

*Issue: Docker build fails*
```bash
Error: Package installation failed
Solution:
# Update package lists
sudo apt update && sudo apt upgrade

# Install required dependencies
sudo apt install -y build-essential python3-dev

# Rebuild containers
python3 netlab-bridge.py setup --rebuild
```

*Issue: Permission denied errors*
```bash
Error: Cannot connect to Docker daemon
Solution:
# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in, then retry
```

**2. Deployment Issues**

*Issue: VMs won't start*
```bash
# Check available resources
free -h && df -h

# Check for conflicting processes  
ps aux | grep qemu

# Solution: Free resources and retry
docker system prune -f
python3 netlab-bridge.py cleanup
python3 netlab-bridge.py setup
```

*Issue: Network bridges not created*
```bash
# Check Docker networking
docker network ls

# Restart Docker service
sudo systemctl restart docker

# Recreate bridges manually if needed
sudo ip link add name netlab-dmz type bridge
sudo ip addr add 192.168.10.1/24 dev netlab-dmz
sudo ip link set netlab-dmz up
```

**3. Connectivity Problems**

*Issue: VMs not reachable*
```bash
# Diagnose network connectivity
ping 192.168.10.10  # From host

# Check bridge status
sudo ip link show type bridge

# Check VM network configuration (connect via VNC)
ip addr show eth0
ip route show

# Solution: Reconfigure VM networking
vm-configurator.py --vm edge-firewall --fix-network
```

*Issue: VNC connection refused*
```bash
# Check VNC ports
netstat -tulpn | grep 592

# Check VM status
vm-manager.py status

# Restart specific VM
vm-manager.py restart edge-firewall
```

**4. Performance Issues**

*Issue: Slow VM performance*
```bash
# Check host resource usage
top
iotop

# Check VM resource allocation
docker stats

# Solution: Adjust VM memory allocation
# Edit topology file and redeploy
```

### **Diagnostic Commands**

**System Health Check**
```bash
# Complete system diagnostic
diagnostic-tool.py --full

# Output includes:
# - Host system resources
# - Docker container status  
# - Network bridge configuration
# - VM status and connectivity
# - Performance metrics
# - Configuration validation
```

**Log Analysis**
```bash
# View system logs
tail -f /netlab/logs/netlab.log

# View specific component logs
tail -f /netlab/logs/vm-manager.log
tail -f /netlab/logs/network-manager.log

# View Docker container logs
docker logs netlab-idev
docker logs netlab-odre
```

### **Recovery Procedures**

**Complete System Reset**
```bash
# Nuclear option - complete reset
python3 netlab-bridge.py cleanup --all
python3 netlab-bridge.py setup
# This removes all VMs, networks, and data!
```

**Partial Recovery**
```bash
# Reset network configuration only
netlab-deploy enterprise-network-lab.yaml --network-only

# Reset specific VM
vm-manager.py reset edge-firewall

# Rebuild containers only
python3 netlab-bridge.py setup --rebuild-containers
```

---

## 💡 Best Practices

### **Production Deployment**

**Security Hardening**
```bash
Security Checklist:
===================
✅ Change default VNC passwords
✅ Configure VM SSH key authentication
✅ Enable API authentication
✅ Implement network access controls
✅ Regular security updates
✅ Monitor logs for anomalies
✅ Backup critical configurations
✅ Document security procedures

# Example security configuration:
# 1. Change VNC passwords
vm-manager.py set-vnc-password --all --password "SecurePass123!"

# 2. Configure SSH keys
ssh-keygen -t rsa -b 4096 -f ~/.ssh/netlab_rsa
# Copy public key to VMs

# 3. Enable API authentication
# Edit /netlab/config/api.conf
api_auth_enabled=true
api_token="your-secure-token-here"
```

**Performance Optimization**
```bash
Performance Best Practices:
===========================
1. Resource Allocation:
   • Don't over-allocate memory to VMs
   • Use sparse disk allocation
   • Pin critical VMs to specific CPU cores

2. Network Optimization:
   • Use virtio network drivers
   • Enable multi-queue networking
   • Optimize bridge configurations

3. Storage Optimization:
   • Use SSD storage for VM images
   • Enable qcow2 compression
   • Regular disk cleanup

# Implementation:
# Optimize VM performance
vm-manager.py optimize --vm edge-firewall --cpu-pin 0,1 --memory-balloon

# Optimize network performance
network-optimizer.py --enable-multi-queue --optimize-buffers
```

**Monitoring and Maintenance**
```bash
Maintenance Schedule:
====================
Daily:
  • Check system resource usage
  • Review VM status
  • Check network connectivity
  • Review error logs

Weekly:
  • Run comprehensive tests
  • Update VM configurations
  • Backup critical data
  • Security configuration review

Monthly:
  • Update base images
  • Performance optimization review
  • Documentation updates
  • Disaster recovery testing

# Automated maintenance script:
cat > daily-maintenance.sh << 'EOF'
#!/bin/bash
echo "🔧 NetLab V2 Daily Maintenance - $(date)"

# Check system health
system-health.py --quick --log

# Check VM status
vm-manager.py status --log

# Run network tests
network-tester.py --quick --log

# Cleanup old logs (keep 7 days)
find /netlab/logs -name "*.log" -mtime +7 -delete

# Backup configurations
backup-configs.py --compress

echo "✅ Daily maintenance complete"
EOF

chmod +x daily-maintenance.sh
# Add to cron for automated execution
```

### **Multi-User Environments**

**User Management**
```bash
# Create isolated user environments
create-user-lab.py --username student01 --template basic-security

# User gets isolated:
# - Separate VMs and networks
# - Isolated storage
# - Resource quotas
# - Access controls

# Example user configuration:
User: student01
Resources: 4GB RAM, 25GB disk, 2 CPU cores
Networks: Isolated student01-dmz, student01-corp  
VMs: 5 VMs (firewall, web, router, client, target)
Access: Web dashboard only, no admin functions
```

**Training Environment Setup**
```bash
Training Best Practices:
========================
1. Use resource quotas per user
2. Implement automatic reset capabilities
3. Provide pre-configured scenarios
4. Enable progress tracking
5. Implement assessment tools

# Setup training lab for 20 students:
setup-training.py --students 20 --template security-basics \
  --duration 4hours --auto-reset --assessment-mode

# This creates:
# - 20 isolated environments
# - Automatic progress tracking
# - Assessment and scoring
# - Instructor dashboard
```

---

## ❓ Frequently Asked Questions

### **General Questions**

**Q: What operating systems does NetLab V2 support?**
A: NetLab V2 runs on Windows 10/11 (with WSL2/Docker Desktop) and Linux distributions (Ubuntu 20.04+, CentOS 8+, Debian 10+). The VMs use Alpine Linux by default but can be customized.

**Q: How much resources does NetLab V2 require?**
A: Minimum: 8GB RAM, 50GB disk, 4 CPU cores. Recommended: 16GB+ RAM, 100GB+ disk, 8+ CPU cores. The enterprise lab with 17 VMs uses approximately 12-16GB RAM and 95GB disk.

**Q: Can I run NetLab V2 in the cloud?**
A: Yes! NetLab V2 works well on cloud instances. Recommended cloud instances: AWS c5.2xlarge+, Azure Standard_D4s_v3+, GCP n1-standard-4+.

### **Technical Questions**

**Q: Can I add Windows VMs to NetLab V2?**
A: Currently, NetLab V2 is optimized for Linux VMs (Alpine Linux). Windows VM support is planned for future releases. You can manually add Windows VMs, but they'll require more resources and custom configuration.

**Q: How do I backup my lab configurations?**
A: NetLab V2 automatically backs up configurations to the `.generated/` directory. For permanent backup:
```bash
# Backup everything
tar -czf netlab-backup-$(date +%Y%m%d).tar.gz .generated/

# Backup only configurations (lightweight)
tar -czf netlab-config-backup.tar.gz topologies/ config/
```

**Q: Can I connect NetLab to real networks?**
A: Yes, but with caution. NetLab V2 is designed for isolated environments. For production connectivity:
```bash
# Bridge NetLab to host network (ADVANCED)
sudo ip route add 10.0.0.0/8 via 192.168.10.1 dev netlab-dmz
# Only do this in controlled environments!
```

### **Troubleshooting FAQ**

**Q: My VMs are slow. How can I improve performance?**
A: Several optimization strategies:
```bash
# 1. Allocate more resources to VMs
vm-manager.py configure edge-firewall --memory 1024 --cpu 2

# 2. Use SSD storage
# 3. Enable KVM acceleration (Linux)
# 4. Reduce number of concurrent VMs
# 5. Pin VMs to specific CPU cores
```

**Q: I can't connect to VNC. What's wrong?**
A: Common VNC issues:
```bash
# Check if VM is running
vm-manager.py status

# Check VNC port
netstat -tulpn | grep 5920

# Test VNC connectivity
telnet localhost 5920

# Common solutions:
# 1. Restart the VM
# 2. Check firewall settings
# 3. Verify VNC password
# 4. Try different VNC client
```

**Q: Network tests are failing. How do I debug?**
A: Network debugging steps:
```bash
# 1. Check bridge networks
sudo ip link show type bridge | grep netlab

# 2. Check VM network config (via VNC)
ip addr show eth0
ip route show

# 3. Test basic connectivity
ping 192.168.10.1  # Bridge gateway

# 4. Check firewall rules
iptables -L -n

# 5. Restart network services
systemctl restart networking
```

### **Advanced Usage FAQ**

**Q: Can I create custom VM images?**
A: Yes! NetLab V2 supports custom VM images:
```bash
# Create custom image
qemu-img create -f qcow2 custom-vm.qcow2 8G

# Install your OS and applications via VNC
# Then import into NetLab
vm-manager.py import custom-vm.qcow2 --name my-custom-vm

# Use in topology files
vms:
  - name: "custom-server"
    image: "my-custom-vm"
    # ... other configuration
```

**Q: How do I integrate with external tools?**
A: NetLab V2 provides several integration points:
```bash
# REST API for automation
curl http://localhost:9000/api/status

# Export data for external monitoring  
network-tester.py --export-prometheus

# Webhook notifications
# Configure in /netlab/config/webhooks.conf
webhook_url=https://your-system.com/netlab-webhook
```

**Q: Can I scale NetLab V2 across multiple hosts?**
A: Multi-host deployment is possible but advanced:
```bash
# Shared storage setup (NFS/Ceph)
# Network fabric configuration (VXLAN/GRE)
# Cluster coordination (etcd/consul)
# Load balancing (HAProxy)

# This requires significant network engineering knowledge
# Consider professional services for multi-host deployments
```

---

## 📚 Additional Resources

### **Documentation Links**
- [API Reference](api-reference.md) - Complete REST API documentation
- [System Design](system-design.md) - Architecture deep-dive
- [Installation Guide](installation.md) - Detailed setup instructions
- [Security Guide](security.md) - Security best practices

### **Community Resources**
- **GitHub Issues**: [Report bugs and request features](https://github.com/sammtan/netlab-v2/issues)
- **Discussions**: [Community Q&A](https://github.com/sammtan/netlab-v2/discussions)
- **Discord**: [Real-time community support](https://discord.gg/netlab-v2)

### **Training Materials**
- [Training Scenarios](training-scenarios.md) - Pre-built lab exercises
- [Assessment Tools](assessment-tools.md) - Skills testing materials
- [Certification Prep](certification-prep.md) - Industry cert preparation

---

*This user guide covers the essential aspects of NetLab V2. For advanced topics and latest features, always refer to the official documentation and community resources.*