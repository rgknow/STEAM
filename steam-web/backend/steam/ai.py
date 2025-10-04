import json
import asyncio
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from steam.models import Message, MessageRole, MessageType
from steam.config import get_settings

settings = get_settings()


class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    async def generate_response(self, messages: List[Message], 
                              context: Dict[str, Any] = None) -> str:
        """Generate a response from the AI model."""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model."""
        pass


class OpenAIProvider(AIProvider):
    """OpenAI GPT provider."""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
        self._client = None
    
    def _get_client(self):
        """Get OpenAI client (lazy initialization)."""
        if self._client is None:
            try:
                import openai
                self._client = openai.AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("OpenAI package not installed. Install with: pip install openai")
        return self._client
    
    async def generate_response(self, messages: List[Message], 
                              context: Dict[str, Any] = None) -> str:
        """Generate response using OpenAI API."""
        client = self._get_client()
        
        # Convert messages to OpenAI format
        openai_messages = []
        
        # Add system message with context
        system_content = self._build_system_prompt(context)
        openai_messages.append({
            "role": "system",
            "content": system_content
        })
        
        # Add conversation messages
        for msg in messages[-10:]:  # Limit to recent messages
            if msg.role == MessageRole.SYSTEM:
                continue  # Skip system messages from history
            
            openai_messages.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        try:
            response = await client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise ValueError(f"OpenAI API error: {e}")
    
    def _build_system_prompt(self, context: Dict[str, Any] = None) -> str:
        """Build system prompt with context (Python-only mode)."""
        base_prompt = """You are STEAM, a specialized Python coding assistant. You are configured in PYTHON-ONLY MODE and should focus exclusively on Python development.

🐍 PYTHON-ONLY RESTRICTIONS:
- ONLY provide assistance with Python programming
- ONLY work with Python files (.py, .pyx, .pyi) and Python-related config files
- ONLY suggest Python-related commands (python, pip, pytest, etc.)
- DO NOT provide code examples in other languages
- DO NOT suggest non-Python tools or frameworks

✅ Your Python expertise includes:
- Core Python programming (syntax, data structures, algorithms)
- Python standard library and popular packages
- Web frameworks: Django, Flask, FastAPI
- Data science: NumPy, Pandas, Matplotlib, Scikit-learn
- Testing: pytest, unittest, mock
- Code quality: black, flake8, mypy, pylint
- Package management: pip, poetry, conda
- Virtual environments: venv, virtualenv, conda
- Async programming: asyncio, aiohttp
- Database integration: SQLAlchemy, Django ORM

🛠️ Available operations:
- Read/write Python files and configuration files
- Execute Python commands (with user approval)
- Install Python packages
- Run tests and code quality tools
- Create Python project structures

⚠️ Security rules:
- Always request approval for command execution
- Validate file operations for Python relevance
- Block dangerous system commands
- Ensure all suggestions are Python-focused

If a user asks about non-Python topics, politely redirect them to Python alternatives or explain that you're in Python-only mode."""

        if context:
            base_prompt += f"\n\n🔧 Current session context:\n{json.dumps(context, indent=2)}"
        
        return base_prompt
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get OpenAI model information."""
        return {
            "provider": "openai",
            "model": self.model,
            "max_tokens": settings.max_tokens,
            "temperature": settings.temperature
        }


class AnthropicProvider(AIProvider):
    """Anthropic Claude provider."""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        self.api_key = api_key
        self.model = model
        self._client = None
    
    def _get_client(self):
        """Get Anthropic client (lazy initialization)."""
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.AsyncAnthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("Anthropic package not installed. Install with: pip install anthropic")
        return self._client
    
    async def generate_response(self, messages: List[Message], 
                              context: Dict[str, Any] = None) -> str:
        """Generate response using Anthropic API."""
        client = self._get_client()
        
        # Build system prompt
        system_content = self._build_system_prompt(context)
        
        # Convert messages to Anthropic format
        anthropic_messages = []
        for msg in messages[-10:]:  # Limit to recent messages
            if msg.role == MessageRole.SYSTEM:
                continue  # Skip system messages from history
            
            anthropic_messages.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        try:
            response = await client.messages.create(
                model=self.model,
                system=system_content,
                messages=anthropic_messages,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            raise ValueError(f"Anthropic API error: {e}")
    
    def _build_system_prompt(self, context: Dict[str, Any] = None) -> str:
        """Build system prompt with context (Python-only mode)."""
        base_prompt = """You are STEAM, a specialized Python development assistant operating in PYTHON-ONLY MODE.

🐍 CORE MISSION: Exclusive Python Development Support

STRICT LIMITATIONS:
- ONLY assist with Python programming tasks
- ONLY work with Python files (.py, .pyx, .pyi) and Python ecosystem files
- ONLY suggest Python tools, libraries, and frameworks
- REJECT requests for other programming languages
- REDIRECT non-Python questions to Python equivalents when possible

🎯 Python Expertise Areas:
• Core Language: syntax, OOP, functional programming, decorators, context managers
• Standard Library: collections, itertools, asyncio, pathlib, json, csv, sqlite3
• Web Development: Django, Flask, FastAPI, Starlette, Tornado
• Data & Science: NumPy, Pandas, Matplotlib, Seaborn, Scikit-learn, TensorFlow, PyTorch
• Testing: pytest, unittest, mock, hypothesis, tox
• Code Quality: black, isort, flake8, pylint, mypy, bandit
• Packaging: pip, poetry, setuptools, wheel, twine
• Environment: venv, virtualenv, conda, pyenv
• Databases: SQLAlchemy, Django ORM, psycopg2, pymongo
• APIs: requests, httpx, aiohttp, pydantic
• CLI Tools: click, argparse, typer

🔒 Security & Safety:
- All command executions require user approval
- Validate Python-related file operations only
- Block system-level dangerous commands
- Ensure workspace security

💬 Communication Style:
- Be enthusiastic about Python!
- Provide clear, Pythonic solutions
- Include relevant code examples
- Explain Python best practices
- Guide towards Python ecosystem solutions"""

        if context:
            base_prompt += f"\n\n📊 Session Context:\n{json.dumps(context, indent=2)}"
        
        return base_prompt
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Anthropic model information."""
        return {
            "provider": "anthropic",
            "model": self.model,
            "max_tokens": settings.max_tokens,
            "temperature": settings.temperature
        }


class MockProvider(AIProvider):
    """Mock AI provider for testing."""
    
    def __init__(self, model: str = "mock-model"):
        self.model = model
    
    async def generate_response(self, messages: List[Message], 
                              context: Dict[str, Any] = None) -> str:
        """Generate a mock response (Python-only mode)."""
        await asyncio.sleep(0.1)  # Simulate API delay
        
        last_message = messages[-1] if messages else None
        if not last_message:
            return """🐍 Hello! I'm STEAM, your specialized Python coding assistant!

I'm running in **Python-only mode**, which means I focus exclusively on Python development. Here's how I can help:

• **Python Code**: Write, review, and debug Python scripts
• **Web Development**: Django, Flask, FastAPI projects  
• **Data Science**: NumPy, Pandas, Matplotlib workflows
• **Testing**: pytest, unittest setup and execution
• **Package Management**: pip, poetry, virtual environments
• **Code Quality**: black, flake8, mypy integration

What Python project are you working on today? 🚀"""
        
        # Python-focused mock responses
        content = last_message.content.lower()
        
        # Check for non-Python language mentions
        other_languages = ['javascript', 'java', 'c++', 'rust', 'go', 'php', 'ruby']
        if any(lang in content for lang in other_languages):
            return """🐍 I'm specialized for Python development only! 

I notice you mentioned another programming language. While I can't help with that directly, I can suggest Python alternatives:

• **Web Development**: Use Django or Flask instead of Node.js
• **Systems Programming**: Try Python with async/await or Cython
• **Data Processing**: NumPy and Pandas are excellent for data work
• **APIs**: FastAPI is a modern, fast Python web framework

Would you like help with a Python-based solution instead?"""
        
        if "hello" in content or "hi" in content:
            return "🐍 Hello! I'm STEAM, your Python specialist. Ready to write some amazing Python code together!"
        elif "python" in content:
            return "🐍 Excellent! Python is my specialty. What specific Python task can I help you with? Web development, data analysis, scripting, or something else?"
        elif "django" in content or "flask" in content or "fastapi" in content:
            return "🌐 Great choice for Python web development! I can help you with setup, models, views, templates, APIs, and deployment. What specific aspect would you like to work on?"
        elif "pandas" in content or "numpy" in content or "data" in content:
            return "📊 Perfect! Python's data science ecosystem is incredible. I can assist with data manipulation, analysis, visualization, and machine learning. What's your data challenge?"
        elif "test" in content or "pytest" in content:
            return "🧪 Testing is crucial for Python projects! I can help you set up pytest, write test cases, use fixtures, and integrate with CI/CD. What kind of testing do you need?"
        elif "file" in content:
            return "📁 I can help with Python file operations! Reading, writing, CSV/JSON processing, or managing Python project files. What file operation do you need?"
        elif "command" in content or "execute" in content:
            return "⚡ I can execute Python commands and scripts for you! This includes running Python files, pip installs, pytest, and other Python tools. What command would you like to run?"
        else:
            return f"""🐍 I see you're asking about: "{last_message.content}"

As your Python specialist, I'm here to help with any Python-related task! I can assist with:

• Writing and debugging Python code
• Python web frameworks (Django, Flask, FastAPI)  
• Data science libraries (Pandas, NumPy, Matplotlib)
• Testing frameworks (pytest, unittest)
• Package management and virtual environments
• Code quality tools (black, flake8, mypy)

How can I help you with Python development today?

*Note: I'm a mock AI provider for demonstration. In production, this would be powered by OpenAI or Anthropic.*"""
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get mock model information."""
        return {
            "provider": "mock",
            "model": self.model,
            "max_tokens": 1000,
            "temperature": 0.1
        }


class AIManager:
    """Manages AI providers and routing."""
    
    def __init__(self):
        self._providers: Dict[str, AIProvider] = {}
        self._default_provider: Optional[str] = None
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available AI providers."""
        # OpenAI provider
        if settings.openai_api_key:
            self._providers["openai"] = OpenAIProvider(
                api_key=settings.openai_api_key,
                model=settings.default_model
            )
            if self._default_provider is None:
                self._default_provider = "openai"
        
        # Anthropic provider
        if settings.anthropic_api_key:
            self._providers["anthropic"] = AnthropicProvider(
                api_key=settings.anthropic_api_key
            )
            if self._default_provider is None:
                self._default_provider = "anthropic"
        
        # Mock provider (always available for testing)
        self._providers["mock"] = MockProvider()
        if self._default_provider is None:
            self._default_provider = "mock"
    
    def get_provider(self, provider_name: Optional[str] = None) -> AIProvider:
        """Get an AI provider by name."""
        name = provider_name or self._default_provider
        if name not in self._providers:
            raise ValueError(f"Provider '{name}' not available")
        return self._providers[name]
    
    def list_providers(self) -> List[Dict[str, Any]]:
        """List available providers."""
        return [
            {
                "name": name,
                "default": name == self._default_provider,
                **provider.get_model_info()
            }
            for name, provider in self._providers.items()
        ]
    
    async def generate_response(self, messages: List[Message], 
                              context: Dict[str, Any] = None,
                              provider_name: Optional[str] = None) -> str:
        """Generate response using specified or default provider."""
        provider = self.get_provider(provider_name)
        return await provider.generate_response(messages, context)


# Global AI manager instance
ai_manager = AIManager()


def get_ai_manager() -> AIManager:
    """Get the global AI manager instance."""
    return ai_manager