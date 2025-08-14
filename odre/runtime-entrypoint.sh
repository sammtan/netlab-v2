#!/bin/bash
set -e

echo "NetLab V2 - Open Devices Runtime Environment (ODRE)"
echo "===================================================="
echo "User: $(whoami)"
echo "Python: $(python3 --version)"
echo "QEMU: $(qemu-system-x86_64 --version | head -1)"
echo "Libvirt: $(virsh --version)"
echo "Docker: $(docker --version)"
echo "OVS: $(ovs-vsctl --version | head -1)"
echo ""

# Start required services
echo "Starting services..."
service openvswitch-switch start
service libvirtd start
service docker start

# Wait for services to be ready
sleep 3

# Create default libvirt network for NetLab
if ! virsh net-list --all | grep -q netlab-default; then
    echo "Creating default NetLab network..."
    cat > /tmp/netlab-default.xml << 'NETXML'
<network>
  <name>netlab-default</name>
  <forward mode='nat'/>
  <bridge name='netlab0' stp='on' delay='0'/>
  <ip address='192.168.100.1' netmask='255.255.255.0'>
    <dhcp>
      <range start='192.168.100.100' end='192.168.100.200'/>
    </dhcp>
  </ip>
</network>
NETXML
    
    virsh net-define /tmp/netlab-default.xml
    virsh net-autostart netlab-default
    virsh net-start netlab-default
    rm /tmp/netlab-default.xml
fi

# Create default OVS bridge
if ! ovs-vsctl br-exists netlab-br0; then
    echo "Creating default OVS bridge..."
    ovs-vsctl add-br netlab-br0
    ovs-vsctl set bridge netlab-br0 stp_enable=true
fi

echo ""
echo "Runtime environment ready!"
echo "Available commands:"
echo "  netlab-deploy <topology>  - Deploy network topology"
echo "  netlab-destroy <lab>      - Destroy lab environment"
echo "  netlab-list               - List running labs"
echo "  netlab-logs <lab>         - Show lab logs"
echo ""

exec "$@"