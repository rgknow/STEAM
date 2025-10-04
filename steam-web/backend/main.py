from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path

from steam.config import get_settings
from steam.models import (
    ChatRequest, ChatResponse, MessageRole, MessageType,
    ApprovalRequest, FileOperation, WebSocketMessage
)
from steam.session import get_session_manager, CodingSession
from steam.ai import get_ai_manager
from steam.filesystem import get_file_manager, get_command_executor

settings = get_settings()
app = FastAPI(title="STEAM Web Interface", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = Path(__file__).parent.parent / "frontend"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


@app.get("/")
async def serve_index():
    """Serve the main application page."""
    static_file = static_path / "index.html"
    if static_file.exists():
        return FileResponse(str(static_file))
    
    # Return a basic HTML page if frontend not built yet
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>STEAM Web Interface</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .status { padding: 20px; background: #f0f0f0; border-radius: 8px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>STEAM Web Interface</h1>
            <div class="status">
                <h3>Backend Status: Running ✅</h3>
                <p>The STEAM backend is running successfully!</p>
                <p>Frontend is still being built. WebSocket endpoint: <code>ws://localhost:8000/ws</code></p>
                <p>API Documentation: <a href="/docs">/docs</a></p>
            </div>
        </div>
    </body>
    </html>
    """)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "steam-web"}


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """Chat with the AI assistant."""
    session_manager = await get_session_manager()
    ai_manager = get_ai_manager()
    
    # Get or create session
    if request.session_id:
        session = await session_manager.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session_id = await session_manager.create_session()
        session = await session_manager.get_session(session_id)
    
    # Add user message to session
    session.add_message(request.message, MessageRole.USER)
    
    # Get AI response
    context = session.get_context_summary()
    context.update(request.context or {})
    
    try:
        response = await ai_manager.generate_response(
            session.get_recent_messages(),
            context
        )
        
        # Add AI response to session
        session.add_message(response, MessageRole.ASSISTANT)
        
        return ChatResponse(
            session_id=session.session_id,
            response=response,
            message_type=MessageType.TEXT
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/approve")
async def approve_command(request: ApprovalRequest):
    """Approve or reject a command execution."""
    session_manager = await get_session_manager()
    
    # Find session with the command
    for session_id in session_manager._sessions:
        session = session_manager._sessions[session_id]
        if request.command_id in session.commands:
            success = session.approve_command(
                request.command_id,
                request.decision,
                request.modified_command
            )
            if success:
                return {"status": "success", "command_id": request.command_id}
    
    raise HTTPException(status_code=404, detail="Command not found")


@app.get("/api/sessions")
async def list_sessions():
    """List all active sessions."""
    session_manager = await get_session_manager()
    sessions = await session_manager.list_sessions()
    return {"sessions": sessions}


@app.get("/api/providers")
async def list_ai_providers():
    """List available AI providers."""
    ai_manager = get_ai_manager()
    providers = ai_manager.list_providers()
    return {"providers": providers}


@app.post("/api/files")
async def file_operation(operation: FileOperation):
    """Perform file operations."""
    file_manager = get_file_manager()
    
    try:
        if operation.operation == "read":
            content = await file_manager.read_file(operation.path, operation.encoding)
            return {"content": content}
        
        elif operation.operation == "write":
            success = await file_manager.write_file(
                operation.path, 
                operation.content or "", 
                operation.encoding
            )
            return {"success": success}
        
        elif operation.operation == "create":
            success = await file_manager.create_file(
                operation.path, 
                operation.content or "", 
                operation.encoding
            )
            return {"success": success}
        
        elif operation.operation == "delete":
            success = await file_manager.delete_file(operation.path)
            return {"success": success}
        
        elif operation.operation == "list":
            files = await file_manager.list_directory(operation.path)
            return {"files": [f.dict() for f in files]}
        
        else:
            raise HTTPException(status_code=400, detail="Invalid operation")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication."""
    await websocket.accept()
    session: Optional[CodingSession] = None
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            msg_type = message.get("type")
            msg_data = message.get("data", {})
            session_id = message.get("session_id")
            
            session_manager = await get_session_manager()
            
            if msg_type == "join_session":
                # Join or create session
                if session_id:
                    session = await session_manager.get_session(session_id)
                if not session:
                    session_id = await session_manager.create_session(session_id)
                    session = await session_manager.get_session(session_id)
                
                session.add_websocket(websocket)
                
                await websocket.send_text(json.dumps({
                    "type": "session_joined",
                    "data": {"session_id": session.session_id}
                }))
            
            elif msg_type == "chat":
                if not session:
                    raise ValueError("No active session")
                
                user_message = msg_data.get("message", "")
                session.add_message(user_message, MessageRole.USER)
                
                # Broadcast user message to all clients
                await session.broadcast_to_websockets({
                    "type": "user_message",
                    "data": {"message": user_message, "timestamp": "now"}
                })
                
                # Get AI response
                ai_manager = get_ai_manager()
                context = session.get_context_summary()
                
                try:
                    # Send typing indicator
                    await session.broadcast_to_websockets({
                        "type": "ai_typing",
                        "data": {"typing": True}
                    })
                    
                    response = await ai_manager.generate_response(
                        session.get_recent_messages(),
                        context
                    )
                    
                    session.add_message(response, MessageRole.ASSISTANT)
                    
                    # Send AI response
                    await session.broadcast_to_websockets({
                        "type": "ai_response",
                        "data": {"message": response, "timestamp": "now"}
                    })
                    
                except Exception as e:
                    await session.broadcast_to_websockets({
                        "type": "error",
                        "data": {"message": f"AI Error: {str(e)}"}
                    })
                
                finally:
                    # Stop typing indicator
                    await session.broadcast_to_websockets({
                        "type": "ai_typing",
                        "data": {"typing": False}
                    })
            
            elif msg_type == "file_operation":
                if not session:
                    raise ValueError("No active session")
                
                file_manager = get_file_manager()
                op_type = msg_data.get("operation")
                path = msg_data.get("path")
                
                try:
                    if op_type == "list":
                        files = await file_manager.list_directory(path)
                        await websocket.send_text(json.dumps({
                            "type": "file_list",
                            "data": {"files": [f.dict() for f in files], "path": path}
                        }))
                    
                    elif op_type == "read":
                        content = await file_manager.read_file(path)
                        await websocket.send_text(json.dumps({
                            "type": "file_content",
                            "data": {"content": content, "path": path}
                        }))
                    
                    # Add more file operations as needed
                    
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "data": {"message": f"File operation error: {str(e)}"}
                    }))
            
            elif msg_type == "command":
                if not session:
                    raise ValueError("No active session")
                
                command = msg_data.get("command", "")
                cwd = msg_data.get("cwd")
                
                # Add command to session
                cmd_exec = session.add_command(command, cwd, requires_approval=True)
                
                # Request approval from user
                await session.broadcast_to_websockets({
                    "type": "command_approval_required",
                    "data": {
                        "command_id": cmd_exec.id,
                        "command": command,
                        "cwd": cwd or session.current_directory
                    }
                })

    except WebSocketDisconnect:
        if session:
            session.remove_websocket(websocket)
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "data": {"message": str(e)}
        }))
        if session:
            session.remove_websocket(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )