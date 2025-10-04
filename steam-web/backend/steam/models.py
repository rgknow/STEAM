from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageType(str, Enum):
    TEXT = "text"
    CODE = "code"
    COMMAND = "command"
    FILE_EDIT = "file_edit"
    ERROR = "error"


class ApprovalDecision(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    MODIFY = "modify"


class SessionStatus(str, Enum):
    ACTIVE = "active"
    IDLE = "idle"
    TERMINATED = "terminated"


class Message(BaseModel):
    id: str
    role: MessageRole
    content: str
    message_type: MessageType = MessageType.TEXT
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None


class CodeEdit(BaseModel):
    file_path: str
    old_content: str
    new_content: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None


class CommandExecution(BaseModel):
    id: str
    command: str
    cwd: str
    requires_approval: bool = False
    approved: Optional[bool] = None
    output: Optional[str] = None
    error: Optional[str] = None
    exit_code: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class FileInfo(BaseModel):
    path: str
    name: str
    is_directory: bool
    size: Optional[int] = None
    modified: Optional[datetime] = None
    extension: Optional[str] = None


class SessionInfo(BaseModel):
    session_id: str
    status: SessionStatus
    created_at: datetime
    last_activity: datetime
    message_count: int
    current_directory: str


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    session_id: str
    response: str
    message_type: MessageType = MessageType.TEXT
    requires_approval: bool = False
    command_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ApprovalRequest(BaseModel):
    command_id: str
    decision: ApprovalDecision
    modified_command: Optional[str] = None


class FileOperation(BaseModel):
    operation: str  # read, write, create, delete, list
    path: str
    content: Optional[str] = None
    encoding: str = "utf-8"


class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    session_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)