import os
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest
import yaml
from martlet_molt.core.config import Settings, _resolve_env_vars, GatewayConfig


def test_resolve_env_vars():
    """測試環境變數替換"""
    os.environ["TEST_KEY"] = "test_value"
    config = {"key": "prefix-${TEST_KEY}-suffix"}
    resolved = _resolve_env_vars(config)
    assert resolved["key"] == "prefix-test_value-suffix"


def test_gateway_config_url():
    """測試 GatewayConfig 的 URL 生成"""
    config = GatewayConfig(host="127.0.0.1", port=9000)
    assert config.url == "http://127.0.0.1:9000"


def test_settings_default_values():
    """測試 Settings 的預設值"""
    with patch("martlet_molt.core.config.load_yaml_config", return_value={}):
        settings = Settings()
        assert settings.system_name == "a"
        assert settings.agent.default_provider == "ollama"
        assert settings.gateway.port == 8001


def test_settings_yaml_loading():
    """測試從 YAML 載入配置"""
    mock_yaml = {
        "gateway": {"port": 9999},
        "agent": {"default_provider": "openai"},
        "tools": {"web_enabled": False}
    }
    
    with patch("martlet_molt.core.config.load_yaml_config", return_value=mock_yaml):
        settings = Settings()
        assert settings.gateway.port == 9999
        assert settings.agent.default_provider == "openai"
        assert settings.tools.web_enabled is False


def test_env_var_override():
    """測試環境變數覆蓋"""
    with patch("martlet_molt.core.config.load_yaml_config", return_value={}):
        os.environ["MARTLET_SYSTEM_NAME"] = "b"
        settings = Settings()
        assert settings.system_name == "b"
