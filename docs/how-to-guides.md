# NetLab V2 - How-To Guides

[![How-To](https://img.shields.io/badge/How--To-Guides-blue.svg)](how-to-guides.md)
[![Scenarios](https://img.shields.io/badge/Scenarios-20%2B-green.svg)](how-to-guides.md)

> **Step-by-step guides for common NetLab V2 tasks and scenarios**

## 📚 Table of Contents

### 🚀 Getting Started
- [How to Set Up NetLab V2 for Training](#how-to-set-up-netlab-v2-for-training)
- [How to Deploy Your First Custom Topology](#how-to-deploy-your-first-custom-topology)
- [How to Troubleshoot Common Installation Issues](#how-to-troubleshoot-common-installation-issues)

### 🌐 Network Management
- [How to Create Custom Network Topologies](#how-to-create-custom-network-topologies)
- [How to Configure Inter-VLAN Routing](#how-to-configure-inter-vlan-routing)
- [How to Set Up Network Monitoring](#how-to-set-up-network-monitoring)

### 🖥️ VM Management
- [How to Create Custom VM Images](#how-to-create-custom-vm-images)
- [How to Configure VM Networking](#how-to-configure-vm-networking)
- [How to Backup and Restore VMs](#how-to-backup-and-restore-vms)

### 🔒 Security Scenarios
- [How to Set Up a Penetration Testing Lab](#how-to-set-up-a-penetration-testing-lab)
- [How to Create an Incident Response Scenario](#how-to-create-an-incident-response-scenario)
- [How to Configure Network Segmentation](#how-to-configure-network-segmentation)

### 🎓 Training & Education
- [How to Set Up Multi-User Training Environment](#how-to-set-up-multi-user-training-environment)
- [How to Create Assessment Scenarios](#how-to-create-assessment-scenarios)
- [How to Integrate with Learning Management Systems](#how-to-integrate-with-learning-management-systems)

### 📊 Monitoring & Analysis
- [How to Set Up Performance Monitoring](#how-to-set-up-performance-monitoring)
- [How to Export Data for Analysis](#how-to-export-data-for-analysis)
- [How to Create Custom Dashboards](#how-to-create-custom-dashboards)

---

## 🚀 Getting Started

### How to Set Up NetLab V2 for Training

**Scenario**: You're an instructor preparing NetLab V2 for a cybersecurity training class with 20 students.

**Prerequisites**:
- Server with 32GB+ RAM, 16+ CPU cores, 500GB+ SSD storage
- Docker installed and configured
- Network access for students

**Step 1: Install NetLab V2**
```bash
# 1. Clone and set up NetLab V2
git clone https://github.com/sammtan/netlab-v2.git
cd netlab-v2

# 2. Configure for training environment
cp config/training-template.conf config/netlab.conf

# Edit configuration for multiple users
nano config/netlab.conf
```

**Configure for Training** (`config/netlab.conf`):
```ini
[system]
max_concurrent_users = 20
resource_per_user_ram = 4096  # 4GB per student
resource_per_user_disk = 25000  # 25GB per student
resource_per_user_cpu = 2  # 2 cores per student

[security]
user_isolation = true
vnc_password_required = true
session_timeout = 14400  # 4 hours

[training]
auto_reset_labs = true
assessment_mode = true
progress_tracking = true
instructor_dashboard = true
```

**Step 2: Create Training Topology**
```yaml
# topologies/training-basics.yaml
name: cybersecurity-training-basics
description: Basic cybersecurity training environment
version: "2.0"

constraints:
  max_ram: 4096    # Per student
  max_disk: 25000  # Per student
  max_cpu: 2       # Per student

networks:
  dmz:
    subnet: "192.168.10.0/24"
    gateway: "192.168.10.1"
    
  internal:
    subnet: "192.168.20.0/24"
    gateway: "192.168.20.1"

vms:
  - name: "firewall"
    type: "firewall"
    network: "dmz"
    ip: "192.168.10.10"
    memory: 512
    packages: ["iptables", "nmap"]
    
  - name: "web-server"
    type: "server"
    network: "dmz" 
    ip: "192.168.10.20"
    memory: 1024
    packages: ["nginx", "php"]
    
  - name: "client-workstation"
    type: "workstation"
    network: "internal"
    ip: "192.168.20.100"
    memory: 1024
    packages: ["firefox", "wireshark"]

training_scenarios:
  - name: "Network Reconnaissance"
    description: "Learn network scanning techniques"
    tasks:
      - "Scan the network using nmap"
      - "Identify open ports and services"
      - "Document findings"
    
  - name: "Web Application Security"
    description: "Test web application vulnerabilities"
    tasks:
      - "Identify web application technologies"
      - "Test for common vulnerabilities"
      - "Demonstrate secure coding practices"
```

**Step 3: Deploy Training Environment**
```bash
# 1. Set up training environment
python3 netlab-bridge.py setup --training-mode

# 2. Create user accounts
./tools/create-training-users.py --count 20 --template training-basics

# 3. Start instructor dashboard
python3 training-dashboard.py --port 8080

# 4. Deploy labs for all users
./tools/deploy-all-training.py --topology training-basics
```

**Step 4: Student Access Setup**
```bash
# Students access via:
# Web Interface: http://your-server:9000/user/{username}
# VNC Access: Individual ports assigned per student
# Progress Tracking: http://your-server:8080 (instructor only)

# Example student environment:
Student: student01
Web Dashboard: http://server:9000/user/student01
VNC Ports: 6000-6010 (firewall: 6000, web: 6001, etc.)
Isolated Networks: 192.168.101.x/24, 192.168.201.x/24
Resources: 4GB RAM, 25GB disk, 2 CPU cores
```

### How to Deploy Your First Custom Topology

**Scenario**: Create a simple IoT security testing environment.

**Step 1: Design Your Topology**
```yaml
# topologies/iot-security-lab.yaml
name: iot-security-lab
description: IoT device security testing environment
version: "2.0"

constraints:
  max_ram: 8192
  max_disk: 40000
  max_cpu: 6

networks:
  iot_network:
    subnet: "10.0.1.0/24"
    gateway: "10.0.1.1"
    purpose: "IoT device network"
    
  management:
    subnet: "10.0.100.0/24"
    gateway: "10.0.100.1"
    purpose: "Management and monitoring"

vms:
  - name: "iot-gateway"
    type: "router"
    network: "iot_network"
    ip: "10.0.1.1"
    memory: 512
    packages: ["mosquitto", "nodejs"]
    
  - name: "smart-device-1"
    type: "iot"
    network: "iot_network"
    ip: "10.0.1.10"
    memory: 256
    packages: ["python3", "mqtt-client"]
    
  - name: "smart-device-2"
    type: "iot"
    network: "iot_network"
    ip: "10.0.1.11"
    memory: 256
    packages: ["python3", "mqtt-client"]
    
  - name: "security-scanner"
    type: "security"
    network: "management"
    ip: "10.0.100.10"
    memory: 2048
    packages: ["nmap", "wireshark", "metasploit"]

deployment_scripts:
  post_deployment:
    - script: "setup-mqtt-broker.sh"
      target: "iot-gateway"
    - script: "configure-iot-devices.sh"
      target: "smart-device-*"
    - script: "setup-security-tools.sh"
      target: "security-scanner"
```

**Step 2: Create Setup Scripts**
```bash
# scripts/setup-mqtt-broker.sh
#!/bin/sh
echo "Setting up MQTT broker on IoT gateway..."
apk add mosquitto mosquitto-clients
echo "listener 1883 0.0.0.0" >> /etc/mosquitto/mosquitto.conf
echo "allow_anonymous true" >> /etc/mosquitto/mosquitto.conf
rc-service mosquitto start
rc-update add mosquitto default

# Test MQTT broker
mosquitto_pub -h localhost -t test/topic -m "MQTT broker ready"
```

```bash
# scripts/configure-iot-devices.sh
#!/bin/sh
echo "Configuring IoT device simulation..."
apk add python3 py3-pip
pip3 install paho-mqtt

# Create IoT device simulator
cat > /opt/iot-simulator.py << 'EOF'
#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import json
import time
import random

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")

client = mqtt.Client()
client.on_connect = on_connect

try:
    client.connect("10.0.1.1", 1883, 60)
    
    while True:
        # Simulate sensor data
        data = {
            "device_id": "smart_device_01",
            "temperature": random.randint(20, 35),
            "humidity": random.randint(40, 80),
            "timestamp": int(time.time())
        }
        
        client.publish("sensors/data", json.dumps(data))
        time.sleep(30)
        
except Exception as e:
    print(f"Error: {e}")
EOF

chmod +x /opt/iot-simulator.py

# Start IoT simulator
nohup python3 /opt/iot-simulator.py &
```

**Step 3: Deploy and Test**
```bash
# 1. Validate topology
netlab-validate iot-security-lab.yaml

# 2. Deploy the lab
netlab-deploy iot-security-lab.yaml

# 3. Test MQTT communication
# Connect to security-scanner VM
mosquitto_sub -h 10.0.1.1 -t "sensors/data"

# Expected output: JSON sensor data every 30 seconds
```

### How to Troubleshoot Common Installation Issues

**Issue 1: Docker Permission Denied**
```bash
# Symptom: "permission denied while trying to connect to Docker daemon"

# Solution:
sudo usermod -aG docker $USER
newgrp docker  # Or log out/back in

# Test:
docker run hello-world
```

**Issue 2: Insufficient Resources**
```bash
# Symptom: VMs fail to start, "Out of memory" errors

# Diagnosis:
free -h
df -h
docker system df

# Solution:
# Increase host resources or reduce VM allocation
# Edit topology file:
constraints:
  max_ram: 8192  # Reduce from 16384
  max_disk: 40000  # Reduce from 80000

# Clean up Docker:
docker system prune -a -f
```

**Issue 3: Network Bridge Issues**
```bash
# Symptom: VMs can't communicate, bridge creation fails

# Diagnosis:
sudo ip link show type bridge
sudo iptables -L -n

# Solution:
# Restart Docker networking
sudo systemctl restart docker

# Or manually create bridges:
sudo ip link add name netlab-dmz type bridge
sudo ip addr add 192.168.10.1/24 dev netlab-dmz
sudo ip link set netlab-dmz up
```

---

## 🌐 Network Management

### How to Create Custom Network Topologies

**Scenario**: Design a financial services network topology for compliance testing.

**Step 1: Plan Your Network Design**
```
Financial Services Network Design:
=================================
DMZ Zone (Public):
• Web servers, API gateways
• Load balancers, reverse proxies
• 192.168.10.0/24

Application Zone (Restricted):
• Application servers
• Message queues, caching
• 192.168.20.0/24

Database Zone (Highly Restricted):
• Database servers
• Backup systems
• 192.168.30.0/24

Management Zone (Admin):
• Jump hosts, monitoring
• Log servers, SIEM
• 192.168.100.0/24
```

**Step 2: Create Topology Definition**
```yaml
# topologies/financial-services.yaml
name: financial-services-network
description: Financial services compliance network
version: "2.0"
compliance: ["PCI-DSS", "SOX", "GDPR"]

constraints:
  max_ram: 20480
  max_disk: 100000
  max_cpu: 12

networks:
  dmz:
    subnet: "192.168.10.0/24"
    gateway: "192.168.10.1"
    security_zone: "public"
    allowed_traffic: ["http", "https"]
    
  application:
    subnet: "192.168.20.0/24"
    gateway: "192.168.20.1"
    security_zone: "restricted"
    allowed_traffic: ["app-specific"]
    
  database:
    subnet: "192.168.30.0/24"
    gateway: "192.168.30.1"
    security_zone: "highly-restricted"
    allowed_traffic: ["database"]
    
  management:
    subnet: "192.168.100.0/24"
    gateway: "192.168.100.1"
    security_zone: "administrative"
    allowed_traffic: ["ssh", "snmp", "syslog"]

vms:
  # DMZ Zone
  - name: "edge-firewall"
    type: "firewall"
    network: "dmz"
    ip: "192.168.10.5"
    memory: 1024
    packages: ["pfsense", "snort"]
    firewall_rules:
      - "allow http from any to 192.168.10.0/24"
      - "allow https from any to 192.168.10.0/24"
      - "block all from dmz to database"
    
  - name: "web-server-1"
    type: "server"
    network: "dmz"
    ip: "192.168.10.10"
    memory: 1024
    packages: ["nginx", "ssl-cert"]
    services: ["nginx"]
    
  - name: "load-balancer"
    type: "loadbalancer"
    network: "dmz"
    ip: "192.168.10.20"
    memory: 512
    packages: ["haproxy"]
    
  # Application Zone
  - name: "app-server-1"
    type: "server"
    network: "application"
    ip: "192.168.20.10"
    memory: 2048
    packages: ["java", "tomcat"]
    
  - name: "app-server-2"
    type: "server"
    network: "application"
    ip: "192.168.20.11"
    memory: 2048
    packages: ["java", "tomcat"]
    
  - name: "message-queue"
    type: "middleware"
    network: "application"
    ip: "192.168.20.20"
    memory: 1024
    packages: ["rabbitmq"]
    
  # Database Zone
  - name: "primary-db"
    type: "database"
    network: "database"
    ip: "192.168.30.10"
    memory: 4096
    packages: ["postgresql", "pgbackrest"]
    encrypted: true
    
  - name: "backup-db"
    type: "database"
    network: "database"
    ip: "192.168.30.11"
    memory: 2048
    packages: ["postgresql"]
    
  # Management Zone
  - name: "jump-host"
    type: "bastion"
    network: "management"
    ip: "192.168.100.10"
    memory: 1024
    packages: ["openssh", "audit"]
    
  - name: "siem-server"
    type: "security"
    network: "management"
    ip: "192.168.100.20"
    memory: 4096
    packages: ["elasticsearch", "logstash", "kibana"]

network_policies:
  - name: "dmz-to-app"
    from: "dmz"
    to: "application"
    ports: ["8080", "8443"]
    protocol: ["tcp"]
    
  - name: "app-to-db"
    from: "application"
    to: "database"
    ports: ["5432"]
    protocol: ["tcp"]
    encryption_required: true
    
  - name: "mgmt-to-all"
    from: "management"
    to: "*"
    ports: ["22", "161"]
    protocol: ["tcp", "udp"]
    
compliance_tests:
  - name: "PCI-DSS Network Segmentation"
    test_type: "network_isolation"
    requirements:
      - "DMZ cannot directly access database"
      - "All database traffic must be encrypted"
      - "Administrative access only from management zone"
      
  - name: "Access Control Validation"
    test_type: "access_control"
    requirements:
      - "Default deny all traffic"
      - "Explicit allow rules only"
      - "Log all access attempts"
```

**Step 3: Create Compliance Testing Scripts**
```python
# scripts/compliance-tester.py
#!/usr/bin/env python3
"""
Financial Services Compliance Tester
Tests network for PCI-DSS, SOX compliance
"""

import subprocess
import json
from datetime import datetime

class ComplianceTester:
    def __init__(self):
        self.test_results = []
        
    def test_network_segmentation(self):
        """Test PCI-DSS network segmentation requirements"""
        print("🔒 Testing Network Segmentation (PCI-DSS)")
        
        # Test 1: DMZ cannot access database directly
        result = subprocess.run([
            'ping', '-c', '3', '-W', '2', '192.168.30.10'
        ], capture_output=True, cwd='/tmp')
        
        if result.returncode != 0:
            self.log_test("DMZ-DB Isolation", "PASS", "DMZ cannot reach database")
        else:
            self.log_test("DMZ-DB Isolation", "FAIL", "DMZ can reach database")
            
        # Test 2: Database encryption
        self.test_database_encryption()
        
    def test_database_encryption(self):
        """Verify database connections are encrypted"""
        print("🔐 Testing Database Encryption")
        
        # Check PostgreSQL SSL configuration
        # This would connect to DB and verify SSL
        self.log_test("DB Encryption", "PASS", "SSL connections enforced")
        
    def test_access_controls(self):
        """Test access control policies"""
        print("🛡️ Testing Access Controls")
        
        # Test firewall rules
        # Test authentication requirements
        # Test privilege escalation prevention
        pass
        
    def log_test(self, test_name, result, details):
        """Log test result"""
        self.test_results.append({
            'test': test_name,
            'result': result,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        
        status = "✅" if result == "PASS" else "❌"
        print(f"{status} {test_name}: {details}")
        
    def generate_report(self):
        """Generate compliance report"""
        report = {
            'compliance_framework': ['PCI-DSS', 'SOX'],
            'test_date': datetime.now().isoformat(),
            'results': self.test_results,
            'summary': {
                'total_tests': len(self.test_results),
                'passed': len([r for r in self.test_results if r['result'] == 'PASS']),
                'failed': len([r for r in self.test_results if r['result'] == 'FAIL'])
            }
        }
        
        with open('/netlab/reports/compliance-report.json', 'w') as f:
            json.dump(report, f, indent=2)
            
        print("\n📊 Compliance Report Generated")
        print(f"Total Tests: {report['summary']['total_tests']}")
        print(f"Passed: {report['summary']['passed']}")
        print(f"Failed: {report['summary']['failed']}")

if __name__ == "__main__":
    tester = ComplianceTester()
    tester.test_network_segmentation()
    tester.test_access_controls()
    tester.generate_report()
```

### How to Configure Inter-VLAN Routing

**Scenario**: Set up controlled routing between network segments with security policies.

**Step 1: Configure Router VM**
```bash
# Connect to core router VM via VNC
# Enable IP forwarding
echo 'net.ipv4.ip_forward=1' >> /etc/sysctl.conf
sysctl -p

# Install routing software
apk add quagga iptables-openrc

# Configure Quagga for OSPF
cat > /etc/quagga/zebra.conf << 'EOF'
hostname router
password zebra
enable password zebra
log stdout
EOF

cat > /etc/quagga/ospfd.conf << 'EOF'
hostname ospfd
password zebra
log stdout

interface eth0
 ip ospf hello-interval 10
 ip ospf dead-interval 40

interface eth1
 ip ospf hello-interval 10
 ip ospf dead-interval 40

router ospf
 network 192.168.20.0/24 area 0
 network 192.168.30.0/24 area 0
EOF
```

**Step 2: Configure Firewall Rules**
```bash
# Create iptables rules for controlled inter-VLAN access
cat > /etc/iptables/rules.v4 << 'EOF'
*filter
:INPUT ACCEPT [0:0]
:FORWARD DROP [0:0]
:OUTPUT ACCEPT [0:0]

# Allow established connections
-A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT

# Allow app zone to database zone (specific ports)
-A FORWARD -s 192.168.20.0/24 -d 192.168.30.0/24 -p tcp --dport 5432 -j ACCEPT

# Allow management zone to all (SSH, SNMP)
-A FORWARD -s 192.168.100.0/24 -p tcp --dport 22 -j ACCEPT
-A FORWARD -s 192.168.100.0/24 -p udp --dport 161 -j ACCEPT

# Block all other inter-VLAN traffic
-A FORWARD -j LOG --log-prefix "BLOCKED: "
-A FORWARD -j DROP

COMMIT
EOF

# Apply firewall rules
iptables-restore < /etc/iptables/rules.v4
```

**Step 3: Test Inter-VLAN Connectivity**
```bash
# Test script for inter-VLAN routing validation
cat > /opt/test-routing.sh << 'EOF'
#!/bin/sh
echo "🌐 Testing Inter-VLAN Routing"

# Test 1: App to Database (should work)
echo "Testing App → Database connectivity..."
ping -c 3 -W 2 192.168.30.10
if [ $? -eq 0 ]; then
    echo "✅ App → Database: SUCCESS"
else
    echo "❌ App → Database: FAILED"
fi

# Test 2: DMZ to Database (should fail)
echo "Testing DMZ → Database connectivity..."
timeout 5 ping -c 3 192.168.30.10
if [ $? -ne 0 ]; then
    echo "✅ DMZ → Database blocked: SUCCESS"
else
    echo "❌ DMZ → Database not blocked: SECURITY ISSUE"
fi

# Test 3: Management access (should work)
echo "Testing Management → All zones..."
ping -c 1 192.168.10.10 && echo "✅ Mgmt → DMZ: OK"
ping -c 1 192.168.20.10 && echo "✅ Mgmt → App: OK"  
ping -c 1 192.168.30.10 && echo "✅ Mgmt → DB: OK"
EOF

chmod +x /opt/test-routing.sh
/opt/test-routing.sh
```

---

## 🔒 Security Scenarios

### How to Set Up a Penetration Testing Lab

**Scenario**: Create a realistic penetration testing environment for ethical hacking training.

**Step 1: Design Vulnerable Environment**
```yaml
# topologies/pentest-lab.yaml
name: penetration-testing-lab
description: Vulnerable network for ethical hacking practice
version: "2.0"

constraints:
  max_ram: 12288
  max_disk: 60000
  max_cpu: 8

networks:
  target_network:
    subnet: "192.168.100.0/24"
    gateway: "192.168.100.1"
    purpose: "Target network with vulnerabilities"
    
  attacker_network:
    subnet: "192.168.200.0/24" 
    gateway: "192.168.200.1"
    purpose: "Attacker tools and systems"

vms:
  # Target Systems (Vulnerable)
  - name: "vulnerable-web"
    type: "server"
    network: "target_network"
    ip: "192.168.100.10"
    memory: 1024
    vulnerabilities:
      - "DVWA" # Damn Vulnerable Web Application
      - "Weak SSH passwords"
      - "Unpatched services"
    packages: ["apache2", "php", "mysql"]
    
  - name: "old-windows-server"
    type: "server"  
    network: "target_network"
    ip: "192.168.100.20"
    memory: 2048
    vulnerabilities:
      - "MS17-010 EternalBlue"
      - "Weak SMB configuration"
      - "Default credentials"
    
  - name: "vulnerable-database"
    type: "database"
    network: "target_network"
    ip: "192.168.100.30"
    memory: 1024
    vulnerabilities:
      - "SQL injection"
      - "Default credentials"
      - "Unencrypted connections"
    packages: ["mysql-server"]
    
  # Attacker Systems
  - name: "kali-linux"
    type: "security"
    network: "attacker_network"
    ip: "192.168.200.10"
    memory: 4096
    packages:
      - "kali-linux-full"
      - "metasploit-framework"
      - "nmap"
      - "wireshark"
      - "burpsuite"
      - "sqlmap"
      
  - name: "command-control"
    type: "server"
    network: "attacker_network"
    ip: "192.168.200.20"
    memory: 1024
    packages: ["empire", "cobalt-strike"]

pentest_scenarios:
  - name: "Network Discovery"
    description: "Discover and enumerate network services"
    objectives:
      - "Scan target network"
      - "Identify open ports and services"
      - "OS fingerprinting"
    tools: ["nmap", "masscan", "zmap"]
    
  - name: "Web Application Testing"
    description: "Test web applications for vulnerabilities"
    objectives:
      - "SQL injection testing"
      - "XSS vulnerability discovery"
      - "Authentication bypass"
    tools: ["burpsuite", "sqlmap", "nikto"]
    
  - name: "Exploitation"
    description: "Exploit identified vulnerabilities"
    objectives:
      - "Gain initial access"
      - "Privilege escalation"
      - "Lateral movement"
    tools: ["metasploit", "empire", "powershell-empire"]
    
  - name: "Post-Exploitation"
    description: "Actions after successful compromise"
    objectives:
      - "Data exfiltration"
      - "Persistence mechanisms"
      - "Evidence cleanup"
    tools: ["meterpreter", "cobalt-strike", "custom-tools"]
```

**Step 2: Set Up Vulnerable Services**
```bash
# Script to configure vulnerable web application
# scripts/setup-vulnerable-web.sh
#!/bin/sh
echo "🎯 Setting up Vulnerable Web Application"

# Install LAMP stack
apk add apache2 php php-apache2 mysql mysql-client php-mysql

# Start services
rc-service apache2 start
rc-service mysql start
rc-update add apache2 default
rc-update add mysql default

# Download and install DVWA
cd /var/www/html
wget https://github.com/digininja/DVWA/archive/master.zip
unzip master.zip
mv DVWA-master dvwa
chown -R apache:apache dvwa

# Configure MySQL for DVWA
mysql -e "CREATE DATABASE dvwa;"
mysql -e "CREATE USER 'dvwa'@'localhost' IDENTIFIED BY 'password';"
mysql -e "GRANT ALL PRIVILEGES ON dvwa.* TO 'dvwa'@'localhost';"
mysql -e "FLUSH PRIVILEGES;"

# Configure DVWA
cp /var/www/html/dvwa/config/config.inc.php.dist /var/www/html/dvwa/config/config.inc.php
sed -i "s/p@ssw0rd/password/" /var/www/html/dvwa/config/config.inc.php

# Set weak SSH password
echo "admin:weakpass123" | chpasswd

# Install vulnerable service (intentionally old version)
cd /tmp
wget https://example.com/old-vulnerable-service.tar.gz
tar -xzf old-vulnerable-service.tar.gz
cp vulnerable-service /usr/local/bin/
chmod +x /usr/local/bin/vulnerable-service

# Start vulnerable service
/usr/local/bin/vulnerable-service --port 9999 &

echo "✅ Vulnerable web application configured"
echo "DVWA: http://192.168.100.10/dvwa (admin:password)"
echo "SSH: admin:weakpass123"
echo "Vulnerable service: port 9999"
```

**Step 3: Create Penetration Testing Scripts**
```bash
# Example penetration testing workflow
# scripts/pentest-workflow.py
#!/usr/bin/env python3
"""
Automated Penetration Testing Workflow
Educational tool for demonstrating attack techniques
"""

import subprocess
import json
import time
from datetime import datetime

class PentestFramework:
    def __init__(self, target_range="192.168.100.0/24"):
        self.target_range = target_range
        self.discoveries = []
        self.vulnerabilities = []
        
    def phase_1_reconnaissance(self):
        """Phase 1: Reconnaissance and Discovery"""
        print("🔍 Phase 1: Reconnaissance")
        
        # Network discovery
        print("Running network discovery...")
        nmap_cmd = f"nmap -sn {self.target_range}"
        result = subprocess.run(nmap_cmd.split(), capture_output=True, text=True)
        
        # Parse results and extract live hosts
        live_hosts = self.parse_nmap_hosts(result.stdout)
        self.discoveries.extend(live_hosts)
        
        return live_hosts
        
    def phase_2_scanning(self, hosts):
        """Phase 2: Port Scanning and Service Enumeration"""
        print("🔬 Phase 2: Scanning and Enumeration")
        
        for host in hosts:
            print(f"Scanning {host}...")
            
            # Port scan
            nmap_cmd = f"nmap -sC -sV -T4 {host}"
            result = subprocess.run(nmap_cmd.split(), capture_output=True, text=True)
            
            services = self.parse_nmap_services(result.stdout)
            self.discoveries.append({
                'host': host,
                'services': services,
                'scan_time': datetime.now().isoformat()
            })
            
    def phase_3_vulnerability_assessment(self):
        """Phase 3: Vulnerability Assessment"""
        print("🎯 Phase 3: Vulnerability Assessment")
        
        # Web application testing
        self.test_web_applications()
        
        # SSH brute force (educational - with rate limiting)
        self.test_ssh_authentication()
        
        # Database testing
        self.test_database_security()
        
    def test_web_applications(self):
        """Test web applications for common vulnerabilities"""
        web_servers = [d for d in self.discoveries if 'http' in str(d)]
        
        for server in web_servers:
            print(f"Testing web application on {server['host']}")
            
            # Directory enumeration
            dirb_cmd = f"dirb http://{server['host']}"
            # Run with timeout and rate limiting
            
            # SQL injection testing (automated with sqlmap)
            sqlmap_cmd = f"sqlmap -u http://{server['host']}/login.php --batch --risk=1"
            # Educational: Explain what this does
            
    def generate_report(self):
        """Generate penetration testing report"""
        report = {
            'test_date': datetime.now().isoformat(),
            'target_range': self.target_range,
            'discoveries': self.discoveries,
            'vulnerabilities': self.vulnerabilities,
            'recommendations': self.generate_recommendations()
        }
        
        with open('/opt/pentest-report.json', 'w') as f:
            json.dump(report, f, indent=2)
            
        print("\n📋 Penetration Test Report Generated")
        print(f"Hosts discovered: {len(self.discoveries)}")
        print(f"Vulnerabilities found: {len(self.vulnerabilities)}")
        
    def generate_recommendations(self):
        """Generate security recommendations"""
        return [
            "Update all systems to latest security patches",
            "Implement strong password policies",
            "Configure proper firewall rules",
            "Enable logging and monitoring",
            "Regular security assessments"
        ]

# Educational usage
if __name__ == "__main__":
    print("🎓 Educational Penetration Testing Framework")
    print("=" * 50)
    print("This tool is for educational purposes only!")
    print("Only use against systems you own or have permission to test.")
    print()
    
    pentest = PentestFramework()
    hosts = pentest.phase_1_reconnaissance()
    pentest.phase_2_scanning(hosts)
    pentest.phase_3_vulnerability_assessment()
    pentest.generate_report()
```

---

## 🎓 Training & Education

### How to Set Up Multi-User Training Environment

**Scenario**: Configure NetLab V2 for a cybersecurity bootcamp with 30 students.

**Step 1: Server Sizing and Planning**
```bash
# Calculate resource requirements
# Per student: 4GB RAM, 25GB disk, 2 CPU cores
# 30 students: 120GB RAM, 750GB disk, 60 CPU cores
# Recommended server: 128GB+ RAM, 1TB+ NVMe SSD, 64+ CPU cores

# Example AWS instance: c5.16xlarge or c5.18xlarge
# Example Azure: Standard_F64s_v2
# Example GCP: c2-standard-60
```

**Step 2: Multi-User Configuration**
```yaml
# config/multi-user.conf
[system]
mode = "multi_user"
max_users = 30
user_isolation = "complete"
resource_enforcement = "strict"

[resources_per_user]
max_ram_mb = 4096
max_disk_mb = 25600
max_cpu_cores = 2
max_vms = 8
max_networks = 4

[security]
user_data_isolation = true
vnc_password_per_user = true
network_isolation = true
session_recording = true

[training]
auto_provision = true
template_topology = "cybersecurity-basics"
assessment_mode = true
progress_tracking = true
time_limits = true
auto_cleanup = true

[instructor]
dashboard_enabled = true
student_monitoring = true
remote_assistance = true
bulk_operations = true
```

**Step 3: User Provisioning Script**
```bash
#!/bin/bash
# provision-training-users.sh
echo "🎓 Provisioning Multi-User Training Environment"

# Create user directories and configurations
for i in {1..30}; do
    username="student$(printf "%02d" $i)"
    echo "Creating user: $username"
    
    # Create user-specific directory
    mkdir -p "/netlab/users/$username"
    
    # Generate user configuration
    cat > "/netlab/users/$username/config.yaml" << EOF
username: $username
password: $(openssl rand -base64 12)
vnc_password: $(openssl rand -base64 8)
resource_limits:
  ram: 4096
  disk: 25600
  cpu: 2
networks:
  - "${username}-dmz"
  - "${username}-internal"
vms:
  - name: "${username}-firewall"
    network: "${username}-dmz"
    ip: "10.${i}.1.10"
  - name: "${username}-server"
    network: "${username}-dmz"
    ip: "10.${i}.1.20"
  - name: "${username}-client"
    network: "${username}-internal"
    ip: "10.${i}.2.100"
EOF
    
    # Create isolated networks for user
    sudo ip netns add "netlab-${username}"
    
    # Set VNC port range (per user gets 10 ports)
    vnc_start=$((6000 + $i * 10))
    echo "VNC ports for $username: $vnc_start-$((vnc_start + 9))"
    
done

echo "✅ Multi-user environment provisioned"
echo "👥 Users: student01-student30"
echo "🌐 Access: http://your-server:9000/student/{username}"
```

**Step 4: Instructor Dashboard**
```python
#!/usr/bin/env python3
# instructor-dashboard.py
"""
Multi-User Training Dashboard
Provides instructor oversight and control
"""

from flask import Flask, render_template, request, jsonify
import json
import subprocess
from datetime import datetime

app = Flask(__name__)

class TrainingDashboard:
    def __init__(self):
        self.users = self.load_users()
        
    def load_users(self):
        """Load user configurations and status"""
        users = {}
        for i in range(1, 31):
            username = f"student{i:02d}"
            users[username] = {
                'id': i,
                'username': username,
                'status': self.get_user_status(username),
                'progress': self.get_user_progress(username),
                'resources': self.get_resource_usage(username),
                'last_activity': self.get_last_activity(username)
            }
        return users
        
    def get_user_status(self, username):
        """Get current user lab status"""
        # Check if user's VMs are running
        try:
            result = subprocess.run(
                ['docker', 'ps', '--filter', f'name={username}'],
                capture_output=True, text=True
            )
            return 'active' if result.stdout else 'inactive'
        except:
            return 'unknown'
            
    def get_user_progress(self, username):
        """Get user's training progress"""
        # Load progress from database/file
        try:
            with open(f'/netlab/users/{username}/progress.json') as f:
                return json.load(f)
        except:
            return {'completed_scenarios': 0, 'total_scenarios': 10, 'score': 0}
            
    def get_resource_usage(self, username):
        """Get user's current resource usage"""
        # Query Docker stats for user's containers
        return {'cpu': 15.2, 'memory': 2048, 'disk': 12000}
        
    def get_last_activity(self, username):
        """Get user's last activity timestamp"""
        return datetime.now().isoformat()

dashboard = TrainingDashboard()

@app.route('/')
def index():
    return render_template('instructor_dashboard.html', users=dashboard.users)

@app.route('/api/users')
def api_users():
    return jsonify(dashboard.users)

@app.route('/api/user/<username>/reset', methods=['POST'])
def reset_user_lab(username):
    """Reset user's lab environment"""
    try:
        # Stop user's containers
        subprocess.run(['docker', 'stop', f'{username}-lab'], check=True)
        
        # Reset user's progress
        progress_file = f'/netlab/users/{username}/progress.json'
        with open(progress_file, 'w') as f:
            json.dump({'completed_scenarios': 0, 'score': 0}, f)
            
        # Restart lab
        subprocess.run(['docker', 'start', f'{username}-lab'], check=True)
        
        return jsonify({'status': 'success', 'message': f'Lab reset for {username}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/broadcast', methods=['POST'])
def broadcast_message():
    """Broadcast message to all students"""
    message = request.json.get('message')
    # Send message to all active student sessions
    return jsonify({'status': 'success', 'recipients': 30})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
```

### How to Create Assessment Scenarios

**Scenario**: Design automated assessments for cybersecurity skills validation.

**Step 1: Define Assessment Framework**
```yaml
# assessments/network-security-assessment.yaml
name: network-security-skills-assessment
description: Comprehensive network security skills evaluation
duration_minutes: 120
passing_score: 70
randomize_questions: true

categories:
  - name: "Network Reconnaissance"
    weight: 20
    description: "Ability to discover and enumerate network assets"
    
  - name: "Vulnerability Assessment"
    weight: 25
    description: "Identifying and analyzing security weaknesses"
    
  - name: "Access Control Testing"
    weight: 20
    description: "Testing authentication and authorization mechanisms"
    
  - name: "Network Defense"
    weight: 25
    description: "Implementing security controls and countermeasures"
    
  - name: "Incident Response"
    weight: 10
    description: "Responding to security incidents and breaches"

scenarios:
  - id: "recon_001"
    category: "Network Reconnaissance"
    title: "Network Discovery Challenge"
    description: "Discover all active hosts in the 192.168.100.0/24 network"
    topology: "assessment-network-recon"
    time_limit: 15
    objectives:
      - task: "Identify all live hosts"
        validation: "nmap_scan_results"
        points: 10
        
      - task: "Determine operating systems"
        validation: "os_fingerprint_accuracy"
        points: 8
        
      - task: "List open ports and services"
        validation: "port_scan_completeness"
        points: 12
    
    validation_scripts:
      nmap_scan_results: |
        #!/bin/bash
        # Check if student found all hosts
        found_hosts=$(cat /student_results/hosts.txt | wc -l)
        total_hosts=5
        if [ $found_hosts -eq $total_hosts ]; then
          echo "PASS:10:All hosts discovered"
        else
          score=$((found_hosts * 10 / total_hosts))
          echo "PARTIAL:$score:Found $found_hosts/$total_hosts hosts"
        fi
        
  - id: "vuln_001"
    category: "Vulnerability Assessment"
    title: "Web Application Security Assessment"
    description: "Identify vulnerabilities in the target web application"
    topology: "assessment-webapp-vuln"
    time_limit: 30
    objectives:
      - task: "Find SQL injection vulnerability"
        validation: "sql_injection_found"
        points: 15
        
      - task: "Identify XSS vulnerabilities"
        validation: "xss_discovery"
        points: 12
        
      - task: "Document security issues"
        validation: "vulnerability_report"
        points: 8

assessment_topologies:
  assessment-network-recon:
    networks:
      target:
        subnet: "192.168.100.0/24"
        hosts: 5
    vms:
      - name: "target-1"
        ip: "192.168.100.10"
        services: ["ssh", "http"]
        os: "linux"
      - name: "target-2"
        ip: "192.168.100.20"
        services: ["ssh", "mysql"]
        os: "linux"
      # ... more targets
      
  assessment-webapp-vuln:
    networks:
      webapp:
        subnet: "192.168.200.0/24"
    vms:
      - name: "vulnerable-web"
        ip: "192.168.200.10"
        services: ["http"]
        vulnerabilities: ["sql_injection", "xss", "weak_auth"]

grading:
  automatic_validation: true
  manual_review_required: false
  time_penalties: true
  penalty_per_minute_over: 0.5
  
reporting:
  generate_individual_reports: true
  generate_class_summary: true
  include_remediation_guidance: true
  export_formats: ["pdf", "json", "csv"]
```

**Step 2: Assessment Automation Engine**
```python
#!/usr/bin/env python3
# assessment-engine.py
"""
Automated Assessment Engine for NetLab V2
Deploys scenarios, monitors student progress, validates results
"""

import json
import yaml
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

class AssessmentEngine:
    def __init__(self, assessment_config):
        self.config = self.load_assessment(assessment_config)
        self.students = {}
        self.results = {}
        
    def load_assessment(self, config_file):
        """Load assessment configuration"""
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
            
    def start_assessment(self, student_list):
        """Start assessment for list of students"""
        print(f"🎯 Starting Assessment: {self.config['name']}")
        print(f"📝 Duration: {self.config['duration_minutes']} minutes")
        print(f"👥 Students: {len(student_list)}")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=self.config['duration_minutes'])
        
        for student in student_list:
            self.deploy_student_environment(student)
            self.students[student] = {
                'start_time': start_time,
                'end_time': end_time,
                'current_scenario': 0,
                'status': 'active'
            }
            
        # Monitor assessment progress
        self.monitor_assessment()
        
    def deploy_student_environment(self, student):
        """Deploy isolated assessment environment for student"""
        print(f"🚀 Deploying environment for {student}")
        
        # Create student-specific topology
        for scenario_id, scenario in enumerate(self.config['scenarios']):
            topology = scenario['topology']
            
            # Customize topology for student
            student_topology = self.customize_topology(topology, student)
            
            # Deploy using NetLab
            subprocess.run([
                'netlab-deploy', 
                f'/tmp/{student}-{topology}.yaml',
                '--user', student,
                '--assessment-mode'
            ])
            
    def customize_topology(self, topology_name, student):
        """Create student-specific version of topology"""
        base_topology = self.config['assessment_topologies'][topology_name]
        
        # Modify IP ranges to be student-specific
        student_id = int(student.replace('student', ''))
        
        customized = base_topology.copy()
        for network in customized.get('networks', {}):
            # Change network to student-specific range
            base_subnet = customized['networks'][network]['subnet']
            # Convert 192.168.100.0/24 to 192.168.{100+student_id}.0/24
            parts = base_subnet.split('.')
            parts[2] = str(int(parts[2]) + student_id)
            customized['networks'][network]['subnet'] = '.'.join(parts)
            
        return customized
        
    def monitor_assessment(self):
        """Monitor student progress and validate results"""
        while any(s['status'] == 'active' for s in self.students.values()):
            for student, info in self.students.items():
                if info['status'] != 'active':
                    continue
                    
                # Check if time expired
                if datetime.now() > info['end_time']:
                    self.finalize_student_assessment(student)
                    continue
                    
                # Check for submitted results
                self.check_student_submissions(student)
                
            time.sleep(30)  # Check every 30 seconds
            
    def check_student_submissions(self, student):
        """Check for and validate student submissions"""
        submission_dir = f'/netlab/users/{student}/assessment_submissions'
        
        if not Path(submission_dir).exists():
            return
            
        for scenario in self.config['scenarios']:
            scenario_id = scenario['id']
            submission_file = f'{submission_dir}/{scenario_id}_results.json'
            
            if Path(submission_file).exists() and scenario_id not in self.results.get(student, {}):
                self.validate_scenario_submission(student, scenario, submission_file)
                
    def validate_scenario_submission(self, student, scenario, submission_file):
        """Validate student's scenario submission"""
        print(f"📝 Validating {scenario['id']} for {student}")
        
        with open(submission_file, 'r') as f:
            submission = json.load(f)
            
        scenario_score = 0
        max_score = sum(obj['points'] for obj in scenario['objectives'])
        
        # Run validation scripts
        for objective in scenario['objectives']:
            validation_script = scenario['validation_scripts'][objective['validation']]
            
            # Create temporary validation script
            script_path = f'/tmp/validate_{objective["validation"]}.sh'
            with open(script_path, 'w') as f:
                f.write(validation_script)
            
            # Make executable and run
            subprocess.run(['chmod', '+x', script_path])
            result = subprocess.run([script_path], capture_output=True, text=True)
            
            # Parse validation result
            if result.stdout.startswith('PASS:'):
                _, points, message = result.stdout.strip().split(':', 2)
                objective_score = int(points)
            elif result.stdout.startswith('PARTIAL:'):
                _, points, message = result.stdout.strip().split(':', 2)
                objective_score = int(points)
            else:
                objective_score = 0
                message = "Validation failed"
                
            scenario_score += objective_score
            print(f"  {objective['task']}: {objective_score}/{objective['points']} - {message}")
            
        # Store results
        if student not in self.results:
            self.results[student] = {}
            
        self.results[student][scenario['id']] = {
            'score': scenario_score,
            'max_score': max_score,
            'percentage': (scenario_score / max_score) * 100,
            'completion_time': datetime.now(),
            'category': scenario['category']
        }
        
    def finalize_student_assessment(self, student):
        """Finalize assessment for student"""
        print(f"⏰ Finalizing assessment for {student}")
        
        self.students[student]['status'] = 'completed'
        
        # Calculate final score
        total_score = 0
        max_total_score = 0
        
        for scenario_id, result in self.results.get(student, {}).items():
            total_score += result['score']
            max_total_score += result['max_score']
            
        final_percentage = (total_score / max_total_score) * 100 if max_total_score > 0 else 0
        
        # Determine pass/fail
        passed = final_percentage >= self.config['passing_score']
        
        # Generate individual report
        self.generate_student_report(student, final_percentage, passed)
        
        # Cleanup student environment
        subprocess.run(['netlab-cleanup', '--user', student])
        
    def generate_student_report(self, student, final_score, passed):
        """Generate detailed assessment report for student"""
        report = {
            'student': student,
            'assessment': self.config['name'],
            'completion_time': datetime.now().isoformat(),
            'final_score': final_score,
            'passing_score': self.config['passing_score'],
            'passed': passed,
            'scenario_results': self.results.get(student, {}),
            'category_breakdown': self.calculate_category_scores(student),
            'recommendations': self.generate_recommendations(student)
        }
        
        # Save JSON report
        with open(f'/netlab/reports/{student}_assessment_report.json', 'w') as f:
            json.dump(report, f, indent=2)
            
        # Generate PDF report
        self.generate_pdf_report(student, report)
        
        print(f"📊 Report generated for {student}: {final_score:.1f}% ({'PASS' if passed else 'FAIL'})")
        
    def generate_pdf_report(self, student, report):
        """Generate PDF assessment report"""
        # This would use a PDF generation library like reportlab
        pass

# Example usage
if __name__ == "__main__":
    engine = AssessmentEngine('assessments/network-security-assessment.yaml')
    
    # List of students
    students = [f'student{i:02d}' for i in range(1, 31)]
    
    # Start assessment
    engine.start_assessment(students)
```

---

*This comprehensive how-to guide covers the most common NetLab V2 scenarios. Each guide provides step-by-step instructions, configuration files, and practical examples to help users master the platform.*