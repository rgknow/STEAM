import os
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # AI Provider Configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # Session Configuration
    session_timeout: int = 3600  # 1 hour
    max_sessions: int = 100
    
    # File System - Python Only Mode
    workspace_root: str = "/workspaces"
    allowed_extensions: List[str] = [
        ".py",           # Python source files
        ".pyx",          # Cython files
        ".pyi",          # Python stub files
        ".txt",          # Text files for documentation
        ".md",           # Markdown documentation
        ".json",         # Configuration files
        ".yaml", ".yml", # Configuration files
        ".toml",         # Configuration files (pyproject.toml, etc.)
        ".cfg",          # Setup.cfg and other config files
        ".ini",          # Configuration files
        ".requirements", # Requirements files
        ".txt"           # Requirements.txt, etc.
    ]
    
    # Python-specific settings
    python_only_mode: bool = True
    allowed_python_patterns: List[str] = [
        "*.py", "requirements*.txt", "setup.py", "setup.cfg", 
        "pyproject.toml", "tox.ini", "pytest.ini", "*.pyi"
    ]
    
    # Security
    secret_key: str = "steam-secret-key-change-in-production"
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "steam.log"
    
    # AI Model Configuration
    default_model: str = "gpt-4"
    max_tokens: int = 4000
    temperature: float = 0.1
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings