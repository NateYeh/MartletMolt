"""
會話管理
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field

from martlet_molt.core.config import settings


class Message(BaseModel):
    """訊息模型"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    role: str  # "user" | "assistant" | "system" | "tool"
    content: str
    name: str | None = None  # for tool messages
    tool_call_id: str | None = None
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
        """添加訊息"""
        message = Message(role=role, content=content, **kwargs)
        self.messages.append(message)
        self.updated_at = datetime.now().isoformat()
        return message

    def add_tool_call(self, name: str, arguments: dict) -> ToolCall:
        """添加工具調用"""
        tool_call = ToolCall(
            id=f"call_{uuid.uuid4().hex[:8]}",
            name=name,
            arguments=arguments,
        )
        self.tool_calls.append(tool_call)
        self.updated_at = datetime.now().isoformat()
        return tool_call

    def get_messages_for_api(self) -> list[dict]:
        """取得用於 API 的訊息列表"""
        return [{"role": msg.role, "content": msg.content} for msg in self.messages if msg.role in ["user", "assistant", "system"]]


class SessionManager:
    """會話管理器"""

    def __init__(self, sessions_dir: Path | None = None):
        self.sessions_dir = sessions_dir or settings.data_dir / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self._sessions: dict[str, Session] = {}

    def create(self, session_id: str | None = None) -> Session:
        """建立新會話"""
        session = Session(id=session_id) if session_id else Session()
        self._sessions[session.id] = session
        self._save_session(session)
        return session

    def get(self, session_id: str) -> Session | None:
        """取得會話"""
        if session_id in self._sessions:
            return self._sessions[session_id]

        # 從檔案載入
        session = self._load_session(session_id)
        if session:
            self._sessions[session_id] = session
        return session

    def get_or_create(self, session_id: str) -> Session:
        """取得或建立會話"""
        return self.get(session_id) or self.create(session_id)

    def save(self, session: Session) -> None:
        """儲存會話"""
        self._save_session(session)

    def _save_session(self, session: Session) -> None:
        """儲存會話到檔案"""
        file_path = self.sessions_dir / f"{session.id}.jsonl"
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(session.model_dump(), ensure_ascii=False) + "\n")

    def _load_session(self, session_id: str) -> Session | None:
        """從檔案載入會話"""
        file_path = self.sessions_dir / f"{session_id}.jsonl"
        if not file_path.exists():
            return None

        try:
            # 讀取最後一行（最新狀態）
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()
                if lines:
                    data = json.loads(lines[-1])
                    return Session(**data)
        except Exception:
            pass

        return None

    def list_sessions(self) -> list[str]:
        """列出所有會話 ID"""
        sessions = []
        for file in self.sessions_dir.glob("*.jsonl"):
            sessions.append(file.stem)
        return sorted(sessions)


# 全域會話管理器
session_manager = SessionManager()
