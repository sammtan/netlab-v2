# NetLab V2 - API Reference

[![API Version](https://img.shields.io/badge/API%20Version-v2.0-blue.svg)](api-reference.md)
[![Documentation](https://img.shields.io/badge/Docs-Complete-green.svg)](api-reference.md)

> **Complete REST API documentation for NetLab V2 web management interface**

## 🌐 Overview

The NetLab V2 REST API provides programmatic access to all platform functionality, enabling automation, integration, and custom tooling. The API is built on standard HTTP methods and returns JSON responses.

### **Base URL**
```
http://localhost:9000/api/
```

### **Authentication**
- **Current**: No authentication required (development mode)
- **Production**: Token-based authentication (configurable)
- **Future**: OAuth 2.0, API keys, JWT tokens

### **Response Format**
All API responses return JSON with consistent structure:
```json
{
  "success": true,
  "data": { /* response data */ },
  "timestamp": "2025-01-15T10:30:00Z",
  "version": "v2.0"
}
```

### **Error Handling**
Error responses include detailed information:
```json
{
  "success": false,
  "error": {
    "code": "VM_NOT_FOUND",
    "message": "Virtual machine 'web-server' not found",
    "details": "Available VMs: edge-firewall, core-router"
  },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

## 📊 System Status Endpoints

### **GET /api/status**
Get comprehensive system status and metrics.

#### **Response**
```json
{
  "success": true,
  "data": {
    "timestamp": 1705319400,
    "odre_status": "online",
    "vm_count": 3,
    "memory_usage": {
      "total": 20797648896,
      "used": 1090236416,
      "percent": 5.2
    },
    "disk_usage": {
      "total": 107374182400,
      "used": 95367782400,
      "percent": 88.8
    },
    "network_bridges": 3,
    "active_connections": 15,
    "uptime": 3600
  }
}
```

#### **Fields**
- `timestamp`: Unix timestamp of status check
- `odre_status`: Runtime environment status (`online`, `offline`, `starting`)
- `vm_count`: Number of active virtual machines
- `memory_usage`: System memory utilization statistics
- `disk_usage`: Storage utilization statistics  
- `network_bridges`: Number of active network bridges
- `active_connections`: Active network connections count
- `uptime`: System uptime in seconds

#### **Example Usage**
```bash
curl http://localhost:9000/api/status
```

### **GET /api/health**
Simple health check endpoint.

#### **Response**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2025-01-15T10:30:00Z"
  }
}
```

## 🖥️ Virtual Machine Management

### **GET /api/vms**
List all virtual machines with their current status.

#### **Response**
```json
{
  "success": true,
  "data": {
    "vms": [
      {
        "id": "edge-firewall",
        "name": "Edge Firewall",
        "type": "firewall",
        "network": "DMZ",
        "ip_address": "192.168.10.10",
        "vnc_port": "5920",
        "status": "running",
        "pid": 1597,
        "memory": "512MB",
        "cpu_usage": 2.5,
        "uptime": 1800
      },
      {
        "id": "web-server",
        "name": "Web Server",
        "type": "server", 
        "network": "DMZ",
        "ip_address": "192.168.10.20",
        "vnc_port": "5921",
        "status": "running",
        "pid": 1609,
        "memory": "1024MB",
        "cpu_usage": 1.8,
        "uptime": 1795
      }
    ],
    "total_count": 2,
    "running_count": 2,
    "stopped_count": 0
  }
}
```

#### **VM Status Values**
- `running`: VM is active and operational
- `stopped`: VM is stopped/shutdown
- `starting`: VM is booting up
- `stopping`: VM is shutting down
- `error`: VM encountered an error

### **GET /api/vms/{vm_id}**
Get detailed information about a specific virtual machine.

#### **Parameters**
- `vm_id` (string): VM identifier (e.g., "edge-firewall")

#### **Response**
```json
{
  "success": true,
  "data": {
    "id": "edge-firewall",
    "name": "Edge Firewall",
    "type": "firewall",
    "network": "DMZ",
    "ip_address": "192.168.10.10",
    "vnc_port": "5920",
    "status": "running",
    "pid": 1597,
    "memory": {
      "allocated": "512MB",
      "used": "320MB",
      "percent": 62.5
    },
    "cpu_usage": 2.5,
    "disk_usage": "4.0GB",
    "network_interfaces": [
      {
        "name": "eth0",
        "mac": "52:54:00:10:00:10",
        "bridge": "netlab-dmz",
        "status": "up"
      }
    ],
    "configuration": {
      "os": "Alpine Linux",
      "arch": "x86_64",
      "boot_order": ["hd", "cdrom"],
      "features": ["firewall", "routing"]
    },
    "uptime": 1800,
    "boot_time": "2025-01-15T10:00:00Z"
  }
}
```

### **POST /api/vms/{vm_id}/start**
Start a stopped virtual machine.

#### **Parameters**
- `vm_id` (string): VM identifier

#### **Request Body**
```json
{
  "force": false,
  "timeout": 60
}
```

#### **Response**
```json
{
  "success": true,
  "data": {
    "vm_id": "web-server",
    "status": "starting",
    "message": "VM start command sent successfully",
    "estimated_boot_time": 45
  }
}
```

### **POST /api/vms/{vm_id}/stop**
Stop a running virtual machine.

#### **Parameters**
- `vm_id` (string): VM identifier

#### **Request Body**
```json
{
  "force": false,
  "graceful": true,
  "timeout": 30
}
```

#### **Response**
```json
{
  "success": true,
  "data": {
    "vm_id": "web-server",
    "status": "stopping",
    "message": "VM stop command sent successfully",
    "estimated_stop_time": 10
  }
}
```

### **POST /api/vms/{vm_id}/restart**
Restart a virtual machine.

#### **Parameters**
- `vm_id` (string): VM identifier

#### **Response**
```json
{
  "success": true,
  "data": {
    "vm_id": "core-router",
    "status": "restarting",
    "message": "VM restart initiated",
    "estimated_restart_time": 60
  }
}
```

### **GET /api/vms/{vm_id}/console**
Get VNC console connection information.

#### **Response**
```json
{
  "success": true,
  "data": {
    "vm_id": "edge-firewall",
    "vnc_port": "5920",
    "vnc_url": "vnc://localhost:5920",
    "web_console": "http://localhost:9000/console/edge-firewall",
    "status": "available",
    "connection_info": {
      "protocol": "VNC",
      "port": 5920,
      "authentication": false,
      "encryption": false
    }
  }
}
```

## 🌐 Network Management

### **GET /api/network**
Get comprehensive network topology information.

#### **Response**
```json
{
  "success": true,
  "data": {
    "bridges": [
      {
        "name": "netlab-dmz",
        "subnet": "192.168.10.0/24",
        "gateway": "192.168.10.1",
        "status": "up",
        "vms_connected": 2,
        "traffic_stats": {
          "bytes_in": 1048576,
          "bytes_out": 2097152,
          "packets_in": 1024,
          "packets_out": 2048
        }
      },
      {
        "name": "netlab-corp", 
        "subnet": "192.168.20.0/24",
        "gateway": "192.168.20.1",
        "status": "up",
        "vms_connected": 1,
        "traffic_stats": {
          "bytes_in": 524288,
          "bytes_out": 1048576,
          "packets_in": 512,
          "packets_out": 1024
        }
      }
    ],
    "total_networks": 3,
    "total_vms": 3,
    "total_connections": 3,
    "routing_table": [
      {
        "destination": "192.168.10.0/24",
        "gateway": "192.168.10.1",
        "interface": "netlab-dmz"
      },
      {
        "destination": "192.168.20.0/24", 
        "gateway": "192.168.20.1",
        "interface": "netlab-corp"
      }
    ]
  }
}
```

### **GET /api/network/bridges**
List all network bridges.

#### **Response**
```json
{
  "success": true,
  "data": {
    "bridges": [
      {
        "name": "netlab-dmz",
        "type": "bridge",
        "subnet": "192.168.10.0/24",
        "gateway": "192.168.10.1",
        "status": "up",
        "mtu": 1500,
        "connected_vms": ["edge-firewall", "web-server"],
        "tap_interfaces": ["tap0", "tap1"]
      }
    ]
  }
}
```

### **GET /api/network/topology**
Get network topology for visualization.

#### **Response**
```json
{
  "success": true,
  "data": {
    "nodes": [
      {
        "id": "edge-firewall",
        "type": "vm",
        "label": "Edge Firewall",
        "network": "dmz",
        "status": "running",
        "position": {"x": 100, "y": 50}
      },
      {
        "id": "netlab-dmz",
        "type": "network",
        "label": "DMZ Network",
        "subnet": "192.168.10.0/24"
      }
    ],
    "edges": [
      {
        "from": "edge-firewall",
        "to": "netlab-dmz",
        "type": "network_connection",
        "interface": "eth0"
      }
    ],
    "layout": "hierarchical"
  }
}
```

## 🧪 Testing & Monitoring

### **POST /api/test/connectivity**
Run comprehensive network connectivity tests.

#### **Request Body**
```json
{
  "test_type": "full",
  "targets": ["all"],
  "timeout": 30,
  "include_performance": true
}
```

#### **Response**
```json
{
  "success": true,
  "data": {
    "test_session": {
      "id": "test_20250115_103000",
      "start_time": "2025-01-15T10:30:00Z",
      "test_type": "full",
      "total_tests": 15,
      "completed_tests": 15,
      "duration": 45.2
    },
    "results": {
      "gateways": [
        {
          "target": "192.168.10.1",
          "name": "DMZ Gateway",
          "status": "success",
          "latency": "0.5ms",
          "packet_loss": "0%"
        }
      ],
      "vms": [
        {
          "target": "192.168.10.10",
          "name": "Edge Firewall", 
          "status": "success",
          "latency": "1.2ms",
          "packet_loss": "0%",
          "services": ["ssh", "https"]
        }
      ],
      "inter_network": [
        {
          "from": "DMZ",
          "to": "Corporate",
          "status": "success",
          "latency": "0.8ms"
        }
      ]
    },
    "summary": {
      "total_success": 13,
      "total_failed": 2,
      "success_rate": 86.7,
      "average_latency": "0.9ms"
    }
  }
}
```

### **GET /api/test/history**
Get test history and results.

#### **Query Parameters**
- `limit` (number): Number of results to return (default: 50)
- `offset` (number): Offset for pagination (default: 0)
- `test_type` (string): Filter by test type
- `status` (string): Filter by test status

#### **Response**
```json
{
  "success": true,
  "data": {
    "tests": [
      {
        "id": "test_20250115_103000",
        "timestamp": "2025-01-15T10:30:00Z",
        "test_type": "connectivity",
        "status": "completed",
        "success_rate": 86.7,
        "duration": 45.2,
        "total_tests": 15
      }
    ],
    "pagination": {
      "total": 25,
      "limit": 50,
      "offset": 0,
      "has_next": false
    }
  }
}
```

### **GET /api/logs**
Get system logs with filtering.

#### **Query Parameters**
- `level` (string): Log level filter (`debug`, `info`, `warn`, `error`)
- `component` (string): Component filter (`vm`, `network`, `api`)
- `limit` (number): Number of logs to return (default: 100)
- `since` (string): Return logs since timestamp

#### **Response**
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "timestamp": "2025-01-15T10:30:00Z",
        "level": "info",
        "component": "vm",
        "vm_id": "edge-firewall",
        "message": "VM started successfully",
        "details": {
          "pid": 1597,
          "memory": "512MB",
          "boot_time": 23.5
        }
      },
      {
        "timestamp": "2025-01-15T10:29:30Z",
        "level": "info", 
        "component": "network",
        "message": "Bridge netlab-dmz created",
        "details": {
          "subnet": "192.168.10.0/24",
          "gateway": "192.168.10.1"
        }
      }
    ],
    "total_count": 147,
    "filtered_count": 23
  }
}
```

## 🏗️ Topology Management

### **GET /api/topologies**
List available network topologies.

#### **Response**
```json
{
  "success": true,
  "data": {
    "topologies": [
      {
        "name": "enterprise-network-lab",
        "display_name": "Enterprise Network Lab",
        "description": "Full enterprise with DMZ, Corporate, Security VLANs",
        "vm_count": 17,
        "complexity": 5,
        "resource_requirements": {
          "ram": "16GB",
          "disk": "95GB",
          "cpu_cores": 8
        },
        "networks": ["DMZ", "Corporate", "Security"],
        "status": "production"
      },
      {
        "name": "basic-security",
        "display_name": "Basic Security Lab",
        "description": "Essential security testing environment",
        "vm_count": 5,
        "complexity": 3,
        "resource_requirements": {
          "ram": "8GB",
          "disk": "25GB", 
          "cpu_cores": 4
        },
        "networks": ["DMZ", "Internal"],
        "status": "production"
      }
    ]
  }
}
```

### **GET /api/topologies/{topology_name}**
Get detailed topology configuration.

#### **Parameters**
- `topology_name` (string): Topology identifier

#### **Response**
```json
{
  "success": true,
  "data": {
    "name": "enterprise-network-lab",
    "display_name": "Enterprise Network Lab",
    "description": "Complete enterprise network simulation",
    "version": "2.0",
    "constraints": {
      "max_ram": 23500,
      "max_disk": 90000,
      "max_cpu": 14
    },
    "networks": {
      "dmz": {
        "subnet": "192.168.10.0/24",
        "gateway": "192.168.10.1",
        "purpose": "DMZ and external-facing services"
      },
      "corporate": {
        "subnet": "192.168.20.0/24", 
        "gateway": "192.168.20.1",
        "purpose": "Internal corporate network"
      }
    },
    "vms": [
      {
        "name": "edge-firewall",
        "type": "firewall",
        "network": "dmz",
        "memory": 512,
        "disk": "4GB",
        "ip": "192.168.10.10",
        "role": "Edge firewall and gateway"
      }
    ],
    "deployment_time": "< 15 minutes",
    "use_cases": ["Training", "Security Testing", "Research"]
  }
}
```

### **POST /api/topologies/{topology_name}/deploy**
Deploy a network topology.

#### **Parameters**
- `topology_name` (string): Topology to deploy

#### **Request Body**
```json
{
  "instance_name": "my-enterprise-lab",
  "resource_limits": {
    "max_memory": "20GB",
    "max_disk": "80GB"
  },
  "configuration": {
    "enable_internet": false,
    "vnc_passwords": true,
    "auto_start_vms": true
  }
}
```

#### **Response**
```json
{
  "success": true,
  "data": {
    "deployment_id": "deploy_20250115_103000", 
    "instance_name": "my-enterprise-lab",
    "status": "deploying",
    "progress": 0,
    "estimated_time": 900,
    "deployment_steps": [
      "Creating network bridges",
      "Deploying VM images",
      "Starting virtual machines",
      "Configuring network connectivity"
    ]
  }
}
```

### **GET /api/deployments/{deployment_id}/status**
Check deployment progress.

#### **Response**
```json
{
  "success": true,
  "data": {
    "deployment_id": "deploy_20250115_103000",
    "status": "in_progress",
    "progress": 65,
    "current_step": "Starting virtual machines",
    "elapsed_time": 420,
    "estimated_remaining": 180,
    "logs": [
      "Network bridges created successfully",
      "VM images deployed (17/17)",
      "Starting edge-firewall VM...",
      "Starting web-server VM..."
    ]
  }
}
```

## ⚙️ Configuration Management

### **GET /api/config**
Get current system configuration.

#### **Response**
```json
{
  "success": true,
  "data": {
    "system": {
      "version": "2.0.0",
      "api_version": "v2",
      "environment": "development",
      "debug_mode": true
    },
    "resource_limits": {
      "max_vms": 50,
      "max_memory": "32GB",
      "max_disk": "500GB",
      "max_networks": 10
    },
    "security": {
      "vnc_authentication": false,
      "api_authentication": false,
      "network_isolation": true,
      "container_privileges": "limited"
    },
    "features": {
      "web_interface": true,
      "api_access": true,
      "vnc_console": true,
      "network_testing": true,
      "topology_management": true
    }
  }
}
```

### **PUT /api/config**
Update system configuration.

#### **Request Body**
```json
{
  "resource_limits": {
    "max_vms": 25,
    "max_memory": "24GB"
  },
  "security": {
    "vnc_authentication": true,
    "api_authentication": true
  }
}
```

#### **Response**
```json
{
  "success": true,
  "data": {
    "message": "Configuration updated successfully",
    "updated_fields": ["resource_limits", "security"],
    "restart_required": false
  }
}
```

## 📊 Analytics & Reporting

### **GET /api/analytics/usage**
Get system usage analytics.

#### **Query Parameters**
- `period` (string): Time period (`hour`, `day`, `week`, `month`)
- `metric` (string): Specific metric to retrieve

#### **Response**
```json
{
  "success": true,
  "data": {
    "period": "day",
    "metrics": {
      "vm_deployments": {
        "total": 25,
        "successful": 23,
        "failed": 2,
        "success_rate": 92.0
      },
      "network_tests": {
        "total": 150,
        "passed": 142,
        "failed": 8,
        "pass_rate": 94.7
      },
      "resource_usage": {
        "peak_memory": "18.5GB",
        "peak_cpu": 85.2,
        "peak_disk": "87GB",
        "average_vms": 12.5
      },
      "api_requests": {
        "total": 2847,
        "successful": 2821,
        "errors": 26,
        "error_rate": 0.9
      }
    },
    "trends": {
      "vm_deployments": "increasing",
      "resource_usage": "stable", 
      "api_usage": "increasing"
    }
  }
}
```

### **GET /api/reports/summary**
Generate comprehensive system summary report.

#### **Response**
```json
{
  "success": true,
  "data": {
    "report_id": "summary_20250115",
    "generated_at": "2025-01-15T10:30:00Z",
    "period": "last_30_days",
    "summary": {
      "total_deployments": 156,
      "unique_topologies": 8,
      "total_vms_created": 1247,
      "total_test_runs": 892,
      "uptime_percentage": 99.2,
      "avg_deployment_time": "8.5 minutes"
    },
    "performance": {
      "fastest_deployment": "3.2 minutes",
      "slowest_deployment": "18.7 minutes",
      "avg_network_latency": "0.8ms",
      "max_concurrent_vms": 45
    },
    "reliability": {
      "vm_success_rate": 96.8,
      "network_test_pass_rate": 94.1,
      "api_error_rate": 0.7,
      "system_crashes": 0
    },
    "recommendations": [
      "Consider increasing VM memory allocation for better performance",
      "Network test failure rate could be improved with additional monitoring",
      "System is operating within optimal parameters"
    ]
  }
}
```

## 🔧 Administration

### **POST /api/admin/shutdown**
Gracefully shutdown the NetLab system.

#### **Request Body**
```json
{
  "force": false,
  "stop_vms": true,
  "cleanup_networks": true,
  "reason": "Scheduled maintenance"
}
```

#### **Response**
```json
{
  "success": true,
  "data": {
    "message": "System shutdown initiated",
    "shutdown_steps": [
      "Stopping all VMs",
      "Cleaning up network bridges", 
      "Stopping containers",
      "System shutdown"
    ],
    "estimated_time": 120
  }
}
```

### **POST /api/admin/backup**
Create system backup.

#### **Request Body**
```json
{
  "include_vms": true,
  "include_configs": true,
  "include_logs": false,
  "compression": "gzip"
}
```

#### **Response**
```json
{
  "success": true,
  "data": {
    "backup_id": "backup_20250115_103000",
    "status": "creating",
    "backup_location": "/netlab/backups/backup_20250115_103000.tar.gz",
    "estimated_size": "12.5GB",
    "estimated_time": 300
  }
}
```

## 🐛 Error Codes

### **System Errors (1000-1999)**
- `1000`: `SYSTEM_ERROR` - General system error
- `1001`: `INSUFFICIENT_RESOURCES` - Not enough system resources
- `1002`: `PERMISSION_DENIED` - Insufficient permissions
- `1003`: `SERVICE_UNAVAILABLE` - Service temporarily unavailable

### **VM Errors (2000-2999)**
- `2000`: `VM_NOT_FOUND` - Virtual machine not found
- `2001`: `VM_ALREADY_RUNNING` - VM is already running
- `2002`: `VM_START_FAILED` - Failed to start VM
- `2003`: `VM_STOP_FAILED` - Failed to stop VM
- `2004`: `VM_CONFIG_INVALID` - Invalid VM configuration

### **Network Errors (3000-3999)**
- `3000`: `NETWORK_ERROR` - General network error
- `3001`: `BRIDGE_CREATE_FAILED` - Failed to create network bridge
- `3002`: `IP_ADDRESS_CONFLICT` - IP address conflict detected
- `3003`: `NETWORK_UNREACHABLE` - Network destination unreachable

### **API Errors (4000-4999)**
- `4000`: `INVALID_REQUEST` - Malformed API request
- `4001`: `MISSING_PARAMETER` - Required parameter missing
- `4002`: `INVALID_PARAMETER` - Parameter value invalid
- `4003`: `AUTHENTICATION_FAILED` - Authentication required
- `4004`: `AUTHORIZATION_FAILED` - Insufficient privileges

## 📚 SDK & Client Libraries

### **Python SDK**
```python
from netlab_v2 import NetLabClient

# Initialize client
client = NetLabClient(base_url='http://localhost:9000')

# Get system status
status = client.get_status()
print(f"System status: {status['odre_status']}")

# List VMs
vms = client.list_vms()
for vm in vms:
    print(f"{vm['name']}: {vm['status']}")

# Start VM
client.start_vm('edge-firewall')

# Run connectivity test
test_result = client.run_connectivity_test()
print(f"Test success rate: {test_result['summary']['success_rate']}%")
```

### **JavaScript/Node.js SDK**
```javascript
const NetLabClient = require('netlab-v2-client');

// Initialize client
const client = new NetLabClient({
  baseURL: 'http://localhost:9000'
});

// Get system status
const status = await client.getStatus();
console.log(`VM Count: ${status.vm_count}`);

// Deploy topology
const deployment = await client.deployTopology('enterprise-network-lab', {
  instance_name: 'my-lab'
});

// Monitor deployment progress
const progress = await client.getDeploymentStatus(deployment.deployment_id);
console.log(`Progress: ${progress.progress}%`);
```

### **Bash/curl Examples**
```bash
#!/bin/bash
BASE_URL="http://localhost:9000/api"

# Get system status
curl -s "$BASE_URL/status" | jq '.data.vm_count'

# List running VMs
curl -s "$BASE_URL/vms" | jq '.data.vms[] | select(.status=="running") | .name'

# Start VM
curl -X POST "$BASE_URL/vms/web-server/start" -H "Content-Type: application/json"

# Run network test
curl -X POST "$BASE_URL/test/connectivity" \
  -H "Content-Type: application/json" \
  -d '{"test_type": "basic", "timeout": 30}' | jq '.data.summary.success_rate'
```

## 🔄 Webhooks & Events

### **Webhook Configuration**
Configure webhooks to receive real-time notifications:

```json
{
  "webhook_url": "https://your-app.com/netlab-webhook",
  "events": ["vm.started", "vm.stopped", "test.completed", "deployment.finished"],
  "secret": "your-webhook-secret"
}
```

### **Event Types**
- **VM Events**: `vm.started`, `vm.stopped`, `vm.error`
- **Network Events**: `network.connected`, `network.disconnected`
- **Test Events**: `test.started`, `test.completed`, `test.failed`
- **Deployment Events**: `deployment.started`, `deployment.completed`, `deployment.failed`
- **System Events**: `system.startup`, `system.shutdown`, `system.error`

### **Webhook Payload**
```json
{
  "event": "vm.started",
  "timestamp": "2025-01-15T10:30:00Z",
  "data": {
    "vm_id": "edge-firewall",
    "vm_name": "Edge Firewall",
    "status": "running",
    "boot_time": 23.5
  },
  "signature": "sha256=..."
}
```

## 📝 Rate Limiting

### **Rate Limits**
- **Default**: 100 requests per minute per IP
- **Burst**: 20 requests in 10 seconds
- **VM Operations**: 10 operations per minute
- **Test Execution**: 5 tests per minute

### **Rate Limit Headers**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705319460
X-RateLimit-Retry-After: 60
```

## 🔍 Debugging & Development

### **Debug Mode**
Enable debug mode for detailed logging:
```bash
export NETLAB_DEBUG=true
export NETLAB_LOG_LEVEL=debug
```

### **API Testing**
Use the built-in API testing endpoints:
```
GET /api/debug/ping
GET /api/debug/system-info
GET /api/debug/memory-usage
POST /api/debug/test-vm-operation
```

---

## 📞 Support

For API support, issues, or feature requests:
- **GitHub Issues**: [API Issues](https://github.com/sammtan/netlab-v2/issues)
- **API Documentation**: Always up-to-date at `/api/docs`
- **Community**: [Discord #api-support](https://discord.gg/netlab-v2)

---

*This API reference is automatically generated and updated with each NetLab V2 release.*