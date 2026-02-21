"""
系統配置管理
"""

from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings


class GatewayConfig(BaseModel):
    """Gateway 配置"""

    host: str = "127.0.0.1"
    port: int = 8002
    debug: bool = False
    reload: bool = False

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"


class ProviderConfig(BaseModel):
    """單一 Provider 配置"""

    api_key: str = ""
    base_url: str | None = None
    model: str = ""
    max_tokens: int = 4096
    temperature: float = 0.7


class ProvidersConfig(BaseModel):
    """所有 Provider 配置"""

    openai: ProviderConfig | None = None
    anthropic: ProviderConfig | None = None
    ollama: ProviderConfig | None = None


class AgentConfig(BaseModel):
    """Agent 配置"""

    default_provider: str = "openai"
    max_tokens: int = 4096
    temperature: float = 0.7
    system_prompt: str = "You are a helpful AI assistant."


class ToolsConfig(BaseModel):
    """Tools 配置"""

    web_enabled: bool = True
    web_headless: bool = True
    shell_enabled: bool = True
    shell_sandbox: bool = True
    file_enabled: bool = True
    mysql_enabled: bool = False


class Settings(BaseSettings):
    """系統設定"""

    model_config = {
        "env_prefix": "MARTLET_",
        "env_file": ".env",
        "env_nested_delimiter": "__",
        "extra": "ignore",
    }

    # 系統識別
    system_name: str = "b"
    system_id: str = "martlet_molt_b"

    # 基礎設定
    debug: bool = False
    log_level: str = "INFO"

    # 路徑設定
    base_dir: Path = Path(".")
    data_dir: Path = Path("shared/data")
    logs_dir: Path = Path("shared/logs")

    # Gateway
    gateway: GatewayConfig = GatewayConfig()

    # Providers
    providers: ProvidersConfig = ProvidersConfig()

    # Agent
    agent: AgentConfig = AgentConfig()

    # Tools
    tools: ToolsConfig = ToolsConfig()


# 全域設定實例
settings = Settings()
