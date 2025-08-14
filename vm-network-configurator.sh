#!/bin/bash
# NetLab V2 - VM Network Configuration Script
# Configures IP addresses and network settings for all VMs

echo "🔧 NetLab V2 - VM Network Configuration"
echo "======================================"

# VM Network Configuration
declare -A VMs=(
    ["edge-firewall"]="192.168.10.10/24:192.168.10.1:netlab-dmz:5920"
    ["web-server-1"]="192.168.10.20/24:192.168.10.1:netlab-dmz:5921"
    ["core-router-1"]="192.168.20.2/24:192.168.20.1:netlab-corp:5922"
    ["database-server"]="192.168.20.10/24:192.168.20.1:netlab-corp:5923"
    ["siem-server"]="192.168.40.10/24:192.168.40.1:netlab-sec:5924"
    ["ids-ips"]="192.168.40.11/24:192.168.40.1:netlab-sec:5925"
)

# Create VM network configuration files
create_vm_network_config() {
    local vm_name=$1
    local ip_config=$2
    
    IFS=':' read -r ip_cidr gateway bridge vnc_port <<< "$ip_config"
    IFS='/' read -r ip_addr netmask <<< "$ip_cidr"
    
    # Create Alpine Linux network configuration
    cat > "/tmp/${vm_name}-network-config.sh" << EOF
#!/bin/sh
# Network configuration for $vm_name
echo "Configuring network for $vm_name..."

# Configure network interface
cat > /etc/network/interfaces << 'NETEOF'
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet static
    address $ip_addr
    netmask 255.255.255.0
    gateway $gateway
    dns-nameservers 8.8.8.8 8.8.4.4
NETEOF

# Restart networking
/etc/init.d/networking restart

# Set hostname
echo "$vm_name" > /etc/hostname
hostname $vm_name

# Add hosts entries
cat >> /etc/hosts << 'HOSTSEOF'
# NetLab V2 Enterprise Network
192.168.10.1    dmz-gateway
192.168.10.10   edge-firewall
192.168.10.20   web-server-1
192.168.20.1    corporate-gateway
192.168.20.2    core-router-1
192.168.20.10   database-server
192.168.40.1    security-gateway
192.168.40.10   siem-server
192.168.40.11   ids-ips
HOSTSEOF

# Enable IP forwarding for routers and firewalls
if [[ "$vm_name" == *"router"* ]] || [[ "$vm_name" == *"firewall"* ]]; then
    echo 'net.ipv4.ip_forward=1' >> /etc/sysctl.conf
    sysctl -p
fi

# Install basic network tools
apk update
apk add curl wget tcpdump nmap-nping

echo "Network configuration complete for $vm_name"
echo "IP Address: $ip_addr/$netmask"
echo "Gateway: $gateway"
echo "Bridge: $bridge"

# Test connectivity
ping -c 3 $gateway && echo "Gateway reachable" || echo "Gateway unreachable"
EOF

    chmod +x "/tmp/${vm_name}-network-config.sh"
}

# Create network configuration ISO for VM
create_config_iso() {
    local vm_name=$1
    local config_script="/tmp/${vm_name}-network-config.sh"
    local iso_file="/netlab/isos/${vm_name}-config.iso"
    
    # Create temporary directory
    mkdir -p "/tmp/${vm_name}-iso"
    cp "$config_script" "/tmp/${vm_name}-iso/network-config.sh"
    
    # Create info file
    cat > "/tmp/${vm_name}-iso/README.txt" << EOF
NetLab V2 - VM Network Configuration
====================================
VM: $vm_name
Generated: $(date)

To configure network:
1. Mount this ISO in the VM
2. Run: sh /media/cdrom/network-config.sh
EOF
    
    # Create ISO
    genisoimage -o "$iso_file" -V "NETLAB-CONFIG" -r -J "/tmp/${vm_name}-iso/"
    
    # Cleanup
    rm -rf "/tmp/${vm_name}-iso"
    
    echo "Configuration ISO created: $iso_file"
}

echo ""
echo "🌐 Verifying Bridge Network Status:"
echo "===================================="
sudo ip link show type bridge | grep netlab
echo ""

echo "📊 Bridge IP Configuration:"
echo "==========================="
sudo ip addr show netlab-dmz 2>/dev/null | grep inet || echo "DMZ bridge not configured"
sudo ip addr show netlab-corp 2>/dev/null | grep inet || echo "Corporate bridge not configured"  
sudo ip addr show netlab-sec 2>/dev/null | grep inet || echo "Security bridge not configured"

echo ""
echo "🔧 Creating VM Network Configurations:"
echo "======================================"

# Create configuration files for each VM
for vm_name in "${!VMs[@]}"; do
    echo "Creating config for $vm_name..."
    create_vm_network_config "$vm_name" "${VMs[$vm_name]}"
    create_config_iso "$vm_name"
done

echo ""
echo "📝 VM Network Assignments:"
echo "=========================="
for vm_name in "${!VMs[@]}"; do
    IFS=':' read -r ip_cidr gateway bridge vnc_port <<< "${VMs[$vm_name]}"
    echo "$vm_name: $ip_cidr (Gateway: $gateway, Bridge: $bridge, VNC: $vnc_port)"
done

echo ""
echo "🚀 Configuration Method Options:"
echo "==============================="
echo "Option 1: Manual VNC Configuration"
echo "  - Connect to each VM via VNC"
echo "  - Mount configuration ISO"  
echo "  - Run network-config.sh script"
echo ""
echo "Option 2: Automated Cloud-Init (if supported)"
echo "  - Restart VMs with cloud-init configuration"
echo "  - Network settings applied automatically"
echo ""

# Create master configuration script for all VMs
cat > "/netlab/state/configure-all-vms.sh" << 'EOF'
#!/bin/bash
echo "🌐 Configuring all VM networks via VNC automation..."
echo "This script helps configure all VMs systematically"
echo ""

VNC_PORTS=(5920 5921 5922)
VM_NAMES=("edge-firewall" "web-server-1" "core-router-1")

for i in "${!VNC_PORTS[@]}"; do
    port=${VNC_PORTS[$i]}
    vm=${VM_NAMES[$i]}
    echo "=== ${vm} Configuration ==="
    echo "1. Connect VNC to localhost:$port"
    echo "2. Login to Alpine Linux console"
    echo "3. Mount config ISO: mount /dev/cdrom /mnt"
    echo "4. Run config: sh /mnt/network-config.sh"
    echo "5. Reboot: reboot"
    echo ""
    read -p "Press Enter when $vm is configured..."
done

echo "✅ All VMs should now have network configuration!"
EOF

chmod +x "/netlab/state/configure-all-vms.sh"

echo "✅ Network configuration preparation complete!"
echo ""
echo "Next Steps:"
echo "==========="
echo "1. Run: /netlab/state/configure-all-vms.sh"
echo "2. Or manually configure each VM via VNC"
echo "3. Test connectivity with network-tester.py"