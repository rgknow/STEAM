import asyncio
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from steam.models import (
    Message, MessageRole, MessageType, SessionInfo, SessionStatus,
    CommandExecution, ApprovalDecision
)
from steam.config import get_settings
from steam.python_guardrails import get_python_guardrails

settings = get_settings()
guardrails = get_python_guardrails()


class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, "CodingSession"] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Start the background cleanup task."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_sessions())
    
    async def _cleanup_sessions(self):
        """Clean up expired sessions periodically."""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                now = datetime.now()
                expired_sessions = []
                
                for session_id, session in self._sessions.items():
                    if (now - session.last_activity).total_seconds() > settings.session_timeout:
                        expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    await self.terminate_session(session_id)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in session cleanup: {e}")
    
    async def create_session(self, session_id: Optional[str] = None) -> str:
        """Create a new coding session."""
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        if len(self._sessions) >= settings.max_sessions:
            # Remove oldest session
            oldest_session_id = min(
                self._sessions.keys(),
                key=lambda k: self._sessions[k].created_at
            )
            await self.terminate_session(oldest_session_id)
        
        session = CodingSession(session_id)
        self._sessions[session_id] = session
        return session_id
    
    async def get_session(self, session_id: str) -> Optional["CodingSession"]:
        """Get a session by ID."""
        session = self._sessions.get(session_id)
        if session:
            session.last_activity = datetime.now()
        return session
    
    async def terminate_session(self, session_id: str) -> bool:
        """Terminate a session."""
        if session_id in self._sessions:
            session = self._sessions[session_id]
            session.status = SessionStatus.TERMINATED
            del self._sessions[session_id]
            return True
        return False
    
    async def list_sessions(self) -> List[SessionInfo]:
        """List all active sessions."""
        return [session.get_info() for session in self._sessions.values()]
    
    async def cleanup(self):
        """Cleanup resources."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass


class CodingSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.status = SessionStatus.ACTIVE
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.current_directory = settings.workspace_root
        
        # Message history
        self.messages: List[Message] = []
        
        # Command execution history
        self.commands: Dict[str, CommandExecution] = {}
        
        # Context and state
        self.context: Dict[str, Any] = {}
        self.file_history: List[str] = []  # Recently accessed files
        
        # WebSocket connections
        self.websocket_connections = set()
    
    def add_message(self, content: str, role: MessageRole, 
                   message_type: MessageType = MessageType.TEXT,
                   metadata: Optional[Dict[str, Any]] = None) -> Message:
        """Add a message to the session history."""
        message = Message(
            id=str(uuid.uuid4()),
            role=role,
            content=content,
            message_type=message_type,
            metadata=metadata or {}
        )
        self.messages.append(message)
        self.last_activity = datetime.now()
        return message
    
    def add_command(self, command: str, cwd: Optional[str] = None, 
                   requires_approval: bool = False) -> CommandExecution:
        """Add a command execution to the session."""
        cmd_exec = CommandExecution(
            id=str(uuid.uuid4()),
            command=command,
            cwd=cwd or self.current_directory,
            requires_approval=requires_approval
        )
        self.commands[cmd_exec.id] = cmd_exec
        self.last_activity = datetime.now()
        return cmd_exec
    
    def approve_command(self, command_id: str, decision: ApprovalDecision,
                       modified_command: Optional[str] = None) -> bool:
        """Approve or reject a command execution."""
        if command_id not in self.commands:
            return False
        
        cmd_exec = self.commands[command_id]
        cmd_exec.approved = decision == ApprovalDecision.APPROVE
        
        if decision == ApprovalDecision.MODIFY and modified_command:
            cmd_exec.command = modified_command
            cmd_exec.approved = True
        
        self.last_activity = datetime.now()
        return True
    
    def update_command_result(self, command_id: str, output: Optional[str] = None,
                            error: Optional[str] = None, exit_code: Optional[int] = None):
        """Update command execution results."""
        if command_id in self.commands:
            cmd_exec = self.commands[command_id]
            cmd_exec.output = output
            cmd_exec.error = error
            cmd_exec.exit_code = exit_code
            self.last_activity = datetime.now()
    
    def get_recent_messages(self, limit: int = 10) -> List[Message]:
        """Get recent messages from the session."""
        return self.messages[-limit:] if self.messages else []
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of the current session context (Python-only mode)."""
        return {
            "session_id": self.session_id,
            "current_directory": self.current_directory,
            "message_count": len(self.messages),
            "recent_files": [f for f in self.file_history[-5:] if guardrails.is_python_related_file(f)],
            "pending_commands": [
                cmd.id for cmd in self.commands.values() 
                if cmd.requires_approval and cmd.approved is None
            ],
            "python_only_mode": True,
            "python_help": guardrails.get_python_help_text(),
            "context": self.context
        }
    
    def add_websocket(self, websocket):
        """Add a WebSocket connection to this session."""
        self.websocket_connections.add(websocket)
    
    def remove_websocket(self, websocket):
        """Remove a WebSocket connection from this session."""
        self.websocket_connections.discard(websocket)
    
    async def broadcast_to_websockets(self, message: Dict[str, Any]):
        """Broadcast a message to all connected WebSockets."""
        if not self.websocket_connections:
            return
        
        # Remove closed connections
        closed_connections = set()
        for ws in self.websocket_connections:
            try:
                await ws.send_json(message)
            except Exception:
                closed_connections.add(ws)
        
        # Clean up closed connections
        for ws in closed_connections:
            self.websocket_connections.discard(ws)
    
    def get_info(self) -> SessionInfo:
        """Get session information."""
        return SessionInfo(
            session_id=self.session_id,
            status=self.status,
            created_at=self.created_at,
            last_activity=self.last_activity,
            message_count=len(self.messages),
            current_directory=self.current_directory
        )


# Global session manager instance
session_manager = SessionManager()


async def get_session_manager() -> SessionManager:
    """Get the global session manager instance."""
    return session_manager