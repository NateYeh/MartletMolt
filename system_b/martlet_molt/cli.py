"""
CLI 入口
"""

import asyncio

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from martlet_molt import __version__
from martlet_molt.core.agent import Agent
from martlet_molt.core.config import settings
from martlet_molt.core.session import Session, session_manager
from martlet_molt.gateway.server import run_server
from martlet_molt.providers.base import BaseProvider
from martlet_molt.providers.ollama import OllamaProvider
from martlet_molt.providers.openai import OpenAIProvider

# Rich console
console = Console()

# Typer app
app = typer.Typer(name="martlet", help="MartletMolt - Self-Evolving AI Agent System")


def get_provider(provider_name: str | None = None) -> BaseProvider:
    """
    根據配置取得 Provider 實例

    Args:
        provider_name: Provider 名稱，若為 None 則使用配置中的預設值

    Returns:
        Provider 實例

    Raises:
        ValueError: Provider 未配置或不支援
    """
    name = provider_name or settings.agent.default_provider
    provider_config = getattr(settings.providers, name, None)

    if not provider_config:
        raise ValueError(f"Provider '{name}' not configured")

    if name == "ollama":
        return OllamaProvider(
            api_key=provider_config.api_key,
            base_url=provider_config.base_url or "https://ollama.com",
            model=provider_config.model,
            max_tokens=provider_config.max_tokens,
            temperature=provider_config.temperature,
        )
    elif name == "openai":
        return OpenAIProvider(
            api_key=provider_config.api_key,
            base_url=provider_config.base_url,
            model=provider_config.model,
            max_tokens=provider_config.max_tokens,
            temperature=provider_config.temperature,
        )
    else:
        raise ValueError(f"Unsupported provider: {name}")


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
    message: str = typer.Argument(None, help="對話訊息（單次對話模式）"),
    session_id: str = typer.Option("default", "--session", "-s", help="會話 ID"),
    provider: str = typer.Option("", "--provider", "-p", help="AI Provider"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="進入互動模式"),
) -> None:
    """
    CLI 對話模式

    用法:
        martlet chat "你好"              # 單次對話
        martlet chat 你好                # 單次對話（無空格可省略引號）
        martlet chat -i                  # 互動模式
        martlet chat -p openai "你好"    # 指定 Provider
    """
    provider_name = provider or settings.agent.default_provider

    # 單次對話模式
    if message and not interactive:
        asyncio.run(_chat_once(message, session_id, provider_name))
        return

    # 互動模式
    asyncio.run(_chat_interactive(session_id, provider_name))


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


def _display_history(session: "Session", max_messages: int = 10) -> None:
    """
    顯示會話歷史記錄

    Args:
        session: 會話實例
        max_messages: 最多顯示的訊息數量
    """
    # 過濾出 user 和 assistant 訊息
    display_messages = [msg for msg in session.messages if msg.role in ("user", "assistant") and msg.content]

    if not display_messages:
        return

    # 顯示最近 N 條
    recent_messages = display_messages[-max_messages:] if len(display_messages) > max_messages else display_messages

    console.print()
    console.print(Panel(f"[bold]📝 最近 {len(recent_messages)} 條對話記錄[/bold]", border_style="yellow"))

    for msg in recent_messages:
        if msg.role == "user":
            # 用戶訊息 - 藍色
            content = msg.content[:200] + "..." if len(msg.content) > 200 else msg.content
            console.print(f"[bold blue]You:[/bold blue] {content}")
        elif msg.role == "assistant":
            # AI 訊息 - 綠色，簡潔顯示
            content = msg.content[:150] + "..." if len(msg.content) > 150 else msg.content
            content = content.replace("\n", " ").strip()  # 壓縮為一行
            console.print(f"[bold green]Assistant:[/bold green] {content}")

    console.print()


async def _chat_once(message: str, session_id: str, provider_name: str) -> None:
    """
    單次對話模式

    Args:
        message: 用戶訊息
        session_id: 會話 ID
        provider_name: Provider 名稱
    """
    console.print(f"[bold green]MartletMolt v{__version__}[/bold green]")
    console.print(f"[dim]Session: {session_id}[/dim]")
    console.print(f"[dim]Provider: {provider_name}[/dim]")

    try:
        # 建立 Provider 和 Agent
        provider = get_provider(provider_name)
        session = session_manager.get_or_create(session_id)
        agent = Agent(provider=provider, session=session)

        # 添加系統提示（如果是新會話）
        if len(session.messages) == 0 and settings.agent.system_prompt:
            agent.add_system_prompt(settings.agent.system_prompt)

        # 顯示歷史記錄
        if len(session.messages) > 0:
            _display_history(session, max_messages=10)

        # 顯示用戶訊息
        console.print(Panel(message, title="[bold blue]You[/bold blue]", border_style="blue"))

        # 發送請求並顯示回應
        with console.status("[bold green]Thinking...[/bold green]"):
            response = await agent.chat(message)

        # 顯示 AI 回應
        console.print()
        console.print(Panel(Markdown(response), title="[bold green]Assistant[/bold green]", border_style="green"))

    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("[dim]Please check your configuration in Config/settings.yaml[/dim]")
    except Exception:
        console.print("[red]An error occurred during chat.[/red]")

        from loguru import logger

        logger.exception("Chat error")


async def _chat_interactive(session_id: str, provider_name: str) -> None:
    """
    互動對話模式

    Args:
        session_id: 會話 ID
        provider_name: Provider 名稱
    """
    console.print(f"[bold green]MartletMolt v{__version__}[/bold green]")
    console.print(f"[dim]Session: {session_id}[/dim]")
    console.print(f"[dim]Provider: {provider_name}[/dim]")
    console.print("[dim]Commands: 'exit' to quit, 'clear' to clear session, 'new' for new session[/dim]")
    console.print()

    try:
        # 建立 Provider 和 Agent
        provider = get_provider(provider_name)
        session = session_manager.get_or_create(session_id)
        agent = Agent(provider=provider, session=session)

        # 添加系統提示（如果是新會話）
        if len(session.messages) == 0 and settings.agent.system_prompt:
            agent.add_system_prompt(settings.agent.system_prompt)

        # 顯示歷史記錄
        if len(session.messages) > 0:
            _display_history(session, max_messages=20)

        while True:
            try:
                # 讀取用戶輸入
                user_input = console.input("[bold blue]You:[bold blue] ").strip()

                if not user_input:
                    continue

                # 處理命令
                if user_input.lower() == "exit":
                    console.print("[dim]Goodbye![/dim]")
                    break
                elif user_input.lower() == "clear":
                    agent.reset()
                    console.print("[dim]Session cleared.[/dim]")
                    continue
                elif user_input.lower() == "new":
                    session_id = f"session_{__import__('uuid').uuid4().hex[:8]}"
                    session = session_manager.create(session_id)
                    agent = Agent(provider=provider, session=session)
                    if settings.agent.system_prompt:
                        agent.add_system_prompt(settings.agent.system_prompt)
                    console.print(f"[dim]New session created: {session_id}[/dim]")
                    continue

                # 發送請求並顯示回應
                with console.status("[bold green]Thinking...[/bold green]"):
                    response = await agent.chat(user_input)

                # 顯示 AI 回應
                console.print()
                console.print(Panel(Markdown(response), title="[bold green]Assistant[/bold green]", border_style="green"))
                console.print()

            except KeyboardInterrupt:
                console.print("\n[dim]Goodbye![/dim]")
                break

    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("[dim]Please check your configuration in Config/settings.yaml[/dim]")
    except Exception:
        console.print("[red]An error occurred during chat.[/red]")

        from loguru import logger

        logger.exception("Chat error")


def main() -> None:
    """主入口點"""
    app()


if __name__ == "__main__":
    main()
