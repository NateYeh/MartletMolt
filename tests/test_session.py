import shutil
import tempfile
from pathlib import Path

import pytest
from martlet_molt.core.session import Session, SessionManager


@pytest.fixture
def temp_session_dir():
    """建立臨時會話目錄"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def session_manager(temp_session_dir):
    """建立測試用的會話管理器"""
    return SessionManager(sessions_dir=temp_session_dir)


def test_session_message_creation():
    """測試訊息建立"""
    session = Session(id="test_s_1")
    session.add_message("user", "Hello AI")
    
    assert len(session.messages) == 1
    assert session.messages[0].role == "user"
    assert session.messages[0].content == "Hello AI"
    assert session.id == "test_s_1"


def test_session_tool_call():
    """測試工具調用添加"""
    session = Session()
    tool_call = session.add_tool_call("shell", {"command": "ls"})
    
    assert len(session.tool_calls) == 1
    assert tool_call.name == "shell"
    assert tool_call.arguments == {"command": "ls"}
    assert tool_call.id.startswith("call_")


def test_manager_create_and_get(session_manager):
    """測試管理器建立與讀取"""
    session = session_manager.create("new_session")
    assert session.id == "new_session"
    
    # 確保記憶體緩存有效
    cached_session = session_manager.get("new_session")
    assert cached_session is session
    
    # 測試自動載入
    session_manager._sessions.clear()  # 清除記憶體緩存
    loaded_session = session_manager.get("new_session")
    assert loaded_session is not None
    assert loaded_session.id == "new_session"


def test_manager_delete(session_manager):
    """測試刪除會話"""
    session_id = "to_delete"
    session_manager.create(session_id)
    
    # 確認檔案存在
    file_path = session_manager.sessions_dir / f"{session_id}.jsonl"
    assert file_path.exists()
    
    # 執行刪除
    success = session_manager.delete(session_id)
    assert success is True
    assert not file_path.exists()
    assert session_id not in session_manager._sessions


def test_session_get_messages_for_api():
    """測試轉換為 API 格式"""
    session = Session()
    session.add_message("system", "You are a helpful assistant")
    session.add_message("user", "Hi")
    session.add_message("assistant", "Hello!", tool_calls=[{"id": "1", "type": "function"}])
    session.add_message("tool", "result", name="my_tool", tool_call_id="1")
    
    api_msgs = session.get_messages_for_api()
    assert len(api_msgs) == 4
    assert api_msgs[0].role == "system"
    assert api_msgs[1].role == "user"
    assert api_msgs[2].role == "assistant"
    assert api_msgs[3].role == "tool"
    assert api_msgs[3].tool_call_id == "1"
