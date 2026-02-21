"""
Web Lite - 獨立前端服務配置
"""

import os
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings


class BackendConfig(BaseModel):
    """後端 API 配置"""

    host: str = "127.0.0.1"
    port: int = 8001

    @property
    def url(self) -> str:
        """後端 API URL"""
        return f"http://{self.host}:{self.port}"

    @property
    def api_base(self) -> str:
        """API 基礎路徑"""
        return f"{self.url}/api"


class FrontendConfig(BaseModel):
    """前端服務配置"""

    host: str = "127.0.0.1"
    port: int = 8002
    debug: bool = False
    reload: bool = False

    @property
    def url(self) -> str:
        """前端服務 URL"""
        return f"http://{self.host}:{self.port}"


class Settings(BaseSettings):
    """Web Lite 設定"""

    model_config = {
        "env_prefix": "WEB_LITE_",
        "env_file": ".env",
        "env_nested_delimiter": "__",
        "extra": "ignore",
    }

    # 路徑設定
    base_dir: Path = Path(__file__).parent
    templates_dir: Path = Path(__file__).parent / "templates"
    static_dir: Path = Path(__file__).parent / "static"

    # 後端配置
    backend: BackendConfig = BackendConfig()

    # 前端配置
    frontend: FrontendConfig = FrontendConfig()

    # 基礎設定
    debug: bool = False
    log_level: str = "INFO"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # 從環境變數覆蓋後端配置
        if os.environ.get("BACKEND_HOST"):
            self.backend = BackendConfig(
                host=os.environ.get("BACKEND_HOST", "127.0.0.1"),
                port=int(os.environ.get("BACKEND_PORT", "8001")),
            )

        # 從環境變數覆蓋前端配置
        if os.environ.get("FRONTEND_PORT"):
            self.frontend = FrontendConfig(
                host=os.environ.get("FRONTEND_HOST", "127.0.0.1"),
                port=int(os.environ.get("FRONTEND_PORT", "8002")),
            )


# 全域設定實例
settings = Settings()
