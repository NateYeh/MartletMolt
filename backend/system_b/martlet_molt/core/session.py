"""
會話管理 - SQLite 數據庫版本

支持消息的增刪改查操作。
"""

import json
import sqlite3
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from loguru import logger
from pydantic import BaseModel, Field

from martlet_molt.core.config import settings
from martlet_molt.providers.base import Message as ProviderMessage


class Message(BaseModel):
    """訊息模型"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    role: str  # "user" | "assistant" | "system" | "tool"
    content: str
    name: str | None = None  # for tool messages
    tool_call_id: str | None = None
    tool_calls: list[dict] | None = None  # for assistant messages with tool calls
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class ToolCall(BaseModel):
    """工具調用"""

    id: str
    name: str
    arguments: dict
    result: str | None = None
    error: str | None = None


class Session(BaseModel):
    """會話模型"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    messages: list[Message] = []
    tool_calls: list[ToolCall] = []
    metadata: dict = {}

    def add_message(self, role: str, content: str, **kwargs) -> Message:
        """添加訊息（兼容舊接口，但不建議直接使用）"""
        message = Message(role=role, content=content, **kwargs)
        self.messages.append(message)
        self.updated_at = datetime.now().isoformat()
        return message

    def add_tool_call(self, name: str, arguments: dict) -> ToolCall:
        """添加工具調用（兼容舊接口，但不建議直接使用）"""
        tool_call = ToolCall(
            id=f"call_{uuid.uuid4().hex[:8]}",
            name=name,
            arguments=arguments,
        )
        self.tool_calls.append(tool_call)
        self.updated_at = datetime.now().isoformat()
        return tool_call

    def get_messages_for_api(self) -> list[ProviderMessage]:
        """
        取得用於 API 的訊息列表

        支援 OpenAI Tool Calling 格式:
        - assistant 訊息可能包含 tool_calls
        - tool 訊息需要 tool_call_id

        Returns:
            ProviderMessage 列表
        """
        api_messages: list[ProviderMessage] = []

        for msg in self.messages:
            # 基本訊息
            if msg.role in ["user", "system"]:
                api_messages.append(
                    ProviderMessage(
                        role=msg.role,
                        content=msg.content,
                    )
                )

            # Assistant 訊息（可能包含 tool_calls）
            elif msg.role == "assistant":
                api_messages.append(
                    ProviderMessage(
                        role=msg.role,
                        content=msg.content,
                        tool_calls=msg.tool_calls,
                    )
                )

            # Tool 結果訊息
            elif msg.role == "tool":
                api_messages.append(
                    ProviderMessage(
                        role=msg.role,
                        content=msg.content,
                        name=msg.name,
                        tool_call_id=msg.tool_call_id,
                    )
                )

        return api_messages


class SessionManager:
    """會話管理器 - SQLite 版本"""

    def __init__(self, sessions_dir: Path | None = None):
        self.sessions_dir = sessions_dir or settings.data_dir / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

        # 數據庫文件路徑
        self.db_path = self.sessions_dir / "sessions.db"

        # 初始化數據庫
        self._init_database()

        # 內存緩存
        self._sessions: dict[str, Session] = {}

    @contextmanager
    def _get_connection(self) -> Iterator[sqlite3.Connection]:
        """獲獲取數據庫連接（上下文管理器）"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        # 啟用外鍵約束，確保級聯刪除有效
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_database(self) -> None:
        """初始化數據庫表結構"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 創建會話表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT DEFAULT '{}'
                )
            """)

            # 創建消息表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT,
                    name TEXT,
                    tool_call_id TEXT,
                    tool_calls TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    position INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                )
            """)

            # 創建工具調用表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tool_calls (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    arguments TEXT,
                    result TEXT,
                    error TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                )
            """)

            # 創建索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_session
                ON messages(session_id, position)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tool_calls_session
                ON tool_calls(session_id)
            """)

    def create(self, session_id: str | None = None) -> Session:
        """建立新會話"""
        session = Session(id=session_id) if session_id else Session()

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 插入會話記錄
            cursor.execute(
                """
                INSERT INTO sessions (id, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?)
                """,
                (
                    session.id,
                    session.created_at,
                    session.updated_at,
                    json.dumps(session.metadata, ensure_ascii=False),
                ),
            )

        self._sessions[session.id] = session
        return session

    def get(self, session_id: str) -> Session | None:
        """取得會話"""
        # 先檢查緩存
        if session_id in self._sessions:
            return self._sessions[session_id]

        # 從數據庫載入
        session = self._load_session(session_id)
        if session:
            self._sessions[session_id] = session
        return session

    def get_or_create(self, session_id: str) -> Session:
        """取得或建立會話"""
        return self.get(session_id) or self.create(session_id)

    def save(self, session: Session) -> None:
        """儲存會話（更新會話元數據）"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 更新會話的 updated_at 和 metadata
            cursor.execute(
                """
                UPDATE sessions
                SET updated_at = ?, metadata = ?
                WHERE id = ?
                """,
                (
                    session.updated_at,
                    json.dumps(session.metadata, ensure_ascii=False),
                    session.id,
                ),
            )

            # 如果會話不存在，則創建
            if cursor.rowcount == 0:
                # 這個會話是新創建的，需要插入
                cursor.execute(
                    """
                    INSERT INTO sessions (id, created_at, updated_at, metadata)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        session.id,
                        session.created_at,
                        session.updated_at,
                        json.dumps(session.metadata, ensure_ascii=False),
                    ),
                )

        # 更新緩存
        self._sessions[session.id] = session

    def _load_session(self, session_id: str) -> Session | None:
        """從數據庫載入會話"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 查詢會話基本信息
            cursor.execute(
                """
                SELECT id, created_at, updated_at, metadata
                FROM sessions
                WHERE id = ?
                """,
                (session_id,),
            )

            row = cursor.fetchone()
            if not row:
                return None

            # 查詢消息
            cursor.execute(
                """
                SELECT id, role, content, name, tool_call_id, tool_calls, timestamp
                FROM messages
                WHERE session_id = ?
                ORDER BY position
                """,
                (session_id,),
            )

            messages = []
            for msg_row in cursor.fetchall():
                tool_calls = None
                if msg_row["tool_calls"]:
                    tool_calls = json.loads(msg_row["tool_calls"])

                messages.append(
                    Message(
                        id=msg_row["id"],
                        role=msg_row["role"],
                        content=msg_row["content"] or "",
                        name=msg_row["name"],
                        tool_call_id=msg_row["tool_call_id"],
                        tool_calls=tool_calls,
                        timestamp=msg_row["timestamp"],
                    )
                )

            # 查詢工具調用
            cursor.execute(
                """
                SELECT id, name, arguments, result, error
                FROM tool_calls
                WHERE session_id = ?
                ORDER BY created_at
                """,
                (session_id,),
            )

            tool_calls = []
            for tc_row in cursor.fetchall():
                tool_calls.append(
                    ToolCall(
                        id=tc_row["id"],
                        name=tc_row["name"],
                        arguments=json.loads(tc_row["arguments"] or "{}"),
                        result=tc_row["result"],
                        error=tc_row["error"],
                    )
                )

            return Session(
                id=row["id"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                messages=messages,
                tool_calls=tool_calls,
                metadata=json.loads(row["metadata"] or "{}"),
            )

    def list_sessions(self) -> list[str]:
        """列出所有會話 ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM sessions ORDER BY updated_at DESC")
            return [row["id"] for row in cursor.fetchall()]

    def get_session_info(self, session_id: str) -> dict | None:
        """取得會話基本資訊"""
        session = self.get(session_id)
        if not session:
            return None

        return {
            "id": session.id,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "message_count": len(session.messages),
            "tool_call_count": len(session.tool_calls),
            "metadata": session.metadata,
        }

    def delete_session(self, session_id: str) -> bool:
        """
        刪除整個會話

        Args:
            session_id: 會話 ID

        Returns:
            是否刪除成功
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            success = cursor.rowcount > 0

        # 清除緩存
        if session_id in self._sessions:
            del self._sessions[session_id]

        return success

    def delete(self, session_id: str) -> bool:
        """兼容舊接口的刪除方法"""
        return self.delete_session(session_id)

    def rename_session(self, session_id: str, new_title: str) -> bool:
        """
        重命名會話標題

        Args:
            session_id: 會話 ID
            new_title: 新標題

        Returns:
            是否成功
        """
        session = self.get(session_id)
        if not session:
            return False

        session.metadata["title"] = new_title
        session.updated_at = datetime.now().isoformat()
        self.save(session)

        logger.info(f"Session {session_id} renamed to: {new_title}")
        return True

    # ==================== 消息編輯功能 ====================

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        name: str | None = None,
        tool_call_id: str | None = None,
        tool_calls: list[dict] | None = None,
    ) -> Message:
        """
        添加消息到會話

        Args:
            session_id: 會話 ID
            role: 角色 (user/assistant/system/tool)
            content: 消息內容
            name: 工具名稱（tool 角色時使用）
            tool_call_id: 工具調用 ID（tool 角色時使用）
            tool_calls: 工具調用列表（assistant 角色時使用）

        Returns:
            創建的消息對象
        """
        message = Message(
            role=role,
            content=content,
            name=name,
            tool_call_id=tool_call_id,
            tool_calls=tool_calls,
        )

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 獲取當前最大 position
            cursor.execute(
                """
                SELECT COALESCE(MAX(position), -1) + 1 as next_position
                FROM messages
                WHERE session_id = ?
                """,
                (session_id,),
            )
            next_position = cursor.fetchone()["next_position"]

            # 插入消息
            cursor.execute(
                """
                INSERT INTO messages
                (id, session_id, role, content, name, tool_call_id, tool_calls, timestamp, position)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    message.id,
                    session_id,
                    role,
                    content,
                    name,
                    tool_call_id,
                    json.dumps(tool_calls, ensure_ascii=False) if tool_calls else None,
                    message.timestamp,
                    next_position,
                ),
            )

            # 更新會話的 updated_at
            now = datetime.now().isoformat()
            cursor.execute(
                "UPDATE sessions SET updated_at = ? WHERE id = ?",
                (now, session_id),
            )

        # 更新緩存
        if session_id in self._sessions:
            self._sessions[session_id].messages.append(message)
            self._sessions[session_id].updated_at = now

        return message

    def update_message(
        self,
        session_id: str,
        message_id: str,
        content: str | None = None,
        role: str | None = None,
        name: str | None = None,
        tool_call_id: str | None = None,
        tool_calls: list[dict] | None = None,
    ) -> Message | None:
        """
        更新消息

        Args:
            session_id: 會話 ID
            message_id: 消息 ID
            content: 新的內容（可選）
            role: 新的角色（可選）
            name: 新的名稱（可選）
            tool_call_id: 新的工具調用 ID（可選）
            tool_calls: 新的工具調用列表（可選）

        Returns:
            更新後的消息對象，如果消息不存在則返回 None
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 檢查消息是否存在
            cursor.execute(
                """
                SELECT id, role, content, name, tool_call_id, tool_calls, timestamp
                FROM messages
                WHERE id = ? AND session_id = ?
                """,
                (message_id, session_id),
            )

            row = cursor.fetchone()
            if not row:
                return None

            # 構建更新字段
            updates = []
            params = []

            if content is not None:
                updates.append("content = ?")
                params.append(content)

            if role is not None:
                updates.append("role = ?")
                params.append(role)

            if name is not None:
                updates.append("name = ?")
                params.append(name)

            if tool_call_id is not None:
                updates.append("tool_call_id = ?")
                params.append(tool_call_id)

            if tool_calls is not None:
                updates.append("tool_calls = ?")
                params.append(json.dumps(tool_calls, ensure_ascii=False))

            if not updates:
                # 沒有要更新的字段
                return Message(
                    id=row["id"],
                    role=row["role"],
                    content=row["content"] or "",
                    name=row["name"],
                    tool_call_id=row["tool_call_id"],
                    tool_calls=json.loads(row["tool_calls"]) if row["tool_calls"] else None,
                    timestamp=row["timestamp"],
                )

            # 添加 updated_at
            updates.append("updated_at = ?")
            now = datetime.now().isoformat()
            params.append(now)

            # 執行更新
            params.extend([message_id, session_id])
            cursor.execute(
                f"""
                UPDATE messages
                SET {", ".join(updates)}
                WHERE id = ? AND session_id = ?
                """,
                params,
            )

            # 更新會話的 updated_at
            cursor.execute(
                "UPDATE sessions SET updated_at = ? WHERE id = ?",
                (now, session_id),
            )

            # 構建更新後的消息對象
            updated_message = Message(
                id=message_id,
                role=role if role is not None else row["role"],
                content=content if content is not None else (row["content"] or ""),
                name=name if name is not None else row["name"],
                tool_call_id=tool_call_id if tool_call_id is not None else row["tool_call_id"],
                tool_calls=tool_calls if tool_calls is not None else (json.loads(row["tool_calls"]) if row["tool_calls"] else None),
                timestamp=row["timestamp"],
            )

        # 更新緩存
        if session_id in self._sessions:
            session = self._sessions[session_id]
            for i, msg in enumerate(session.messages):
                if msg.id == message_id:
                    session.messages[i] = updated_message
                    break
            session.updated_at = now

        return updated_message

    def delete_message(self, session_id: str, message_id: str) -> bool:
        """
        刪除消息

        Args:
            session_id: 會話 ID
            message_id: 消息 ID

        Returns:
            是否刪除成功
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 刪除消息
            cursor.execute(
                "DELETE FROM messages WHERE id = ? AND session_id = ?",
                (message_id, session_id),
            )

            success = cursor.rowcount > 0

            if success:
                # 更新會話的 updated_at
                now = datetime.now().isoformat()
                cursor.execute(
                    "UPDATE sessions SET updated_at = ? WHERE id = ?",
                    (now, session_id),
                )

        # 更新緩存
        if success and session_id in self._sessions:
            session = self._sessions[session_id]
            session.messages = [msg for msg in session.messages if msg.id != message_id]
            session.updated_at = now

        return success

    def get_message(self, session_id: str, message_id: str) -> Message | None:
        """
        獲取單個消息

        Args:
            session_id: 會話 ID
            message_id: 消息 ID

        Returns:
            消息對象，如果不存在則返回 None
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT id, role, content, name, tool_call_id, tool_calls, timestamp
                FROM messages
                WHERE id = ? AND session_id = ?
                """,
                (message_id, session_id),
            )

            row = cursor.fetchone()
            if not row:
                return None

            return Message(
                id=row["id"],
                role=row["role"],
                content=row["content"] or "",
                name=row["name"],
                tool_call_id=row["tool_call_id"],
                tool_calls=json.loads(row["tool_calls"]) if row["tool_calls"] else None,
                timestamp=row["timestamp"],
            )

    # ==================== 工具調用管理 ====================

    def add_tool_call(
        self,
        session_id: str,
        name: str,
        arguments: dict,
    ) -> ToolCall:
        """
        添加工具調用記錄

        Args:
            session_id: 會話 ID
            name: 工具名稱
            arguments: 工具參數

        Returns:
            創建的工具調用對象
        """
        tool_call = ToolCall(
            id=f"call_{uuid.uuid4().hex[:8]}",
            name=name,
            arguments=arguments,
        )

        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO tool_calls (id, session_id, name, arguments)
                VALUES (?, ?, ?, ?)
                """,
                (
                    tool_call.id,
                    session_id,
                    name,
                    json.dumps(arguments, ensure_ascii=False),
                ),
            )

        # 更新緩存
        if session_id in self._sessions:
            self._sessions[session_id].tool_calls.append(tool_call)

        return tool_call

    def update_tool_call(
        self,
        session_id: str,
        tool_call_id: str,
        result: str | None = None,
        error: str | None = None,
    ) -> ToolCall | None:
        """
        更新工具調用結果

        Args:
            session_id: 會話 ID
            tool_call_id: 工具調用 ID
            result: 執行結果
            error: 錯誤信息

        Returns:
            更新後的工具調用對象，如果不存在則返回 None
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 更新
            cursor.execute(
                """
                UPDATE tool_calls
                SET result = ?, error = ?
                WHERE id = ? AND session_id = ?
                """,
                (result, error, tool_call_id, session_id),
            )

            if cursor.rowcount == 0:
                return None

            # 查詢更新後的記錄
            cursor.execute(
                """
                SELECT id, name, arguments, result, error
                FROM tool_calls
                WHERE id = ?
                """,
                (tool_call_id,),
            )

            row = cursor.fetchone()
            updated_tool_call = ToolCall(
                id=row["id"],
                name=row["name"],
                arguments=json.loads(row["arguments"] or "{}"),
                result=row["result"],
                error=row["error"],
            )

        # 更新緩存
        if session_id in self._sessions:
            session = self._sessions[session_id]
            for i, tc in enumerate(session.tool_calls):
                if tc.id == tool_call_id:
                    session.tool_calls[i] = updated_tool_call
                    break

        return updated_tool_call


# 全域會話管理器
session_manager = SessionManager()
