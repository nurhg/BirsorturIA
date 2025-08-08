// Chatbot API Interface JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the interface
    initializeInterface();
    checkAPIStatus();
    setupEventListeners();
});

function initializeInterface() {
    // Initialize Bootstrap tabs
    const tabTriggerList = document.querySelectorAll('#mainTabs button');
    tabTriggerList.forEach(trigger => {
        new bootstrap.Tab(trigger);
    });
    
    // Setup AI options toggle
    const processWithAI = document.getElementById('process-with-ai');
    const aiOptions = document.getElementById('ai-options');
    
    processWithAI.addEventListener('change', function() {
        aiOptions.style.display = this.checked ? 'block' : 'none';
    });
}

function setupEventListeners() {
    // Chat form submission
    document.getElementById('chat-form').addEventListener('submit', handleChatSubmission);
    
    // Upload form submission
    document.getElementById('upload-form').addEventListener('submit', handleUploadSubmission);
    
    // File input change
    document.getElementById('file-input').addEventListener('change', handleFileSelection);
}

async function checkAPIStatus() {
    const statusElement = document.getElementById('api-status');
    
    try {
        const response = await fetch('/health');
        const data = await response.json();
        
        if (response.ok && data.status === 'healthy') {
            statusElement.innerHTML = `
                <span class="status-indicator status-healthy"></span>
                <span class="text-success">API is healthy and ready</span>
            `;
        } else {
            throw new Error('API unhealthy');
        }
    } catch (error) {
        statusElement.innerHTML = `
            <span class="status-indicator status-error"></span>
            <span class="text-danger">API connection failed</span>
        `;
        console.error('API status check failed:', error);
    }
}

async function handleChatSubmission(event) {
    event.preventDefault();
    
    const submitButton = document.getElementById('chat-submit');
    const responseContainer = document.getElementById('chat-response-container');
    const responseContent = document.getElementById('chat-response-content');
    const responseMeta = document.getElementById('chat-response-meta');
    
    // Get form data
    const message = document.getElementById('chat-message').value.trim();
    const model = document.getElementById('chat-model').value;
    const mode = document.getElementById('chat-mode').value;
    const context = document.getElementById('chat-context').value.trim();
    
    if (!message) {
        showAlert('Please enter a message', 'warning');
        return;
    }
    
    // Show loading state
    submitButton.disabled = true;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    responseContainer.style.display = 'none';
    
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
        
        if (response.ok && data.success) {
            // Display response
            responseContent.innerHTML = `<div class="response-content">${escapeHtml(data.response)}</div>`;
            
            // Display metadata
            let metaInfo = `Model: ${data.model} | Mode: ${data.mode}`;
            if (data.metadata.perspectives_analyzed) {
                metaInfo += ` | Perspectives: ${data.metadata.perspectives_analyzed}`;
            }
            if (data.usage.total_tokens) {
                metaInfo += ` | Tokens: ${data.usage.total_tokens}`;
            }
            responseMeta.textContent = metaInfo;
            
            responseContainer.style.display = 'block';
            responseContainer.scrollIntoView({ behavior: 'smooth' });
        } else {
            throw new Error(data.message || 'Failed to get response');
        }
    } catch (error) {
        console.error('Chat error:', error);
        showAlert(`Error: ${error.message}`, 'danger');
    } finally {
        // Reset button
        submitButton.disabled = false;
        submitButton.innerHTML = '<i class="fas fa-paper-plane"></i> Send Message';
    }
}

async function handleUploadSubmission(event) {
    event.preventDefault();
    
    const submitButton = document.getElementById('upload-submit');
    const responseContainer = document.getElementById('upload-response-container');
    const responseContent = document.getElementById('upload-response-content');
    
    const fileInput = document.getElementById('file-input');
    const processWithAI = document.getElementById('process-with-ai').checked;
    const model = document.getElementById('upload-model').value;
    const question = document.getElementById('upload-question').value.trim();
    
    if (!fileInput.files[0]) {
        showAlert('Please select a file', 'warning');
        return;
    }
    
    // Show loading state
    submitButton.disabled = true;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    responseContainer.style.display = 'none';
    
    try {
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        
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
        
        if (response.ok && data.success) {
            // Display file info and results
            let html = `
                <div class="file-info mb-3">
                    <h6><i class="fas fa-file"></i> File Information</h6>
                    <ul class="list-unstyled mb-0">
                        <li><strong>Name:</strong> ${escapeHtml(data.file_info.filename)}</li>
                        <li><strong>Size:</strong> ${formatFileSize(data.file_info.size)}</li>
                        <li><strong>Type:</strong> ${data.file_info.type.toUpperCase()}</li>
                        <li><strong>Words:</strong> ${data.file_info.word_count.toLocaleString()}</li>
                    </ul>
                </div>
            `;
            
            if (data.content_preview) {
                html += `
                    <div class="mb-3">
                        <h6><i class="fas fa-eye"></i> Content Preview</h6>
                        <div class="response-content">${escapeHtml(data.content_preview)}</div>
                    </div>
                `;
            }
            
            if (data.ai_analysis) {
                html += `
                    <div class="mb-3">
                        <h6><i class="fas fa-brain"></i> AI Analysis</h6>
                        <div class="response-content">${escapeHtml(data.ai_analysis.response)}</div>
                        <div class="mt-2">
                            <small class="text-muted">
                                Model: ${data.ai_analysis.model} | 
                                Question: ${escapeHtml(data.ai_analysis.question)}
                            </small>
                        </div>
                    </div>
                `;
            }
            
            responseContent.innerHTML = html;
            responseContainer.style.display = 'block';
            responseContainer.scrollIntoView({ behavior: 'smooth' });
        } else {
            throw new Error(data.message || 'Failed to process file');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showAlert(`Error: ${error.message}`, 'danger');
    } finally {
        // Reset button
        submitButton.disabled = false;
        submitButton.innerHTML = '<i class="fas fa-upload"></i> Upload & Process';
    }
}

function handleFileSelection(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Validate file size
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
        showAlert('File size exceeds 10MB limit', 'danger');
        event.target.value = '';
        return;
    }
    
    // Validate file type
    const allowedTypes = ['text/plain', 'application/pdf'];
    if (!allowedTypes.includes(file.type)) {
        showAlert('Only PDF and TXT files are supported', 'danger');
        event.target.value = '';
        return;
    }
}

function showAlert(message, type = 'info') {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at top of container
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
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

// Additional utility functions for enhanced UX
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showAlert('Copied to clipboard!', 'success');
    }).catch(function(err) {
        console.error('Copy failed:', err);
        showAlert('Failed to copy to clipboard', 'danger');
    });
}

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Ctrl/Cmd + Enter to submit chat form
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
        const activeTab = document.querySelector('.tab-pane.active');
        if (activeTab && activeTab.id === 'chat') {
            const chatForm = document.getElementById('chat-form');
            chatForm.dispatchEvent(new Event('submit'));
        }
    }
});
