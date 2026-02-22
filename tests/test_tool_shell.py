import pytest
from martlet_molt.tools.shell import ShellTool


@pytest.fixture
def shell_tool():
    return ShellTool()


def test_shell_basic_execution(shell_tool):
    """測試基本命令執行"""
    result = shell_tool.execute("echo 'hello martlet'")
    assert result.success is True
    assert "hello martlet" in result.data["stdout"]
    assert result.data["return_code"] == 0


def test_shell_error_execution(shell_tool):
    """測試錯誤命令執行"""
    result = shell_tool.execute("ls /path/to/non/existent/directory")
    assert result.success is False
    assert result.data["return_code"] != 0
    assert len(result.data["stderr"]) > 0


def test_shell_dangerous_command(shell_tool):
    """測試危險命令過濾"""
    # 假設 settings.tools.shell_sandbox 預設為 True
    result = shell_tool.execute("rm -rf /")
    assert result.success is False
    assert "Dangerous command detected" in result.error


def test_shell_timeout(shell_tool):
    """測試超時處理"""
    # 這裡用一個會睡 2 秒的命令，但設定 1 秒超時
    result = shell_tool.execute("sleep 2", timeout=1)
    assert result.success is False
    assert "timed out" in result.error
