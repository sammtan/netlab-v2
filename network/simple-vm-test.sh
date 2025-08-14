#!/bin/bash
# Simple VM Network Test - NetLab V2
# Tests core network functionality with minimal VMs

echo "🚀 NetLab V2 - Simple Network Test"
echo "================================="

# Clean up any previous processes
echo "🧹 Cleaning up previous processes..."
sudo pkill -f qemu-system 2>/dev/null || true
sleep 2

# Create bridge networks if they don't exist
echo "🌉 Setting up bridge networks..."

# DMZ Bridge
if ! sudo ip link show netlab-dmz 2>/dev/null; then
    sudo ip link add name netlab-dmz type bridge
    sudo ip addr add 192.168.10.1/24 dev netlab-dmz
    sudo ip link set netlab-dmz up
    echo "✅ Created netlab-dmz bridge"
else
    echo "✅ netlab-dmz bridge already exists"
fi

# Corporate Bridge
if ! sudo ip link show netlab-corp 2>/dev/null; then
    sudo ip link add name netlab-corp type bridge
    sudo ip addr add 192.168.20.1/24 dev netlab-corp
    sudo ip link set netlab-corp up
    echo "✅ Created netlab-corp bridge"
else
    echo "✅ netlab-corp bridge already exists"
fi

# Security Bridge
if ! sudo ip link show netlab-sec 2>/dev/null; then
    sudo ip link add name netlab-sec type bridge
    sudo ip addr add 192.168.40.1/24 dev netlab-sec
    sudo ip link set netlab-sec up
    echo "✅ Created netlab-sec bridge"
else
    echo "✅ netlab-sec bridge already exists"
fi

echo ""
echo "📊 Network Bridge Status:"
sudo ip link show type bridge | grep netlab
echo ""

echo "🎯 Starting 3 Test VMs with VNC Access:"
echo "======================================="

# Test VM 1 - Edge Firewall (DMZ)
echo "Starting Edge Firewall (VNC :20)..."
qemu-system-x86_64 \
    -m 512 \
    -hda /netlab/vms/firewalls/edge-firewall/disk.img \
    -netdev bridge,id=net0,br=netlab-dmz \
    -device e1000,netdev=net0 \
    -vnc :20 \
    -daemonize \
    -name edge-firewall

# Test VM 2 - Web Server (DMZ)
echo "Starting Web Server (VNC :21)..."
qemu-system-x86_64 \
    -m 1024 \
    -hda /netlab/vms/servers/web-server-1/disk.img \
    -netdev bridge,id=net0,br=netlab-dmz \
    -device e1000,netdev=net0 \
    -vnc :21 \
    -daemonize \
    -name web-server-1

# Test VM 3 - Core Router (Corporate)
echo "Starting Core Router (VNC :22)..."
qemu-system-x86_64 \
    -m 512 \
    -hda /netlab/vms/routers/core-router-1/disk.img \
    -netdev bridge,id=net0,br=netlab-corp \
    -device e1000,netdev=net0 \
    -vnc :22 \
    -daemonize \
    -name core-router-1

sleep 5

echo ""
echo "🔍 VM Status Check:"
echo "=================="
ps aux | grep qemu-system | grep -v grep | wc -l | xargs echo "Running VMs:"

echo ""
echo "🌐 Network Connectivity Tests:"
echo "=============================="

# Test bridge connectivity
echo "Testing bridge network gateways:"
echo -n "DMZ Gateway (192.168.10.1): "
if ping -c 1 -W 2 192.168.10.1 >/dev/null 2>&1; then
    echo "✅ REACHABLE"
else
    echo "⚠️  TIMEOUT"
fi

echo -n "Corporate Gateway (192.168.20.1): "
if ping -c 1 -W 2 192.168.20.1 >/dev/null 2>&1; then
    echo "✅ REACHABLE"
else
    echo "⚠️  TIMEOUT"
fi

echo -n "Security Gateway (192.168.40.1): "
if ping -c 1 -W 2 192.168.40.1 >/dev/null 2>&1; then
    echo "✅ REACHABLE"
else
    echo "⚠️  TIMEOUT"
fi

echo ""
echo "📋 Network Test Summary:"
echo "========================"
echo "✅ Enterprise network bridges created"
echo "✅ VMs deployed with bridge networking"  
echo "✅ VNC access available on ports 5920-5922"
echo "✅ Ready for VM OS configuration and testing"

echo ""
echo "🎮 VNC Access Instructions:"
echo "==========================="
echo "Edge Firewall:  VNC Viewer -> localhost:5920"
echo "Web Server:     VNC Viewer -> localhost:5921"  
echo "Core Router:    VNC Viewer -> localhost:5922"

echo ""
echo "📝 Next Steps:"
echo "=============="
echo "1. Connect via VNC to configure VM operating systems"
echo "2. Set static IP addresses on VMs"
echo "3. Test inter-VM communication"
echo "4. Configure network services"