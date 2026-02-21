"""
CLI 入口
"""

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from martlet_molt import __version__
from martlet_molt.core.config import settings
from martlet_molt.gateway.server import run_server

# Rich console
console = Console()

# Typer app
app = typer.Typer(name="martlet", help="MartletMolt - Self-Evolving AI Agent System")


@app.command()
def start(
    host: str = typer.Option(None, "--host", "-h", help="Host to bind"),
    port: int = typer.Option(None, "--port", "-p", help="Port to bind"),
    reload: bool = typer.Option(False, "--reload", "-r", help="Enable auto-reload"),
) -> None:
    """啟動服務"""
    if host:
        settings.gateway.host = host
    if port:
        settings.gateway.port = port
    if reload:
        settings.gateway.reload = reload

    console.print(f"[bold green]MartletMolt v{__version__}[/bold green]")
    console.print(f"[dim]Starting server on {settings.gateway.url}[/dim]")
    console.print()

    run_server()


@app.command()
def chat(
    session_id: Annotated[str, typer.Option("--session", "-s")] = "default",
    provider: str = typer.Option("openai", "--provider", "-p", help="AI Provider"),
) -> None:
    """CLI 對話模式"""
    console.print(f"[bold green]MartletMolt v{__version__}[/bold green]")
    console.print(f"[dim]Session: {session_id}[/dim]")
    console.print(f"[dim]Provider: {provider}[/dim]")
    console.print()
    console.print("[dim]Type 'exit' to quit, 'clear' to clear session.[/dim]")
    console.print()

    # TODO: 實現 CLI 對話
    console.print("[red]CLI chat mode not yet implemented[/red]")
    console.print("[dim]Use 'martlet start' to start the web server first.[/dim]")


@app.command()
def status() -> None:
    """顯示系統狀態"""
    console.print(f"[bold green]MartletMolt v{__version__}[/bold green]")
    console.print()

    table = Table(title="System Status")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("System Name", settings.system_name)
    table.add_row("Gateway URL", settings.gateway.url)
    table.add_row("Debug Mode", str(settings.debug))
    table.add_row("Log Level", settings.log_level)

    console.print(table)


@app.command()
def tools() -> None:
    """列出可用工具"""
    from martlet_molt.tools.base import ToolRegistry

    console.print("[bold green]Available Tools[/bold green]")
    console.print()

    registry = ToolRegistry()
    registry.register_defaults()

    table = Table()
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="white")

    for tool_name in registry.list_tools():
        tool = registry.get(tool_name)
        if tool:
            table.add_row(tool_name, tool.description[:50] + "..." if len(tool.description) > 50 else tool.description)

    console.print(table)


@app.command()
def config() -> None:
    """顯示配置"""
    console.print("[bold green]Current Configuration[/bold green]")
    console.print()

    console.print("[cyan]Gateway:[/cyan]")
    console.print(f"  Host: {settings.gateway.host}")
    console.print(f"  Port: {settings.gateway.port}")
    console.print(f"  Debug: {settings.gateway.debug}")

    console.print()
    console.print("[cyan]Agent:[/cyan]")
    console.print(f"  Default Provider: {settings.agent.default_provider}")
    console.print(f"  Max Tokens: {settings.agent.max_tokens}")
    console.print(f"  Temperature: {settings.agent.temperature}")

    console.print()
    console.print("[cyan]Tools:[/cyan]")
    console.print(f"  Web Enabled: {settings.tools.web_enabled}")
    console.print(f"  Shell Enabled: {settings.tools.shell_enabled}")
    console.print(f"  File Enabled: {settings.tools.file_enabled}")


def main() -> None:
    """主入口點"""
    app()


if __name__ == "__main__":
    main()
