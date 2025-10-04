import os
import asyncio
import subprocess
from typing import Optional, Dict, Any, List
from pathlib import Path
import aiofiles
import aiofiles.os
from steam.models import FileInfo, FileOperation
from steam.config import get_settings
from steam.python_guardrails import get_python_guardrails
from datetime import datetime

settings = get_settings()
guardrails = get_python_guardrails()


class FileSystemManager:
    def __init__(self, workspace_root: str = None):
        self.workspace_root = Path(workspace_root or settings.workspace_root)
        self.allowed_extensions = set(settings.allowed_extensions)
    
    def _is_safe_path(self, path: str) -> bool:
        """Check if the path is safe and within workspace."""
        try:
            resolved_path = Path(path).resolve()
            workspace_resolved = self.workspace_root.resolve()
            return str(resolved_path).startswith(str(workspace_resolved))
        except Exception:
            return False
    
    def _is_allowed_file(self, path: str) -> bool:
        """Check if file extension is allowed (Python-only mode)."""
        if Path(path).is_dir():
            return guardrails.is_safe_directory(path)
        
        # Use Python guardrails for file validation
        return guardrails.is_python_related_file(path)
    
    async def list_directory(self, path: str) -> List[FileInfo]:
        """List files and directories in the given path (Python-only mode)."""
        if not self._is_safe_path(path):
            raise ValueError(f"Path not allowed: {path}")
        
        # Validate directory access with guardrails
        is_valid, error_msg = guardrails.validate_file_operation("list", path)
        if not is_valid:
            raise ValueError(error_msg)
        
        dir_path = Path(path)
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")
        
        if not dir_path.is_dir():
            raise ValueError(f"Path is not a directory: {path}")
        
        files = []
        try:
            for item in dir_path.iterdir():
                # Skip hidden files unless they're Python-related
                if item.name.startswith('.') and not item.name in {'.env', '.gitignore', '.python-version'}:
                    continue
                
                # Check if file/directory is allowed
                if not self._is_allowed_file(str(item)):
                    continue
                
                stat = item.stat()
                file_info = FileInfo(
                    path=str(item),
                    name=item.name,
                    is_directory=item.is_dir(),
                    size=stat.st_size if not item.is_dir() else None,
                    modified=datetime.fromtimestamp(stat.st_mtime),
                    extension=item.suffix.lower() if not item.is_dir() else None
                )
                files.append(file_info)
        except PermissionError:
            raise ValueError(f"Permission denied: {path}")
        
        # Sort: directories first, then Python files, then other files
        def sort_key(x):
            if x.is_directory:
                return (0, x.name.lower())
            elif guardrails.is_python_file(x.path):
                return (1, x.name.lower())
            else:
                return (2, x.name.lower())
        
        files.sort(key=sort_key)
        return files
    
    async def read_file(self, path: str, encoding: str = "utf-8") -> str:
        """Read file contents (Python-only mode)."""
        if not self._is_safe_path(path):
            raise ValueError(f"Path not allowed: {path}")
        
        # Validate file access with guardrails
        is_valid, error_msg = guardrails.validate_file_operation("read", path)
        if not is_valid:
            raise ValueError(error_msg)
        
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        if file_path.is_dir():
            raise ValueError(f"Path is a directory: {path}")
        
        try:
            async with aiofiles.open(file_path, 'r', encoding=encoding) as f:
                return await f.read()
        except UnicodeDecodeError:
            # Try binary mode for non-text files
            async with aiofiles.open(file_path, 'rb') as f:
                content = await f.read()
                return content.decode('utf-8', errors='replace')
    
    async def write_file(self, path: str, content: str, encoding: str = "utf-8") -> bool:
        """Write content to file (Python-only mode)."""
        if not self._is_safe_path(path):
            raise ValueError(f"Path not allowed: {path}")
        
        # Validate file write with guardrails
        is_valid, error_msg = guardrails.validate_file_operation("write", path)
        if not is_valid:
            raise ValueError(error_msg)
        
        file_path = Path(path)
        
        # Create directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            async with aiofiles.open(file_path, 'w', encoding=encoding) as f:
                await f.write(content)
            return True
        except Exception as e:
            raise ValueError(f"Failed to write file: {e}")
    
    async def create_file(self, path: str, content: str = "", encoding: str = "utf-8") -> bool:
        """Create a new file."""
        if not self._is_safe_path(path):
            raise ValueError(f"Path not allowed: {path}")
        
        file_path = Path(path)
        if file_path.exists():
            raise ValueError(f"File already exists: {path}")
        
        return await self.write_file(path, content, encoding)
    
    async def delete_file(self, path: str) -> bool:
        """Delete a file or directory."""
        if not self._is_safe_path(path):
            raise ValueError(f"Path not allowed: {path}")
        
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        try:
            if file_path.is_dir():
                # Remove directory and all contents
                import shutil
                shutil.rmtree(file_path)
            else:
                file_path.unlink()
            return True
        except Exception as e:
            raise ValueError(f"Failed to delete: {e}")
    
    async def create_directory(self, path: str) -> bool:
        """Create a directory."""
        if not self._is_safe_path(path):
            raise ValueError(f"Path not allowed: {path}")
        
        dir_path = Path(path)
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            raise ValueError(f"Failed to create directory: {e}")
    
    async def get_file_info(self, path: str) -> FileInfo:
        """Get information about a file or directory."""
        if not self._is_safe_path(path):
            raise ValueError(f"Path not allowed: {path}")
        
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        stat = file_path.stat()
        return FileInfo(
            path=str(file_path),
            name=file_path.name,
            is_directory=file_path.is_dir(),
            size=stat.st_size if not file_path.is_dir() else None,
            modified=datetime.fromtimestamp(stat.st_mtime),
            extension=file_path.suffix.lower() if not file_path.is_dir() else None
        )
    
    async def search_files(self, pattern: str, directory: str = None) -> List[FileInfo]:
        """Search for files matching a pattern."""
        search_dir = Path(directory) if directory else self.workspace_root
        
        if not self._is_safe_path(str(search_dir)):
            raise ValueError(f"Directory not allowed: {search_dir}")
        
        if not search_dir.exists() or not search_dir.is_dir():
            raise ValueError(f"Invalid search directory: {search_dir}")
        
        files = []
        try:
            for file_path in search_dir.rglob(pattern):
                if file_path.name.startswith('.'):
                    continue
                
                if self._is_safe_path(str(file_path)) and self._is_allowed_file(str(file_path)):
                    stat = file_path.stat()
                    file_info = FileInfo(
                        path=str(file_path),
                        name=file_path.name,
                        is_directory=file_path.is_dir(),
                        size=stat.st_size if not file_path.is_dir() else None,
                        modified=datetime.fromtimestamp(stat.st_mtime),
                        extension=file_path.suffix.lower() if not file_path.is_dir() else None
                    )
                    files.append(file_info)
        except Exception as e:
            raise ValueError(f"Search failed: {e}")
        
        return files[:100]  # Limit results


class CommandExecutor:
    def __init__(self, workspace_root: str = None):
        self.workspace_root = Path(workspace_root or settings.workspace_root)
    
    def _is_safe_command(self, command: str) -> tuple[bool, Optional[str]]:
        """Check if command is safe to execute (Python-only mode)."""
        return guardrails.validate_command(command)
    
    async def execute_command(self, command: str, cwd: str = None, 
                            timeout: int = 30) -> Dict[str, Any]:
        """Execute a shell command safely (Python-only mode)."""
        is_safe, error_msg = self._is_safe_command(command)
        if not is_safe:
            raise ValueError(error_msg)
        
        work_dir = Path(cwd) if cwd else self.workspace_root
        
        if not str(work_dir.resolve()).startswith(str(self.workspace_root.resolve())):
            raise ValueError(f"Working directory not allowed: {work_dir}")
        
        try:
            # Set up Python-friendly environment
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'  # Ensure Python output is not buffered
            
            process = await asyncio.create_subprocess_shell(
                command,
                cwd=work_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )
            
            return {
                "stdout": stdout.decode('utf-8', errors='replace'),
                "stderr": stderr.decode('utf-8', errors='replace'),
                "exit_code": process.returncode,
                "command": command,
                "cwd": str(work_dir),
                "python_mode": True
            }
            
        except asyncio.TimeoutError:
            if process:
                process.kill()
                await process.wait()
            raise ValueError(f"Command timed out after {timeout}s")
        except Exception as e:
            raise ValueError(f"Command execution failed: {e}")


# Global instances
file_manager = FileSystemManager()
command_executor = CommandExecutor()


def get_file_manager() -> FileSystemManager:
    """Get the global file manager instance."""
    return file_manager


def get_command_executor() -> CommandExecutor:
    """Get the global command executor instance."""
    return command_executor