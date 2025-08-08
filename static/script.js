// Modern Chat Interface JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeInterface();
    checkAPIStatus();
    setupEventListeners();
    autoResizeTextarea();
});

function initializeInterface() {
    // Setup sidebar toggle functionality
    setupSidebarToggle();
    
    // Setup AI options toggle
    const processWithAI = document.getElementById('process-with-ai');
    const aiOptions = document.getElementById('ai-options');
    
    processWithAI.addEventListener('change', function() {
        aiOptions.style.display = this.checked ? 'block' : 'none';
    });
    
    // Auto-focus on message input
    const messageInput = document.getElementById('chat-message');
    messageInput.focus();
}

function setupSidebarToggle() {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebarClose = document.getElementById('sidebar-close');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const mainContent = document.getElementById('main-content');
    
    function openSidebar() {
        sidebar.classList.add('open');
        sidebarOverlay.classList.add('active');
        if (window.innerWidth >= 1024) {
            mainContent.classList.add('sidebar-open');
        }
    }
    
    function closeSidebar() {
        sidebar.classList.remove('open');
        sidebarOverlay.classList.remove('active');
        mainContent.classList.remove('sidebar-open');
    }
    
    sidebarToggle.addEventListener('click', openSidebar);
    sidebarClose.addEventListener('click', closeSidebar);
    sidebarOverlay.addEventListener('click', closeSidebar);
    
    // Auto-open sidebar on desktop
    if (window.innerWidth >= 1024) {
        openSidebar();
    }
    
    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth >= 1024) {
            openSidebar();
        } else {
            closeSidebar();
        }
    });
}

function setupEventListeners() {
    // Chat form submission
    document.getElementById('chat-form').addEventListener('submit', handleChatSubmission);
    
    // File attachment button
    document.getElementById('attach-file-btn').addEventListener('click', function() {
        document.getElementById('file-input').click();
    });
    
    // File input change
    document.getElementById('file-input').addEventListener('change', handleFileSelection);
    
    // Enter key to submit (Shift+Enter for new line)
    document.getElementById('chat-message').addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            document.getElementById('chat-form').dispatchEvent(new Event('submit'));
        }
    });
}

function autoResizeTextarea() {
    const textarea = document.getElementById('chat-message');
    
    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });
}

async function checkAPIStatus() {
    const statusElement = document.getElementById('api-status');
    
    try {
        const response = await fetch('/health');
        const data = await response.json();
        
        if (response.ok && data.status === 'healthy') {
            statusElement.innerHTML = `
                <span class="status-indicator status-healthy"></span>
                <span class="text-success">API conectada</span>
            `;
        } else {
            throw new Error('API no disponible');
        }
    } catch (error) {
        statusElement.innerHTML = `
            <span class="status-indicator status-error"></span>
            <span class="text-danger">Error de conexión</span>
        `;
        console.error('API status check failed:', error);
    }
}

async function handleChatSubmission(event) {
    event.preventDefault();
    
    const messageInput = document.getElementById('chat-message');
    const submitButton = document.getElementById('chat-submit');
    const messagesContainer = document.getElementById('chat-messages');
    
    // Get form data
    const message = messageInput.value.trim();
    const model = document.getElementById('chat-model').value;
    const mode = document.getElementById('chat-mode').value;
    const context = document.getElementById('chat-context').value.trim();
    
    if (!message) {
        showAlert('Por favor escribe un mensaje', 'warning');
        return;
    }
    
    // Clear input and hide welcome message
    messageInput.value = '';
    messageInput.style.height = 'auto';
    hideWelcomeMessage();
    
    // Add user message to chat
    addUserMessage(message);
    
    // Show loading state
    submitButton.disabled = true;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    
    // Add loading message
    const loadingId = addLoadingMessage();
    
    try {
        const requestData = {
            message: message,
            model: model,
            mode: mode
        };
        
        if (context) {
            requestData.context = context;
        }
        
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        
        // Remove loading message
        removeLoadingMessage(loadingId);
        
        if (response.ok && data.success) {
            // Add AI response to chat
            addAssistantMessage(data.response, {
                model: data.model,
                mode: data.mode,
                perspectives: data.metadata?.perspectives_analyzed,
                tokens: data.usage?.total_tokens
            });
        } else {
            throw new Error(data.message || 'Error al obtener respuesta');
        }
    } catch (error) {
        // Remove loading message
        removeLoadingMessage(loadingId);
        console.error('Chat error:', error);
        showAlert(`Error: ${error.message}`, 'danger');
        addAssistantMessage('Lo siento, ha ocurrido un error al procesar tu mensaje. Por favor intenta de nuevo.', { error: true });
    } finally {
        // Reset button
        submitButton.disabled = false;
        submitButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
        messageInput.focus();
    }
}

async function handleFileSelection(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Validate file size
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
        showAlert('El archivo excede el límite de 10MB', 'danger');
        event.target.value = '';
        return;
    }
    
    // Validate file type
    const allowedTypes = ['text/plain', 'application/pdf'];
    if (!allowedTypes.includes(file.type)) {
        showAlert('Solo se admiten archivos PDF y TXT', 'danger');
        event.target.value = '';
        return;
    }
    
    // Process file upload
    await processFileUpload(file);
    event.target.value = '';
}

async function processFileUpload(file) {
    const processWithAI = document.getElementById('process-with-ai').checked;
    const model = document.getElementById('chat-model').value;
    const question = document.getElementById('upload-question').value.trim();
    
    hideWelcomeMessage();
    
    // Add file upload message
    addUserMessage(`📎 Archivo subido: ${file.name} (${formatFileSize(file.size)})`);
    
    // Show loading
    const loadingId = addLoadingMessage('Procesando archivo...');
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        if (processWithAI) {
            formData.append('process_with_ai', 'true');
            formData.append('model', model);
            if (question) {
                formData.append('question', question);
            }
        }
        
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        // Remove loading message
        removeLoadingMessage(loadingId);
        
        if (response.ok && data.success) {
            let responseText = `✅ Archivo procesado exitosamente:\n\n`;
            responseText += `📄 **${data.file_info.filename}**\n`;
            responseText += `📊 Tamaño: ${formatFileSize(data.file_info.size)}\n`;
            responseText += `📝 Palabras: ${data.file_info.word_count.toLocaleString()}\n\n`;
            
            if (data.content_preview) {
                responseText += `**Vista previa del contenido:**\n${data.content_preview}\n\n`;
            }
            
            if (data.ai_analysis) {
                responseText += `**Análisis de IA (${data.ai_analysis.model}):**\n`;
                responseText += `${data.ai_analysis.response}`;
            }
            
            addAssistantMessage(responseText, { 
                model: data.ai_analysis?.model,
                file: true
            });
        } else {
            throw new Error(data.message || 'Error al procesar archivo');
        }
    } catch (error) {
        // Remove loading message
        removeLoadingMessage(loadingId);
        console.error('Upload error:', error);
        showAlert(`Error: ${error.message}`, 'danger');
        addAssistantMessage('Error al procesar el archivo. Por favor intenta de nuevo.', { error: true });
    }
}

function hideWelcomeMessage() {
    const welcomeMessage = document.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.style.display = 'none';
    }
}

function addUserMessage(message) {
    const messagesContainer = document.getElementById('chat-messages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user';
    messageDiv.innerHTML = `
        <div class="message-content">
            ${escapeHtml(message).replace(/\n/g, '<br>')}
        </div>
        <div class="message-avatar">
            <i class="fas fa-user"></i>
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

function addAssistantMessage(message, metadata = {}) {
    const messagesContainer = document.getElementById('chat-messages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    
    let metaInfo = '';
    if (metadata.model && !metadata.error) {
        metaInfo = `Modelo: ${metadata.model}`;
        if (metadata.mode) metaInfo += ` | Modo: ${metadata.mode}`;
        if (metadata.perspectives) metaInfo += ` | Perspectivas: ${metadata.perspectives}`;
        if (metadata.tokens) metaInfo += ` | Tokens: ${metadata.tokens}`;
        if (metadata.file) metaInfo += ` | Procesamiento de archivo`;
    }
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
            ${formatMessage(message)}
            ${metaInfo ? `<div class="message-meta">${metaInfo}</div>` : ''}
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

function addLoadingMessage(text = 'Pensando...') {
    const messagesContainer = document.getElementById('chat-messages');
    const loadingId = 'loading-' + Date.now();
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    messageDiv.id = loadingId;
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
            <div class="loading-message">
                <span>${text}</span>
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
    
    return loadingId;
}

function removeLoadingMessage(loadingId) {
    const loadingElement = document.getElementById(loadingId);
    if (loadingElement) {
        loadingElement.remove();
    }
}

function scrollToBottom() {
    const chatContainer = document.getElementById('chat-container');
    setTimeout(() => {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }, 100);
}

function formatMessage(text) {
    // Simple markdown-like formatting
    let formatted = escapeHtml(text);
    
    // Bold text **text**
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Line breaks
    formatted = formatted.replace(/\n/g, '<br>');
    
    return formatted;
}

function showAlert(message, type = 'info') {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 2000; max-width: 400px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to body
    document.body.appendChild(alertDiv);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Additional utility functions
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showAlert('¡Copiado al portapapeles!', 'success');
    }).catch(function(err) {
        console.error('Copy failed:', err);
        showAlert('Error al copiar al portapapeles', 'danger');
    });
}

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Ctrl/Cmd + / to toggle sidebar
    if ((event.ctrlKey || event.metaKey) && event.key === '/') {
        event.preventDefault();
        document.getElementById('sidebar-toggle').click();
    }
});

// Handle file drag and drop
document.addEventListener('DOMContentLoaded', function() {
    const chatContainer = document.getElementById('chat-container');
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        chatContainer.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        chatContainer.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        chatContainer.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight(e) {
        chatContainer.classList.add('dragover');
    }
    
    function unhighlight(e) {
        chatContainer.classList.remove('dragover');
    }
    
    chatContainer.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            const file = files[0];
            document.getElementById('file-input').files = files;
            handleFileSelection({ target: { files: files } });
        }
    }
});