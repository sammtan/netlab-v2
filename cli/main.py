"""NetLab main CLI entry point."""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Add the project root to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli import __version__
from core.planner.capacity import HostResourceScanner
from scripts.host_detect import detect_host_capabilities
from core.backends.manager import BackendManager
from core.deployment import DeploymentEngine, TopologyLoader

# Initialize Typer app and Rich console
app = typer.Typer(
    name="uvdnl",
    help="NetLab - Universal Parametric Cyber Range Deployment Tool",
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

console = Console()


def version_callback(value: bool) -> None:
    """Show version information."""
    if value:
        console.print(f"[bold blue]NetLab (uvdnl)[/bold blue] version [bold]{__version__}[/bold]")
        console.print("Universal Parametric Cyber Range Deployment Tool")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version information",
        callback=version_callback,
        is_eager=True,
    )
) -> None:
    """NetLab - Universal Parametric Cyber Range Deployment Tool.
    
    Build, deploy, and manage complex network topologies with real devices.
    """
    pass


@app.command("init")
def init_command(
    workspace: Path = typer.Option(
        Path.home() / ".netlab",
        "--workspace",
        "-w",
        help="NetLab workspace directory",
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Force reinitialize"),
) -> None:
    """Initialize NetLab workspace and perform first-run setup."""
    console.print("[bold blue]NetLab Initialization[/bold blue]")
    console.print("=" * 50)
    
    # Create workspace directories
    dirs = [
        workspace,
        workspace / "labs",
        workspace / "images",
        workspace / "images" / "base",
        workspace / "images" / "cache",
        workspace / "configs",
        workspace / "logs",
        workspace / "state",
    ]
    
    for dir_path in dirs:
        if dir_path.exists() and not force:
            console.print(f"[green]OK[/green] Directory exists: {dir_path}")
        else:
            dir_path.mkdir(parents=True, exist_ok=True)
            console.print(f"[blue]Created[/blue]: {dir_path}")
    
    console.print("\n[green]NetLab workspace initialized![/green]")
    console.print(f"Workspace location: [bold]{workspace}[/bold]")
    
    # Show next steps
    console.print("\n[bold yellow]Next Steps:[/bold yellow]")
    console.print("1. [blue]uvdnl host scan[/blue] - Check host capabilities")
    console.print("2. [blue]uvdnl sources sync[/blue] - Download device images")
    console.print("3. [blue]uvdnl catalog list[/blue] - View available devices")


@app.command("host")
def host_command() -> None:
    """Host resource management commands."""
    pass


@app.command("scan", help="Scan host resources and capabilities")
def scan_command(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Scan and display host system resources and capabilities."""
    if json_output:
        # JSON output for programmatic use
        import json
        capabilities = detect_host_capabilities()
        console.print(json.dumps(capabilities, indent=2))
        return
    
    # Rich formatted output for human consumption
    console.print("[bold blue]NetLab Host Resource Scan[/bold blue]")
    console.print("=" * 50)
    
    scanner = HostResourceScanner()
    resources = scanner.scan_resources()
    
    # System Information Table
    system_table = Table(title="System Information", show_header=True, header_style="bold magenta")
    system_table.add_column("Component", style="cyan", width=20)
    system_table.add_column("Details", style="white")
    system_table.add_column("Status", justify="center")
    
    # CPU Information
    cpu_status = "Good" if resources.cpu_cores >= 4 else "Limited"
    system_table.add_row(
        "CPU",
        f"{resources.cpu_cores} cores ({resources.cpu_threads} threads)",
        cpu_status
    )
    
    # RAM Information
    ram_gb = resources.ram_total_mb // 1024
    ram_available_gb = resources.ram_available_mb // 1024
    ram_status = "Good" if ram_gb >= 8 else "Limited"
    system_table.add_row(
        "RAM",
        f"{ram_gb} GB total ({ram_available_gb} GB available)",
        ram_status
    )
    
    # Disk Information
    disk_gb = resources.disk_free_gb
    disk_status = "Good" if disk_gb >= 100 else "Limited"
    system_table.add_row(
        "Disk Space",
        f"{disk_gb:.1f} GB free",
        disk_status
    )
    
    # Virtualization Support
    virt_status = "Available" if resources.virtualization_enabled else "Not Available"
    system_table.add_row(
        "Virtualization",
        f"KVM/VT-x support",
        virt_status
    )
    
    console.print(system_table)
    
    # Resource Limits Calculation
    console.print("\n[bold yellow]📊 NetLab Resource Allocation Limits:[/bold yellow]")
    
    limits_table = Table(show_header=True, header_style="bold green")
    limits_table.add_column("Resource", style="cyan")
    limits_table.add_column("Available", justify="right")
    limits_table.add_column("NetLab Limit (70%)", justify="right")
    limits_table.add_column("Safety Buffer", justify="right")
    
    max_cpu = int(resources.cpu_threads * 0.7)
    max_ram_gb = int((resources.ram_available_mb * 0.7) // 1024)
    max_disk_gb = int(resources.disk_free_gb * 0.8)
    
    limits_table.add_row(
        "CPU Cores",
        f"{resources.cpu_threads}",
        f"{max_cpu}",
        f"{resources.cpu_threads - max_cpu} reserved"
    )
    limits_table.add_row(
        "RAM",
        f"{ram_available_gb} GB",
        f"{max_ram_gb} GB",
        f"{ram_available_gb - max_ram_gb} GB reserved"
    )
    limits_table.add_row(
        "Disk Space",
        f"{disk_gb:.1f} GB",
        f"{max_disk_gb} GB",
        f"{disk_gb - max_disk_gb:.1f} GB reserved"
    )
    
    console.print(limits_table)
    
    # Deployment Capacity Estimates
    console.print("\n[bold yellow]🎯 Estimated Lab Deployment Capacity:[/bold yellow]")
    
    # Simple capacity estimates based on typical device requirements
    small_vms = max_ram_gb // 1  # 1GB per small VM
    medium_vms = max_ram_gb // 2  # 2GB per medium VM
    large_vms = max_ram_gb // 4   # 4GB per large VM
    
    capacity_table = Table(show_header=True, header_style="bold blue")
    capacity_table.add_column("Lab Size", style="cyan")
    capacity_table.add_column("VM Count", justify="right")
    capacity_table.add_column("Example Scenario", style="dim")
    
    capacity_table.add_row(
        "Small VMs (1GB RAM, 20GB disk)",
        f"~{small_vms} VMs",
        "Routers, switches, lightweight endpoints"
    )
    capacity_table.add_row(
        "Medium VMs (2GB RAM, 40GB disk)",
        f"~{medium_vms} VMs",
        "Servers, firewalls, desktop endpoints"
    )
    capacity_table.add_row(
        "Large VMs (4GB RAM, 80GB disk)",
        f"~{large_vms} VMs",
        "Windows servers, complex applications"
    )
    
    console.print(capacity_table)
    
    # Recommendations
    console.print("\n[bold yellow]💡 Recommendations:[/bold yellow]")
    
    if ram_gb < 8:
        console.print("• Consider upgrading RAM to 16GB+ for better lab capacity")
    if disk_gb < 200:
        console.print("• Consider allocating more disk space for VM images")
    if not resources.virtualization_enabled:
        console.print("• Enable VT-x/AMD-V in BIOS for VM support")
    
    if ram_gb >= 16 and disk_gb >= 200 and resources.virtualization_enabled:
        console.print("• ✅ Your system is well-suited for NetLab deployment!")
        console.print("• You can run complex multi-device network scenarios")


# Placeholder commands for the CLI structure
@app.command("backends")
def backends_command() -> None:
    """Show available backends and their status."""
    console.print("[bold blue]NetLab Backend Status[/bold blue]")
    console.print("=" * 50)
    
    try:
        backend_manager = BackendManager()
        capabilities = backend_manager.get_system_capabilities()
        
        # Compute Backends Table
        compute_table = Table(title="Compute Backends", show_header=True, header_style="bold green")
        compute_table.add_column("Backend", style="cyan")
        compute_table.add_column("Status", justify="center")
        compute_table.add_column("Description")
        
        compute_backends_info = {
            "vm_virtualbox": ("VirtualBox VM", "Full OS virtual machines"),
            "ctr_docker": ("Docker Container", "Lightweight containerized devices")
        }
        
        for backend_name, info in compute_backends_info.items():
            name, description = info
            is_available = backend_name in capabilities["compute_backends"]
            status = "[green]Available[/green]" if is_available else "[red]Not Available[/red]"
            compute_table.add_row(name, status, description)
        
        console.print(compute_table)
        
        # Network Backends Table
        network_table = Table(title="Network Backends", show_header=True, header_style="bold green")
        network_table.add_column("Backend", style="cyan")
        network_table.add_column("Status", justify="center")
        network_table.add_column("Description")
        
        network_backends_info = {
            "net_bridge": ("Bridge Network", "Layer 2 bridge networking")
        }
        
        for backend_name, info in network_backends_info.items():
            name, description = info
            is_available = backend_name in capabilities["network_backends"]
            status = "[green]Available[/green]" if is_available else "[red]Not Available[/red]"
            network_table.add_row(name, status, description)
        
        console.print(network_table)
        
        # Available Features
        if capabilities["available_features"]:
            console.print("\\n[bold yellow]Available Features:[/bold yellow]")
            for feature in capabilities["available_features"]:
                console.print(f"  • {feature.replace('_', ' ').title()}")
        
        # Recommendations
        console.print("\\n[bold yellow]Installation Status:[/bold yellow]")
        if not capabilities["compute_backends"]:
            console.print("  • [red]No compute backends available[/red]")
            console.print("  • Install VirtualBox or Docker to enable device deployment")
        elif len(capabilities["compute_backends"]) == 1:
            console.print("  • [yellow]Single compute backend available[/yellow]")
            console.print("  • Consider installing additional backends for flexibility")
        else:
            console.print("  • [green]Multiple compute backends available[/green]")
            console.print("  • System ready for flexible device deployment")
            
    except Exception as e:
        console.print(f"[bold red]Error checking backends: {e}[/bold red]")


@app.command("sources")
def sources_command() -> None:
    """Manage device source images."""
    console.print("[bold red]Sources management not yet implemented[/bold red]")
    console.print("This will manage downloading and verifying device images")


@app.command("catalog")  
def catalog_command() -> None:
    """Manage device catalog."""
    console.print("[bold red]Device catalog not yet implemented[/bold red]")
    console.print("This will show available devices and templates")


@app.command("plan")
def plan_command(
    topology_file: Path = typer.Argument(..., help="Topology YAML file to plan")
) -> None:
    """Plan a network topology deployment."""
    console.print(f"[bold blue]NetLab Deployment Plan[/bold blue]")
    console.print("=" * 50)
    
    try:
        # Load topology
        topology = TopologyLoader.load_from_file(topology_file)
        console.print(f"Topology: [bold]{topology.name}[/bold]")
        if topology.description:
            console.print(f"Description: {topology.description}")
        
        # Create deployment engine and plan
        engine = DeploymentEngine()
        plan = engine.plan_deployment(topology)
        
        # Show deployment feasibility
        if plan["can_deploy"]:
            console.print("[green]OK - Deployment is feasible[/green]")
        else:
            console.print("[red]ERROR - Deployment cannot proceed[/red]")
            for error in plan["errors"]:
                console.print(f"  [red]- {error}[/red]")
        
        # Resource requirements
        reqs = plan["resource_requirements"]
        console.print("\\n[bold yellow]Resource Requirements:[/bold yellow]")
        console.print(f"  Devices: {reqs['device_count']}")
        console.print(f"  Networks: {reqs['network_count']}")
        console.print(f"  Total RAM: {reqs['total_memory_gb']:.1f} GB")
        console.print(f"  Total CPU: {reqs['total_cpu_cores']} cores")
        
        # Networks table
        if plan["networks"]:
            console.print("\\n[bold yellow]Networks:[/bold yellow]")
            net_table = Table(show_header=True, header_style="bold cyan")
            net_table.add_column("Name")
            net_table.add_column("Subnet")
            net_table.add_column("Backend")
            
            for network in plan["networks"]:
                net_table.add_row(
                    network["name"],
                    network["subnet"], 
                    network["backend"]
                )
            console.print(net_table)
        
        # Devices table
        if plan["devices"]:
            console.print("\\n[bold yellow]Devices:[/bold yellow]")
            dev_table = Table(show_header=True, header_style="bold cyan")
            dev_table.add_column("Name")
            dev_table.add_column("Type")
            dev_table.add_column("Backend")
            dev_table.add_column("CPU")
            dev_table.add_column("RAM")
            dev_table.add_column("Disk")
            
            for device in plan["devices"]:
                dev_table.add_row(
                    device["name"],
                    device["device_type"],
                    device["backend"],
                    str(device["cpu_cores"]),
                    f"{device['memory_mb']}MB",
                    f"{device['disk_size_gb']}GB"
                )
            console.print(dev_table)
        
        # Warnings
        if plan["warnings"]:
            console.print("\\n[bold yellow]Warnings:[/bold yellow]")
            for warning in plan["warnings"]:
                console.print(f"  [yellow]- {warning}[/yellow]")
        
    except Exception as e:
        console.print(f"[bold red]Error planning deployment: {e}[/bold red]")


@app.command("lab")
def lab_command() -> None:
    """Lab lifecycle management."""
    pass


# Add lab subcommands
lab_app = typer.Typer(help="Lab lifecycle management")
app.add_typer(lab_app, name="lab")


@lab_app.command("up")
def lab_up(
    topology_file: Path = typer.Argument(..., help="Topology YAML file")
) -> None:
    """Deploy a network topology."""
    console.print(f"[bold blue]NetLab Lab Deployment[/bold blue]")
    console.print("=" * 50)
    
    try:
        # Load topology
        topology = TopologyLoader.load_from_file(topology_file)
        console.print(f"Deploying topology: [bold]{topology.name}[/bold]")
        
        # Deploy
        engine = DeploymentEngine()
        deployment = engine.deploy_topology(topology)
        
        # Show results
        if deployment["status"] == "running":
            console.print("[green]OK - Deployment completed successfully[/green]")
        elif deployment["status"] == "partial":
            console.print("[yellow]WARNING - Deployment completed with warnings[/yellow]")
        else:
            console.print("[red]ERROR - Deployment failed[/red]")
        
        console.print(f"Deployment ID: [bold]{deployment['id']}[/bold]")
        console.print(f"Duration: {deployment['duration']:.1f} seconds")
        
        # Show created resources
        if deployment["networks"]:
            console.print("\\n[bold yellow]Networks Created:[/bold yellow]")
            for name, info in deployment["networks"].items():
                status = "[green]OK[/green]" if info["status"] == "created" else "[red]FAILED[/red]"
                console.print(f"  {name}: {info['subnet']} {status}")
        
        if deployment["devices"]:
            console.print("\\n[bold yellow]Devices Created:[/bold yellow]")
            for name, info in deployment["devices"].items():
                status_color = "green" if info["status"] == "running" else "yellow"
                console.print(f"  {name}: [{status_color}]{info['status'].upper()}[/{status_color}] ({info['backend']})")
        
        # Show errors
        if deployment["errors"]:
            console.print("\\n[bold red]Errors:[/bold red]")
            for error in deployment["errors"]:
                console.print(f"  [red]- {error}[/red]")
        
        # Next steps
        console.print("\\n[bold yellow]Next Steps:[/bold yellow]")
        console.print(f"- [blue]uvdnl lab status {deployment['id']}[/blue] - Check status")
        console.print(f"- [blue]uvdnl lab down {deployment['id']}[/blue] - Destroy lab")
        
    except Exception as e:
        console.print(f"[bold red]Error deploying topology: {e}[/bold red]")


@lab_app.command("down")
def lab_down(
    topology_file: Path = typer.Argument(..., help="Topology YAML file")
) -> None:
    """Destroy a network topology."""
    console.print(f"[bold red]Lab destruction not yet implemented[/bold red]")
    console.print(f"Would destroy: {topology_file}")


@lab_app.command("status")
def lab_status(
    topology_file: Optional[Path] = typer.Argument(None, help="Topology YAML file")
) -> None:
    """Show lab status."""
    console.print(f"[bold red]Lab status not yet implemented[/bold red]")
    if topology_file:
        console.print(f"Would show status for: {topology_file}")
    else:
        console.print("Would show status for all labs")


if __name__ == "__main__":
    app()