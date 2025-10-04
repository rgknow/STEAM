#!/usr/bin/env python3
"""
STEAM Web Interface Launcher
"""

import sys
import os
import uvicorn
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def main():
    """Launch the STEAM web interface."""
    print("🚂 Starting STEAM Web Interface...")
    print("=" * 50)
    
    # Check if requirements are installed
    try:
        import fastapi
        import websockets
        import openai
        import anthropic
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install requirements:")
        print("pip install -r requirements.txt")
        return 1
    
    print("✅ Dependencies loaded")
    print("🌐 Starting web server...")
    print("📁 Workspace root: /workspaces")
    print("🔗 Access at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    print("=" * 50)
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        app_dir=str(backend_dir)
    )

if __name__ == "__main__":
    sys.exit(main())