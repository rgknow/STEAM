# STEAM Web Interface

A Python-based web interface for STEAM coding assistant, inspired by OpenAI Codex architecture.

## Features

- Real-time chat interface with AI coding assistant
- Integrated code editor with syntax highlighting
- File explorer and project management
- WebSocket-based real-time communication
- Session management and conversation history
- Command execution and approval system
- Multi-model support (OpenAI, Anthropic, local models)

## Architecture

- **Backend**: FastAPI with WebSocket support
- **Frontend**: Modern web interface with Monaco Editor
- **Communication**: WebSocket protocol for real-time interaction
- **AI Integration**: Support for multiple AI providers

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. Run the server:
   ```bash
   python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. Open your browser to `http://localhost:8000`

## Configuration

See `backend/steam/config.py` for configuration options.

## License

MIT License