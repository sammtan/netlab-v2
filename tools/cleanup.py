#!/usr/bin/env python3
"""
NetLab V2 - Cleanup Utility
Cleans up generated files, containers, and resources
"""

import argparse
import subprocess
import os
import shutil
import sys
from pathlib import Path

def run_command(cmd, capture_output=True, check=True):
    """Run shell command with error handling"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, 
                              text=True, check=check)
        return result.stdout if capture_output else None
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Error: {e.stderr if hasattr(e, 'stderr') else str(e)}")
        return None

def cleanup_docker_containers():
    """Stop and remove NetLab containers"""
    print("🐳 Cleaning up Docker containers...")
    
    # Stop containers
    containers = ["netlab-idev", "netlab-odre"]
    for container in containers:
        print(f"  Stopping {container}...")
        run_command(f"docker stop {container}", check=False)
        run_command(f"docker rm {container}", check=False)
    
    # Remove networks
    networks = ["netlab-dmz", "netlab-corp", "netlab-sec"]
    for network in networks:
        print(f"  Removing network {network}...")
        run_command(f"docker network rm {network}", check=False)

def cleanup_docker_images():
    """Remove NetLab Docker images"""
    print("🗑️ Cleaning up Docker images...")
    
    images = ["netlab-idev", "netlab-odre"]
    for image in images:
        print(f"  Removing image {image}...")
        run_command(f"docker rmi {image}", check=False)

def cleanup_generated_files():
    """Remove generated files and directories"""
    print("📁 Cleaning up generated files...")
    
    cleanup_paths = [
        ".generated",
        "workspace", 
        "state",
        "runtime",
        "cache",
        "logs",
        "images/cache",
        "images/base/*.qcow2"
    ]
    
    project_root = Path(__file__).parent.parent
    
    for path_str in cleanup_paths:
        path = project_root / path_str
        
        if "*" in path_str:
            # Handle glob patterns
            import glob
            for file_path in glob.glob(str(path)):
                print(f"  Removing {file_path}...")
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"    Warning: {e}")
        else:
            if path.exists():
                print(f"  Removing {path}...")
                try:
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
                except Exception as e:
                    print(f"    Warning: {e}")

def cleanup_system_resources():
    """Clean up system-level resources"""
    print("🧹 Cleaning up system resources...")
    
    # Remove bridge networks (if they exist)
    bridges = ["netlab-dmz", "netlab-corp", "netlab-sec"]
    for bridge in bridges:
        print(f"  Removing bridge {bridge}...")
        run_command(f"sudo ip link delete {bridge}", check=False)
    
    # Kill any remaining QEMU processes
    print("  Stopping QEMU processes...")
    run_command("pkill -f qemu-system", check=False)

def cleanup_python_cache():
    """Remove Python cache files"""
    print("🐍 Cleaning up Python cache files...")
    
    project_root = Path(__file__).parent.parent
    
    # Remove __pycache__ directories
    for cache_dir in project_root.rglob("__pycache__"):
        print(f"  Removing {cache_dir}...")
        try:
            shutil.rmtree(cache_dir)
        except Exception as e:
            print(f"    Warning: {e}")
    
    # Remove .pyc files
    for pyc_file in project_root.rglob("*.pyc"):
        print(f"  Removing {pyc_file}...")
        try:
            pyc_file.unlink()
        except Exception as e:
            print(f"    Warning: {e}")

def main():
    parser = argparse.ArgumentParser(description="NetLab V2 Cleanup Utility")
    parser.add_argument("--all", action="store_true", 
                       help="Clean up everything (containers, images, files)")
    parser.add_argument("--containers", action="store_true",
                       help="Clean up containers and networks only")
    parser.add_argument("--images", action="store_true",
                       help="Clean up Docker images")
    parser.add_argument("--files", action="store_true",
                       help="Clean up generated files only")
    parser.add_argument("--system", action="store_true",
                       help="Clean up system resources")
    parser.add_argument("--python", action="store_true",
                       help="Clean up Python cache files")
    
    args = parser.parse_args()
    
    if not any([args.all, args.containers, args.images, args.files, 
                args.system, args.python]):
        print("No cleanup options specified. Use --help for options.")
        return
    
    print("🧽 NetLab V2 Cleanup Utility")
    print("=" * 30)
    
    if args.all or args.containers:
        cleanup_docker_containers()
    
    if args.all or args.images:
        cleanup_docker_images()
    
    if args.all or args.files:
        cleanup_generated_files()
    
    if args.all or args.system:
        cleanup_system_resources()
    
    if args.all or args.python:
        cleanup_python_cache()
    
    print("\n✅ Cleanup complete!")
    print("\nTo restart NetLab V2:")
    print("  python3 netlab-bridge.py setup")

if __name__ == "__main__":
    main()