#!/usr/bin/env python3
"""
NetLab V2 - Host Bridge CLI
Minimal host interface that communicates with isolated IDEV/ODRE environments.
This is the ONLY component that runs on the host system.
"""

import os
import sys
import json
import subprocess
import platform
from pathlib import Path
from typing import Dict, Any, List, Optional


class NetLabBridge:
    """Minimal bridge between host and NetLab isolated environments."""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.project_root = Path(__file__).parent
        self.docker_cmd = self._find_docker()
        
    def _find_docker(self) -> Optional[str]:
        """Find Docker executable on host system."""
        import shutil
        return shutil.which("docker")
    
    def _check_prerequisites(self) -> Dict[str, bool]:
        """Check if host has required prerequisites."""
        checks = {}
        
        # Docker availability
        checks["docker"] = self.docker_cmd is not None
        if checks["docker"]:
            try:
                result = subprocess.run([self.docker_cmd, "info"], 
                                      capture_output=True, timeout=10)
                checks["docker_daemon"] = result.returncode == 0
            except:
                checks["docker_daemon"] = False
        else:
            checks["docker_daemon"] = False
            
        # System resources (non-invasive check)
        try:
            import psutil
            checks["memory_sufficient"] = psutil.virtual_memory().total >= 8 * 1024**3  # 8GB
            checks["disk_space"] = psutil.disk_usage('.').free >= 50 * 1024**3  # 50GB
        except ImportError:
            checks["memory_sufficient"] = None
            checks["disk_space"] = None
            
        return checks
    
    def status(self) -> Dict[str, Any]:
        """Get NetLab system status without touching host system."""
        status = {
            "host_platform": self.platform,
            "prerequisites": self._check_prerequisites(),
            "idev_status": self._get_container_status("netlab-idev"),
            "odre_status": self._get_container_status("netlab-odre"),
            "project_root": str(self.project_root)
        }
        return status
    
    def _get_container_status(self, container_name: str) -> Dict[str, Any]:
        """Get status of NetLab container."""
        if not self.docker_cmd:
            return {"status": "docker_unavailable"}
            
        try:
            # Check if container exists
            result = subprocess.run([
                self.docker_cmd, "ps", "-a", "--filter", f"name={container_name}",
                "--format", "{{.Status}}"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0 or not result.stdout.strip():
                return {"status": "not_created"}
            
            status_text = result.stdout.strip()
            if "Up" in status_text:
                return {"status": "running", "details": status_text}
            else:
                return {"status": "stopped", "details": status_text}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def setup(self) -> bool:
        """Set up NetLab isolated environments."""
        print("Setting up NetLab V2 - Isolated Environments")
        print("=" * 50)
        
        # Check prerequisites
        prereqs = self._check_prerequisites()
        if not all([prereqs.get("docker"), prereqs.get("docker_daemon")]):
            print("ERROR: Docker is required but not available")
            print("Please install Docker and ensure it's running")
            return False
            
        print("Prerequisites check passed")
        
        # Build IDEV
        print("\nBuilding Isolated Development Environment (IDEV)...")
        if not self._build_idev():
            print("FAILED to build IDEV")
            return False
        print("IDEV built successfully")
        
        # Build ODRE
        print("\nBuilding Open Devices Runtime Environment (ODRE)...")
        if not self._build_odre():
            print("FAILED to build ODRE")
            return False
        print("ODRE built successfully")
        
        print("\nNetLab V2 setup completed!")
        print("\nNext steps:")
        print("  netlab dev    - Enter development environment")
        print("  netlab status - Check system status")
        return True
    
    def _build_idev(self) -> bool:
        """Build IDEV container."""
        try:
            cmd = [
                self.docker_cmd, "compose", "-f", "idev/docker-compose.dev.yml",
                "build", "netlab-idev"
            ]
            result = subprocess.run(cmd, cwd=self.project_root, timeout=600)
            return result.returncode == 0
        except Exception:
            return False
    
    def _build_odre(self) -> bool:
        """Build ODRE container."""
        try:
            cmd = [
                self.docker_cmd, "compose", "-f", "odre/docker-compose.runtime.yml", 
                "build", "netlab-odre"
            ]
            result = subprocess.run(cmd, cwd=self.project_root, timeout=600)
            return result.returncode == 0
        except Exception:
            return False
    
    def dev(self) -> bool:
        """Enter development environment (IDEV)."""
        if not self._ensure_idev_running():
            return False
            
        print("Entering NetLab Development Environment...")
        try:
            cmd = [self.docker_cmd, "exec", "-it", "netlab-idev", "/bin/bash"]
            subprocess.run(cmd)
            return True
        except Exception as e:
            print(f"FAILED to enter IDEV: {e}")
            return False
    
    def runtime(self) -> bool:
        """Enter runtime environment (ODRE)."""
        if not self._ensure_odre_running():
            return False
            
        print("Entering NetLab Runtime Environment...")
        try:
            cmd = [self.docker_cmd, "exec", "-it", "netlab-odre", "/bin/bash"]
            subprocess.run(cmd)
            return True
        except Exception as e:
            print(f"FAILED to enter ODRE: {e}")
            return False
    
    def _ensure_idev_running(self) -> bool:
        """Ensure IDEV container is running."""
        status = self._get_container_status("netlab-idev")
        if status["status"] == "running":
            return True
        elif status["status"] == "stopped":
            return self._start_container("idev/docker-compose.dev.yml", "netlab-idev")
        else:
            print("ERROR: IDEV not available. Run 'netlab setup' first.")
            return False
    
    def _ensure_odre_running(self) -> bool:
        """Ensure ODRE container is running."""
        status = self._get_container_status("netlab-odre")
        if status["status"] == "running":
            return True
        elif status["status"] == "stopped":
            return self._start_container("odre/docker-compose.runtime.yml", "netlab-odre")
        else:
            print("ERROR: ODRE not available. Run 'netlab setup' first.")
            return False
    
    def _start_container(self, compose_file: str, service_name: str) -> bool:
        """Start a container using docker-compose."""
        try:
            cmd = [self.docker_cmd, "compose", "-f", compose_file, "up", "-d", service_name]
            result = subprocess.run(cmd, cwd=self.project_root, timeout=60)
            return result.returncode == 0
        except Exception:
            return False
    
    def cleanup(self) -> bool:
        """Clean up all NetLab containers and volumes."""
        print("🧹 Cleaning up NetLab environments...")
        
        try:
            # Stop and remove IDEV
            subprocess.run([
                self.docker_cmd, "compose", "-f", "idev/docker-compose.dev.yml", 
                "down", "-v"
            ], cwd=self.project_root)
            
            # Stop and remove ODRE
            subprocess.run([
                self.docker_cmd, "compose", "-f", "odre/docker-compose.runtime.yml", 
                "down", "-v"
            ], cwd=self.project_root)
            
            print("NetLab environments cleaned up")
            return True
            
        except Exception as e:
            print(f"ERROR: Cleanup failed: {e}")
            return False


def main():
    """Main CLI entry point."""
    bridge = NetLabBridge()
    
    if len(sys.argv) < 2:
        print("NetLab V2 - Universal Parametric Cyber Range Deployment Tool")
        print("Host Bridge CLI - Manages isolated environments")
        print()
        print("Commands:")
        print("  setup     - Set up NetLab isolated environments")
        print("  status    - Show system status")
        print("  dev       - Enter development environment (IDEV)")
        print("  runtime   - Enter runtime environment (ODRE)")
        print("  cleanup   - Clean up all environments")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "setup":
        success = bridge.setup()
        sys.exit(0 if success else 1)
        
    elif command == "status":
        status = bridge.status()
        print(json.dumps(status, indent=2))
        
    elif command == "dev":
        success = bridge.dev()
        sys.exit(0 if success else 1)
        
    elif command == "runtime":
        success = bridge.runtime()
        sys.exit(0 if success else 1)
        
    elif command == "cleanup":
        success = bridge.cleanup()
        sys.exit(0 if success else 1)
        
    else:
        print(f"ERROR: Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()