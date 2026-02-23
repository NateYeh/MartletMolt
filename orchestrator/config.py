"""
Orchestrator 配置管理
"""

from pathlib import Path

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings

# 動態獲取專案根目錄 (MartletMolt/)
BASE_DIR = Path(__file__).resolve().parent.parent


class HealthCheckConfig(BaseModel):
    """健康檢查配置"""

    interval: int = 30  # 檢查間隔（秒）
    retries: int = 3  # 重試次數
    timeout: int = 10  # 超時時間（秒）
    endpoint: str = "/health"  # 健康檢查端點


class SyncConfig(BaseModel):
    """同步配置"""

    enabled: bool = True
    exclude_patterns: list[str] = [
        "__pycache__",
        "*.pyc",
        ".git",
        ".venv",
        "node_modules",
        "*.log",
    ]


class SystemConfig(BaseModel):
    """單一系統配置"""

    name: str
    port: int
    host: str = "127.0.0.1"  # 內部通訊預設使用 localhost
    path: Path

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"


def load_yaml_config() -> dict:
    """從 Config/settings.yaml 載入配置"""
    yaml_path = BASE_DIR / "Config" / "settings.yaml"
    if yaml_path.exists():
        try:
            with open(yaml_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data.get("orchestrator", {})
        except Exception:
            return {}
    return {}


class OrchestratorSettings(BaseSettings):
    """Orchestrator 設定"""

    model_config = {"env_prefix": "MARTLET_", "env_file": ".env", "extra": "ignore"}

    # 基礎設定
    debug: bool = False
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000

    # 健康檢查
    health_check: HealthCheckConfig = HealthCheckConfig()

    # 同步設定
    sync: SyncConfig = SyncConfig()

    # 系統配置
    system_a: SystemConfig = SystemConfig(
        name="a",
        port=8001,
        path=Path("backend/system_a/martlet_molt"),
    )
    system_b: SystemConfig = SystemConfig(
        name="b",
        port=8002,
        path=Path("backend/system_b/martlet_molt"),
    )

    # 狀態檔案路徑
    state_file: Path = BASE_DIR / "shared" / "state" / "state.json"

    def __init__(self, **values):
        # 載入 YAML 設定並作為初始值
        yaml_data = load_yaml_config()
        # 優先合併 YAML 資料，但允許傳入的 values 覆蓋
        combined_values = {**yaml_data, **values}
        super().__init__(**combined_values)


# 全域設定實例
settings = OrchestratorSettings()
