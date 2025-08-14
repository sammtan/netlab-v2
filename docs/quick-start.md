# NetLab V2 - Quick Start Guide

[![Quick Start](https://img.shields.io/badge/Quick%20Start-5%20Minutes-green.svg)](quick-start.md)
[![Difficulty](https://img.shields.io/badge/Difficulty-Beginner-brightgreen.svg)](quick-start.md)

> **Get your first cyber range up and running in under 5 minutes!**

## 🚀 Prerequisites Check (30 seconds)

```bash
# Quick system check
echo "CPU Cores: $(nproc)"
echo "RAM: $(free -h | awk '/Mem:/{print $2}')" 
echo "Disk: $(df -h . | awk 'NR==2{print $4}')"
echo "Docker: $(docker --version 2>/dev/null || echo 'Install Docker')"

# Requirements: 4+ cores, 8GB+ RAM, 50GB+ disk, Docker 20.10+
```

## ⚡ Installation (2 minutes)

```bash
# 1. Clone repository
git clone https://github.com/sammtan/netlab-v2.git
cd netlab-v2

# 2. One-command setup
python3 netlab-bridge.py setup

# ✅ Setup complete when you see:
# "NetLab V2 installation complete!"
```

## 🌐 Deploy Your First Lab (2 minutes)

```bash
# 1. Enter development environment
python3 netlab-bridge.py dev

# 2. Deploy enterprise network (inside container)
netlab-deploy enterprise-network-lab.yaml

# ✅ Success when you see:
# "Enterprise network lab deployed successfully!"
```

## 🎮 Access Your Lab (1 minute)

**Web Dashboard** (easiest):
```bash
# Open in browser: http://localhost:9000
# Features: Interactive topology, one-click VNC, testing tools
```

**VNC Access** (direct):
```bash
# Connect with any VNC client:
# Edge Firewall: localhost:5920
# Web Server: localhost:5921  
# Core Router: localhost:5922
```

## 🧪 Run Your First Test (30 seconds)

```bash
# In web dashboard: Click "Full Network Test" button
# OR via command line (inside IDEV):
network-tester.py --quick

# ✅ Expected: 90%+ success rate
```

## 🎯 What You've Achieved

✅ **Complete Enterprise Network**: 17 VMs across 3 VLANs
✅ **Security Segmentation**: DMZ, Corporate, Security zones  
✅ **Management Interface**: Web dashboard with real-time monitoring
✅ **Testing Framework**: Automated network validation
✅ **VM Console Access**: Full administrative access to all systems

## 🚀 Next Steps

1. **Explore the Web Dashboard**: http://localhost:9000
2. **Connect to VMs**: Try VNC access to different devices
3. **Run Network Tests**: Experiment with different test types
4. **Read Full Documentation**: [Complete User Guide](user-guide.md)

## ❓ Need Help?

**Quick Solutions**:
- **VMs won't start**: `python3 netlab-bridge.py cleanup && python3 netlab-bridge.py setup`
- **Network issues**: `network-tester.py --diagnosis`
- **Performance slow**: Check host resources with `htop`

**Full Support**: [User Guide](user-guide.md) | [Troubleshooting](user-guide.md#troubleshooting) | [GitHub Issues](https://github.com/sammtan/netlab-v2/issues)

---

🎉 **Congratulations!** You now have a fully functional enterprise cyber range running on your system!