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
    # 確保 settings 不會影響這裡，手動指定 sessions_dir
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
    
    # 確保在清單中
    assert session_id in session_manager.list_sessions()
    
    # 執行刪除
    success = session_manager.delete(session_id)
    assert success is True
    assert session_id not in session_manager.list_sessions()
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


# ==================== P0 穩定性增強測試 (SQLite 深層驗證) ====================

def test_message_persistence_and_ordering(session_manager):
    """測試訊息持久化與 Position 排序"""
    session_id = "order_test"
    session_manager.create(session_id)
    
    # 按順序添加三條訊息
    session_manager.add_message(session_id, "system", "Msg 1")
    session_manager.add_message(session_id, "user", "Msg 2")
    session_manager.add_message(session_id, "assistant", "Msg 3")
    
    # 清除緩存，強制從數據庫重新讀取
    session_manager._sessions.clear()
    session = session_manager.get(session_id)
    
    assert len(session.messages) == 3
    assert session.messages[0].content == "Msg 1"
    assert session.messages[1].content == "Msg 2"
    assert session.messages[2].content == "Msg 3"
    assert session.messages[0].role == "system"
    assert session.messages[2].role == "assistant"


def test_message_edit_workflow(session_manager):
    """測試訊息更新與刪除流程"""
    session_id = "edit_test"
    session_manager.create(session_id)
    
    msg = session_manager.add_message(session_id, "user", "Original Content")
    msg_id = msg.id
    
    # 1. 測試更新
    updated = session_manager.update_message(session_id, msg_id, content="Updated Content")
    assert updated.content == "Updated Content"
    
    # 確保緩存同步
    assert session_manager.get(session_id).messages[0].content == "Updated Content"
    
    # 再次清除緩存驗證數據庫持久化
    session_manager._sessions.clear()
    assert session_manager.get(session_id).messages[0].content == "Updated Content"
    
    # 2. 測試刪除單條訊息
    success = session_manager.delete_message(session_id, msg_id)
    assert success is True
    assert len(session_manager.get(session_id).messages) == 0


def test_cascade_delete_integrity(session_manager):
    """測試級聯刪除：刪除 Session 是否清理了 Messages 和 ToolCalls"""
    session_id = "cascade_test"
    session_manager.create(session_id)
    
    # 添加訊息與工具調用
    session_manager.add_message(session_id, "user", "Hello")
    session_manager.add_tool_call(session_id, "test_tool", {"arg": 1})
    
    # 執行刪除 Session
    session_manager.delete(session_id)
    
    # 直接檢查數據庫（確保底層清理乾淨）
    import sqlite3
    conn = sqlite3.connect(session_manager.db_path)
    cursor = conn.cursor()
    
    # 檢查 messages 表
    cursor.execute("SELECT count(*) FROM messages WHERE session_id = ?", (session_id,))
    assert cursor.fetchone()[0] == 0
    
    # 檢查 tool_calls 表
    cursor.execute("SELECT count(*) FROM tool_calls WHERE session_id = ?", (session_id,))
    assert cursor.fetchone()[0] == 0
    
    conn.close()
