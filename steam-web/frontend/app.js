// STEAM Web Interface JavaScript Application

class SteamApp {
    constructor() {
        this.websocket = null;
        this.sessionId = null;
        this.editor = null;
        this.currentFile = null;
        this.files = {};
        this.isConnected = false;
        
        this.initializeElements();
        this.initializeEventListeners();
        this.initializeEditor();
        this.connect();
    }
    
    initializeElements() {
        // Get DOM elements
        this.elements = {
            connectionStatus: document.getElementById('connectionStatus'),
            sessionId: document.getElementById('sessionId'),
            messageCount: document.getElementById('messageCount'),
            chatMessages: document.getElementById('chatMessages'),
            chatInput: document.getElementById('chatInput'),
            sendButton: document.getElementById('sendButton'),
            typingIndicator: document.getElementById('typingIndicator'),
            fileTree: document.getElementById('fileTree'),
            editorTabs: document.getElementById('editorTabs'),
            editor: document.getElementById('editor'),
            approvalModal: document.getElementById('approvalModal'),
            commandPreview: document.getElementById('commandPreview'),
            loadingOverlay: document.getElementById('loadingOverlay'),
            aiProvider: document.getElementById('aiProvider'),
            clearChat: document.getElementById('clearChat'),
            saveFile: document.getElementById('saveFile'),
            newFile: document.getElementById('newFile')
        };
    }
    
    initializeEventListeners() {
        // Chat input
        this.elements.chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        this.elements.chatInput.addEventListener('input', () => {
            this.adjustTextareaHeight();
        });
        
        this.elements.sendButton.addEventListener('click', () => {
            this.sendMessage();
        });
        
        // Clear chat
        this.elements.clearChat.addEventListener('click', () => {
            this.clearChat();
        });
        
        // File operations
        this.elements.saveFile.addEventListener('click', () => {
            this.saveCurrentFile();
        });
        
        this.elements.newFile.addEventListener('click', () => {
            this.createNewFile();
        });
        
        // Modal buttons
        document.getElementById('approveCommand').addEventListener('click', () => {
            this.handleCommandApproval('approve');
        });
        
        document.getElementById('rejectCommand').addEventListener('click', () => {
            this.handleCommandApproval('reject');
        });
        
        document.getElementById('modifyCommand').addEventListener('click', () => {
            this.handleCommandApproval('modify');
        });
        
        // AI Provider change
        this.elements.aiProvider.addEventListener('change', () => {
            this.updateAIProvider();
        });
    }
    
    async initializeEditor() {
        // Load Monaco Editor
        require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs' }});
        
        require(['vs/editor/editor.main'], () => {
            this.editor = monaco.editor.create(this.elements.editor, {
                value: this.getWelcomeContent(),
                language: 'markdown',
                theme: 'vs-dark',
                fontSize: 14,
                automaticLayout: true,
                wordWrap: 'on',
                minimap: { enabled: false },
                scrollBeyondLastLine: false
            });
            
            // Editor change listener
            this.editor.onDidChangeModelContent(() => {
                if (this.currentFile && this.currentFile !== 'welcome') {
                    this.markFileAsModified(this.currentFile);
                }
            });
        });
    }
    
    getWelcomeContent() {
        return `# Welcome to STEAM 🚂

STEAM is your intelligent coding assistant, inspired by OpenAI Codex.

## Features

- **Real-time Chat**: Communicate with AI assistant through WebSocket
- **Code Editor**: Monaco editor with syntax highlighting
- **File Operations**: Browse, create, edit, and save files
- **Command Execution**: Execute terminal commands with approval system
- **Multi-AI Support**: OpenAI GPT, Anthropic Claude, and more

## Getting Started

1. **Connect**: Check connection status in the header
2. **Chat**: Use the chat panel to ask questions or request help
3. **Code**: Open files in the editor or create new ones
4. **Execute**: Ask STEAM to run commands (requires approval)

## Commands

Try asking STEAM to:
- "Create a Python hello world script"
- "List files in the current directory" 
- "Help me debug this code"
- "Explain this function"

Start chatting below to begin! 👇`;
    }
    
    connect() {
        this.showLoading('Connecting to STEAM...');
        
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        const wsUrl = `${protocol}//${host}/ws`;
        
        this.websocket = new WebSocket(wsUrl);
        
        this.websocket.onopen = () => {
            console.log('WebSocket connected');
            this.isConnected = true;
            this.updateConnectionStatus('online');
            this.hideLoading();
            
            // Join session
            this.sendWebSocketMessage('join_session', {});
            
            // Load file tree
            this.loadFileTree('/workspaces');
        };
        
        this.websocket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleWebSocketMessage(message);
        };
        
        this.websocket.onclose = () => {
            console.log('WebSocket disconnected');
            this.isConnected = false;
            this.updateConnectionStatus('offline');
            
            // Reconnect after delay
            setTimeout(() => {
                if (!this.isConnected) {
                    this.connect();
                }
            }, 5000);
        };
        
        this.websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.hideLoading();
            this.addErrorMessage('Connection error. Retrying...');
        };
    }
    
    sendWebSocketMessage(type, data) {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify({
                type: type,
                data: data,
                session_id: this.sessionId
            }));
        }
    }
    
    handleWebSocketMessage(message) {
        const { type, data } = message;
        
        switch (type) {
            case 'session_joined':
                this.sessionId = data.session_id;
                this.elements.sessionId.textContent = this.sessionId.substring(0, 8) + '...';
                break;
                
            case 'user_message':
                this.addMessage(data.message, 'user');
                break;
                
            case 'ai_response':
                this.addMessage(data.message, 'assistant');
                this.updateMessageCount();
                break;
                
            case 'ai_typing':
                this.showTypingIndicator(data.typing);
                break;
                
            case 'error':
                this.addErrorMessage(data.message);
                break;
                
            case 'file_list':
                this.updateFileTree(data.files, data.path);
                break;
                
            case 'file_content':
                this.openFileInEditor(data.path, data.content);
                break;
                
            case 'command_approval_required':
                this.showCommandApproval(data);
                break;
                
            default:
                console.log('Unknown message type:', type, data);
        }
    }
    
    sendMessage() {
        const message = this.elements.chatInput.value.trim();
        if (!message || !this.isConnected) return;
        
        // Clear input
        this.elements.chatInput.value = '';
        this.adjustTextareaHeight();
        
        // Send message
        this.sendWebSocketMessage('chat', { message: message });
    }
    
    addMessage(content, role) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const now = new Date().toLocaleTimeString();
        const roleIcon = role === 'user' ? '👤' : '🚂';
        const roleText = role === 'user' ? 'You' : 'STEAM';
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-header">
                    <span class="message-role ${role}">${roleIcon} ${roleText}</span>
                    <span class="message-time">${now}</span>
                </div>
                <div class="message-text">${this.formatMessage(content)}</div>
            </div>
        `;
        
        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addErrorMessage(content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message error';
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-header">
                    <span class="message-role">❌ Error</span>
                    <span class="message-time">${new Date().toLocaleTimeString()}</span>
                </div>
                <div class="message-text">${content}</div>
            </div>
        `;
        
        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    formatMessage(content) {
        // Basic markdown-like formatting
        content = content.replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>');
        content = content.replace(/`([^`]+)`/g, '<code>$1</code>');
        content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        content = content.replace(/\*(.*?)\*/g, '<em>$1</em>');
        content = content.replace(/\n/g, '<br>');
        
        return content;
    }
    
    showTypingIndicator(show) {
        this.elements.typingIndicator.style.display = show ? 'flex' : 'none';
        if (show) {
            this.scrollToBottom();
        }
    }
    
    scrollToBottom() {
        this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
    }
    
    adjustTextareaHeight() {
        const textarea = this.elements.chatInput;
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
    
    updateConnectionStatus(status) {
        this.elements.connectionStatus.className = `status-indicator ${status}`;
        this.elements.connectionStatus.textContent = status === 'online' ? 'Online' : 'Offline';
    }
    
    updateMessageCount() {
        const messages = this.elements.chatMessages.querySelectorAll('.message:not(.welcome-message)');
        this.elements.messageCount.textContent = messages.length;
    }
    
    clearChat() {
        // Keep welcome message, remove others
        const messages = this.elements.chatMessages.querySelectorAll('.message:not(.welcome-message)');
        messages.forEach(msg => msg.remove());
        this.updateMessageCount();
    }
    
    showLoading(text) {
        this.elements.loadingOverlay.querySelector('.loading-text').textContent = text;
        this.elements.loadingOverlay.style.display = 'flex';
    }
    
    hideLoading() {
        this.elements.loadingOverlay.style.display = 'none';
    }
    
    loadFileTree(path) {
        this.sendWebSocketMessage('file_operation', {
            operation: 'list',
            path: path
        });
    }
    
    updateFileTree(files, path) {
        this.elements.fileTree.innerHTML = '';
        
        // Add parent directory link if not root
        if (path !== '/workspaces') {
            const parentItem = this.createFileItem('..', true, () => {
                const parentPath = path.split('/').slice(0, -1).join('/') || '/workspaces';
                this.loadFileTree(parentPath);
            });
            this.elements.fileTree.appendChild(parentItem);
        }
        
        // Sort files: directories first, then files
        files.sort((a, b) => {
            if (a.is_directory !== b.is_directory) {
                return b.is_directory - a.is_directory;
            }
            return a.name.localeCompare(b.name);
        });
        
        files.forEach(file => {
            const item = this.createFileItem(file.name, file.is_directory, () => {
                if (file.is_directory) {
                    this.loadFileTree(file.path);
                } else {
                    this.openFile(file.path);
                }
            });
            this.elements.fileTree.appendChild(item);
        });
    }
    
    createFileItem(name, isDirectory, onClick) {
        const item = document.createElement('div');
        item.className = 'file-item';
        item.onclick = onClick;
        
        const icon = isDirectory ? '📁' : this.getFileIcon(name);
        
        item.innerHTML = `
            <span class="file-icon">${icon}</span>
            <span class="file-name">${name}</span>
        `;
        
        return item;
    }
    
    getFileIcon(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const icons = {
            'py': '🐍',
            'js': '💛',
            'ts': '💙',
            'html': '🌐',
            'css': '🎨',
            'md': '📝',
            'json': '📋',
            'txt': '📄',
            'rs': '🦀',
            'go': '🔵',
            'java': '☕',
        };
        return icons[ext] || '📄';
    }
    
    openFile(path) {
        this.sendWebSocketMessage('file_operation', {
            operation: 'read',
            path: path
        });
    }
    
    openFileInEditor(path, content) {
        if (!this.editor) return;
        
        this.currentFile = path;
        this.files[path] = content;
        
        // Detect language
        const language = this.detectLanguage(path);
        
        // Update editor
        const model = monaco.editor.createModel(content, language);
        this.editor.setModel(model);
        
        // Update tab
        this.updateEditorTab(path);
    }
    
    detectLanguage(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const languages = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'typescript',
            'html': 'html',
            'css': 'css',
            'md': 'markdown',
            'json': 'json',
            'rs': 'rust',
            'go': 'go',
            'java': 'java',
            'cpp': 'cpp',
            'c': 'c',
            'sh': 'shell',
            'yml': 'yaml',
            'yaml': 'yaml',
            'xml': 'xml',
            'sql': 'sql'
        };
        return languages[ext] || 'plaintext';
    }
    
    updateEditorTab(filePath) {
        const filename = filePath.split('/').pop();
        
        // Remove existing tabs except welcome
        const tabs = this.elements.editorTabs.querySelectorAll('.tab:not([data-file="welcome"])');
        tabs.forEach(tab => tab.remove());
        
        // Remove active class from welcome tab
        const welcomeTab = this.elements.editorTabs.querySelector('.tab[data-file="welcome"]');
        if (welcomeTab) {
            welcomeTab.classList.remove('active');
        }
        
        // Create new tab
        const tab = document.createElement('div');
        tab.className = 'tab active';
        tab.dataset.file = filePath;
        tab.innerHTML = `
            <span class="tab-name">${filename}</span>
            <span class="tab-close" onclick="event.stopPropagation(); app.closeTab('${filePath}')">×</span>
        `;
        
        tab.onclick = () => this.switchToFile(filePath);
        this.elements.editorTabs.appendChild(tab);
    }
    
    closeTab(filePath) {
        const tab = this.elements.editorTabs.querySelector(`[data-file="${filePath}"]`);
        if (tab) {
            tab.remove();
        }
        
        // Switch to welcome tab
        this.switchToWelcome();
    }
    
    switchToWelcome() {
        const welcomeTab = this.elements.editorTabs.querySelector('.tab[data-file="welcome"]');
        if (welcomeTab) {
            this.elements.editorTabs.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            welcomeTab.classList.add('active');
            
            if (this.editor) {
                const model = monaco.editor.createModel(this.getWelcomeContent(), 'markdown');
                this.editor.setModel(model);
            }
            
            this.currentFile = 'welcome';
        }
    }
    
    switchToFile(filePath) {
        if (this.files[filePath] && this.editor) {
            this.openFileInEditor(filePath, this.files[filePath]);
        }
    }
    
    saveCurrentFile() {
        if (!this.currentFile || this.currentFile === 'welcome' || !this.editor) {
            return;
        }
        
        const content = this.editor.getValue();
        
        // Send save request via WebSocket (could be implemented)
        // For now, just update local storage
        this.files[this.currentFile] = content;
        
        // Remove modified indicator
        this.markFileAsSaved(this.currentFile);
        
        this.addMessage(`File saved: ${this.currentFile}`, 'assistant');
    }
    
    createNewFile() {
        const filename = prompt('Enter filename:');
        if (!filename) return;
        
        const path = `/workspaces/${filename}`;
        this.openFileInEditor(path, '');
    }
    
    markFileAsModified(filePath) {
        const tab = this.elements.editorTabs.querySelector(`[data-file="${filePath}"] .tab-name`);
        if (tab && !tab.textContent.endsWith('*')) {
            tab.textContent += '*';
        }
    }
    
    markFileAsSaved(filePath) {
        const tab = this.elements.editorTabs.querySelector(`[data-file="${filePath}"] .tab-name`);
        if (tab) {
            tab.textContent = tab.textContent.replace('*', '');
        }
    }
    
    showCommandApproval(data) {
        this.elements.commandPreview.textContent = data.command;
        this.elements.approvalModal.style.display = 'flex';
        this.currentCommandId = data.command_id;
    }
    
    handleCommandApproval(decision) {
        this.elements.approvalModal.style.display = 'none';
        
        let modifiedCommand = null;
        if (decision === 'modify') {
            modifiedCommand = prompt('Modify command:', this.elements.commandPreview.textContent);
            if (!modifiedCommand) return;
        }
        
        // Send approval via HTTP API (would need to implement)
        console.log('Command approval:', decision, this.currentCommandId, modifiedCommand);
    }
    
    updateAIProvider() {
        const provider = this.elements.aiProvider.value;
        console.log('Switching to AI provider:', provider);
        // Could send provider preference to backend
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new SteamApp();
});