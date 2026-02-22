"""
系統配置管理
"""

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class GatewayConfig(BaseModel):
    """Gateway 配置"""

    host: str = "0.0.0.0"
    port: int = 8001
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

    default_provider: str = "ollama"
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


def load_yaml_config() -> dict[str, Any]:
    """
    從 settings.yaml 載入配置

    Returns:
        配置字典
    """
    # 尋找配置檔路徑
    config_paths = [
        Path("Config/settings.yaml"),
        Path("../Config/settings.yaml"),
        Path("/mnt/work/py_works/external_projects/MartletMolt/Config/settings.yaml"),
    ]

    for config_path in config_paths:
        if config_path.exists():
            with open(config_path, encoding="utf-8") as f:
                config: dict[str, Any] = yaml.safe_load(f) or {}
                # 替換環境變數
                if config:
                    config = _resolve_env_vars(config)
                return config

    return {}


def _resolve_env_vars(obj):
    """
    遞迴替換配置中的環境變數

    支援 ${VAR_NAME} 格式

    Args:
        obj: 配置物件

    Returns:
        替換後的配置
    """
    import re

    if isinstance(obj, dict):
        return {k: _resolve_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_resolve_env_vars(item) for item in obj]
    elif isinstance(obj, str):
        # 匹配 ${VAR_NAME} 模式
        pattern = r"\$\{([^}]+)\}"
        matches = re.findall(pattern, obj)
        for var_name in matches:
            env_value = os.environ.get(var_name, "")
            obj = obj.replace(f"${{{var_name}}}", env_value)
        return obj
    return obj


class Settings(BaseSettings):
    """系統設定"""

    model_config = {
        "env_prefix": "MARTLET_",
        "env_file": ".env",
        "env_nested_delimiter": "__",
        "extra": "ignore",
    }

    # 系統識別
    system_name: str = "a"
    system_id: str = "martlet_molt_a"

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

    def __init__(self, **kwargs):
        # 先從 YAML 載入配置
        yaml_config = load_yaml_config()

        # 合併 kwargs (kwargs 優先)
        merged = {**yaml_config, **kwargs}

        # 呼叫父類初始化
        super().__init__(**merged)

        # 如果 YAML 中有 gateway 配置，更新它
        if "gateway" in yaml_config:
            self.gateway = GatewayConfig(**yaml_config["gateway"])

        # 如果 YAML 中有 providers 配置，更新它
        if "providers" in yaml_config:
            providers_data = {}
            for name, config in yaml_config["providers"].items():
                if config:
                    providers_data[name] = ProviderConfig(**config)
            if providers_data:
                self.providers = ProvidersConfig(**providers_data)

        # 如果 YAML 中有 agent 配置，更新它
        if "agent" in yaml_config:
            self.agent = AgentConfig(**yaml_config["agent"])

        # 如果 YAML 中有 tools 配置，更新它
        if "tools" in yaml_config:
            self.tools = ToolsConfig(**yaml_config["tools"])


# 全域設定實例
settings = Settings()
