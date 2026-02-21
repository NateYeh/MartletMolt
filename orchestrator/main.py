"""
Orchestrator 主入口點
"""

import signal
import sys

import typer
from loguru import logger
from rich.console import Console
from rich.table import Table

from orchestrator import __version__
from orchestrator.config import settings
from orchestrator.health_check import health_checker
from orchestrator.manager import process_manager
from orchestrator.state import state_manager
from orchestrator.switcher import switcher

# 設定 loguru
logger.remove()
logger.add(
    sys.stderr,
    level=settings.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)

# Rich console
console = Console()

# Typer app
app = typer.Typer(name="orchestrator", help="MartletMolt Orchestrator")


@app.command()
def start(
    system: str | None = typer.Option(None, "--system", "-s", help="指定啟動的系統 (a/b)"),
    daemon: bool = typer.Option(False, "--daemon", "-d", help="以守護程序運行"),
) -> None:
    """啟動 Orchestrator"""
    console.print(f"[bold green]MartletMolt Orchestrator v{__version__}[/bold green]")
    console.print(f"[dim]Log Level: {settings.log_level}[/dim]")
    console.print()

    # 註冊信號處理
    def signal_handler(sig, frame):
        console.print("\n[yellow]Shutting down...[/yellow]")
        process_manager.stop("a")
        process_manager.stop("b")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 啟動系統
    system = system or state_manager.get_active_system()
    console.print(f"[cyan]Starting system {system}...[/cyan]")

    if process_manager.start(system):
        console.print(f"[green]System {system} started successfully[/green]")
        console.print(f"[dim]URL: {getattr(settings, f'system_{system}').url}[/dim]")
    else:
        console.print(f"[red]Failed to start system {system}[/red]")
        raise typer.Exit(1)

    if daemon:
        # 守護程序模式：持續運行並監控
        import time

        console.print("[dim]Running in daemon mode...[/dim]")
        while True:
            time.sleep(settings.health_check.interval)
            # 健康檢查
            active = state_manager.get_active_system()
            active_config = getattr(settings, f"system_{active}")
            health = health_checker.check(active_config.url)

            if health.status != "running":
                logger.warning(f"System {active} health check failed, attempting restart")
                process_manager.restart(active)


@app.command()
def stop() -> None:
    """停止所有系統"""
    console.print("[yellow]Stopping all systems...[/yellow]")
    process_manager.stop("a")
    process_manager.stop("b")
    console.print("[green]All systems stopped[/green]")


@app.command()
def status() -> None:
    """顯示系統狀態"""
    state = state_manager.state

    table = Table(title="MartletMolt Status")
    table.add_column("System", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Port", style="green")
    table.add_column("Active", style="bold")

    for sys_name in ["a", "b"]:
        sys_config = getattr(settings, f"system_{sys_name}")
        health = state.health_status.get(sys_name)
        is_active = state.active == sys_name

        status_str = health.status if health else "unknown"
        active_str = "✓" if is_active else ""

        table.add_row(
            f"System {sys_name.upper()}",
            status_str,
            str(sys_config.port),
            active_str,
        )

    console.print(table)


@app.command()
def switch(
    target: str = typer.Argument(..., help="目標系統 (a/b)"),
) -> None:
    """切換系統"""
    if target not in ["a", "b"]:
        console.print("[red]Invalid target. Use 'a' or 'b'.[/red]")
        raise typer.Exit(1)

    console.print(f"[cyan]Switching to system {target}...[/cyan]")

    if switcher.switch(target):
        console.print(f"[green]Successfully switched to system {target}[/green]")
    else:
        console.print(f"[red]Failed to switch to system {target}[/red]")
        raise typer.Exit(1)


@app.command()
def evolve(
    system: str = typer.Argument(..., help="被修改的系統 (a/b)"),
) -> None:
    """執行進化流程"""
    if system not in ["a", "b"]:
        console.print("[red]Invalid system. Use 'a' or 'b'.[/red]")
        raise typer.Exit(1)

    console.print(f"[cyan]Starting evolution with system {system}...[/cyan]")

    if switcher.evolve(system):
        console.print("[green]Evolution successful![/green]")
    else:
        console.print("[red]Evolution failed![/red]")
        raise typer.Exit(1)


@app.command()
def doctor() -> None:
    """診斷系統"""
    console.print("[bold]MartletMolt Doctor[/bold]\n")

    # 檢查狀態
    console.print("[cyan]Checking state file...[/cyan]")
    state = state_manager.state
    console.print(f"  Active system: {state.active}")
    console.print(f"  Version: A={state.version.a}, B={state.version.b}")

    # 檢查系統
    console.print("\n[cyan]Checking systems...[/cyan]")
    for sys_name in ["a", "b"]:
        sys_config = getattr(settings, f"system_{sys_name}")
        health = health_checker.check(sys_config.url)
        status_icon = "✓" if health.status == "running" else "✗"
        color = "green" if health.status == "running" else "red"
        console.print(f"  System {sys_name.upper()}: [{color}]{status_icon} {health.status}[/{color}]")

    # 檢查目錄
    console.print("\n[cyan]Checking directories...[/cyan]")
    for sys_name in ["a", "b"]:
        sys_config = getattr(settings, f"system_{sys_name}")
        path = sys_config.path
        exists = path.exists()
        status_icon = "✓" if exists else "✗"
        color = "green" if exists else "red"
        console.print(f"  {path}: [{color}]{status_icon}[/{color}]")


def main() -> None:
    """主入口點"""
    app()


if __name__ == "__main__":
    main()
