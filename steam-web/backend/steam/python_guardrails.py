"""
Python-only validation utilities for STEAM.
Ensures all operations are restricted to Python development.
"""

import re
from typing import List, Set, Optional
from pathlib import Path
from steam.config import get_settings

settings = get_settings()


class PythonGuardrails:
    """Enforces Python-only restrictions across STEAM."""
    
    # Python file extensions
    PYTHON_EXTENSIONS = {'.py', '.pyx', '.pyi'}
    
    # Python-related file patterns
    PYTHON_CONFIG_FILES = {
        'requirements.txt', 'requirements-dev.txt', 'requirements-test.txt',
        'setup.py', 'setup.cfg', 'pyproject.toml', 'tox.ini', 'pytest.ini',
        'conftest.py', '__init__.py', 'manage.py', 'wsgi.py', 'asgi.py'
    }
    
    # Python-related directories
    PYTHON_DIRECTORIES = {
        '__pycache__', '.pytest_cache', '.tox', 'venv', 'env',
        '.venv', 'site-packages', 'dist', 'build', 'egg-info'
    }
    
    # Allowed Python-related commands
    ALLOWED_COMMANDS = {
        # Python execution
        'python', 'python3', 'py',
        # Package management
        'pip', 'pip3', 'pipenv', 'poetry', 'conda',
        # Testing
        'pytest', 'python -m pytest', 'unittest', 'python -m unittest',
        # Code quality
        'flake8', 'black', 'mypy', 'pylint', 'autopep8', 'isort',
        # Virtual environments
        'virtualenv', 'venv', 'conda create', 'conda activate',
        # Django management
        'python manage.py', 'django-admin',
        # Flask
        'flask',
        # FastAPI
        'uvicorn', 'gunicorn',
        # General system commands (safe)
        'ls', 'pwd', 'cd', 'mkdir', 'rmdir', 'cp', 'mv', 'cat', 'echo', 'grep',
        'find', 'which', 'whereis', 'tree', 'head', 'tail', 'wc', 'sort'
    }
    
    # Dangerous commands to block
    BLOCKED_COMMANDS = {
        'rm -rf', 'sudo', 'chmod 777', 'chown', 'format', 'del', 'shutdown',
        'reboot', 'halt', 'init', 'kill -9', 'killall', 'pkill', 'dd',
        'mkfs', 'fdisk', 'parted', 'mount', 'umount', 'crontab -r'
    }
    
    @classmethod
    def is_python_file(cls, file_path: str) -> bool:
        """Check if a file is a Python file."""
        path = Path(file_path)
        
        # Check extension
        if path.suffix.lower() in cls.PYTHON_EXTENSIONS:
            return True
        
        # Check specific filenames
        if path.name.lower() in cls.PYTHON_CONFIG_FILES:
            return True
        
        # Check patterns like requirements-*.txt
        if re.match(r'requirements.*\.txt$', path.name.lower()):
            return True
        
        return False
    
    @classmethod
    def is_python_related_file(cls, file_path: str) -> bool:
        """Check if a file is related to Python development."""
        path = Path(file_path)
        
        # Python files
        if cls.is_python_file(file_path):
            return True
        
        # Documentation files in Python projects
        if path.suffix.lower() in {'.md', '.txt', '.rst'}:
            return True
        
        # Configuration files
        if path.suffix.lower() in {'.json', '.yaml', '.yml', '.toml', '.cfg', '.ini'}:
            return True
        
        return False
    
    @classmethod
    def is_safe_directory(cls, dir_path: str) -> bool:
        """Check if directory operations are safe."""
        path = Path(dir_path)
        
        # Allow Python-specific directories
        if path.name in cls.PYTHON_DIRECTORIES:
            return True
        
        # Block system directories
        system_dirs = {'/bin', '/usr', '/etc', '/sys', '/proc', '/dev', '/boot'}
        if str(path) in system_dirs or str(path).startswith(tuple(system_dirs)):
            return False
        
        return True
    
    @classmethod
    def validate_command(cls, command: str) -> tuple[bool, Optional[str]]:
        """Validate if a command is allowed for Python development."""
        command_lower = command.lower().strip()
        
        # Check for blocked commands
        for blocked in cls.BLOCKED_COMMANDS:
            if blocked in command_lower:
                return False, f"Command blocked for security: contains '{blocked}'"
        
        # Extract the main command (first word)
        main_cmd = command_lower.split()[0] if command_lower.split() else ""
        
        # Check if it's an allowed command
        allowed = False
        for allowed_cmd in cls.ALLOWED_COMMANDS:
            if command_lower.startswith(allowed_cmd.lower()):
                allowed = True
                break
        
        if not allowed:
            # Check if it's a Python-related command pattern
            python_patterns = [
                r'^python\d*\s+',       # python, python3
                r'^pip\d*\s+',          # pip, pip3
                r'^python\d*\s+-m\s+',  # python -m module
                r'\.py$',               # Running .py files
                r'^cd\s+\w+',           # cd to directories
                r'^ls\s*',              # ls commands
                r'^cat\s+.*\.py',       # cat Python files
            ]
            
            for pattern in python_patterns:
                if re.match(pattern, command_lower):
                    allowed = True
                    break
        
        if not allowed:
            return False, f"Command not allowed in Python-only mode: '{main_cmd}'"
        
        return True, None
    
    @classmethod
    def filter_file_list(cls, files: List[dict]) -> List[dict]:
        """Filter file list to show only Python-related files."""
        filtered = []
        
        for file_info in files:
            path = file_info.get('path', '')
            is_dir = file_info.get('is_directory', False)
            
            if is_dir:
                # Allow directories but check if they're safe
                if cls.is_safe_directory(path):
                    filtered.append(file_info)
            else:
                # Only allow Python-related files
                if cls.is_python_related_file(path):
                    filtered.append(file_info)
        
        return filtered
    
    @classmethod
    def validate_file_operation(cls, operation: str, file_path: str) -> tuple[bool, Optional[str]]:
        """Validate file operations for Python-only mode."""
        
        # Always allow reading directories
        if operation == "list":
            if not cls.is_safe_directory(file_path):
                return False, f"Directory access not allowed: {file_path}"
            return True, None
        
        # For file operations, check if it's Python-related
        if not cls.is_python_related_file(file_path):
            return False, f"File type not allowed in Python-only mode: {file_path}"
        
        # Additional checks for write/delete operations
        if operation in ["write", "create", "delete"]:
            path = Path(file_path)
            
            # Prevent modification of critical system files
            if str(path).startswith(('/usr/', '/bin/', '/etc/', '/sys/', '/proc/')):
                return False, f"System file modification not allowed: {file_path}"
            
            # Prevent deletion of important Python files
            if operation == "delete" and path.name in ['__init__.py', 'setup.py', 'requirements.txt']:
                return False, f"Critical Python file deletion blocked: {file_path}"
        
        return True, None
    
    @classmethod
    def get_python_help_text(cls) -> str:
        """Get help text for Python-only mode."""
        return """
🐍 STEAM Python-Only Mode

This STEAM instance is configured for Python development only. Here's what you can do:

📁 File Operations:
• Create, edit, and manage .py files
• Work with Python configuration files (requirements.txt, setup.py, pyproject.toml)
• Read documentation files (.md, .txt, .rst)

⚡ Commands Available:
• Python execution: python, python3, py
• Package management: pip, poetry, conda
• Testing: pytest, unittest
• Code quality: black, flake8, mypy, pylint
• Virtual environments: venv, virtualenv, conda
• Web frameworks: django-admin, flask, uvicorn

🚫 Restrictions:
• Non-Python files are hidden/blocked
• System commands are restricted for security
• Only Python-related operations are allowed

Need help with Python development? Just ask!
        """.strip()


# Global instance
python_guardrails = PythonGuardrails()


def get_python_guardrails() -> PythonGuardrails:
    """Get the global Python guardrails instance."""
    return python_guardrails