import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class RequestValidator:
    @staticmethod
    def validate_chat_request(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate chat request data."""
        errors = []
        
        # Check message
        message = data.get('message', '').strip()
        if not message:
            errors.append("Message is required and cannot be empty")
        elif len(message) > 4000:
            errors.append("Message cannot exceed 4000 characters")
        
        # Check model
        model = data.get('model', 'llama3-8b')
        from config import Config
        if model not in Config.AVAILABLE_MODELS:
            errors.append(f"Invalid model. Available models: {list(Config.AVAILABLE_MODELS.keys())}")
        
        # Check mode
        mode = data.get('mode', 'basic')
        if mode not in ['basic', 'pro']:
            errors.append("Mode must be either 'basic' or 'pro'")
        
        # Check context (optional)
        context = data.get('context', '')
        if context and len(context) > 8000:
            errors.append("Context cannot exceed 8000 characters")
        
        if errors:
            raise ValueError("; ".join(errors))
        
        return {
            'message': message,
            'model': model,
            'mode': mode,
            'context': context if context else None
        }
    
    @staticmethod
    def validate_groq_api_key() -> bool:
        """Validate that Groq API key is available."""
        from config import Config
        api_key = Config.GROQ_API_KEY
        
        if not api_key:
            logger.error("GROQ_API_KEY environment variable not set")
            return False
        
        if len(api_key) < 20:  # Basic sanity check
            logger.error("GROQ_API_KEY appears to be invalid (too short)")
            return False
        
        return True
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage."""
        # Remove any path components
        filename = filename.split('/')[-1].split('\\')[-1]
        
        # Replace unsafe characters
        filename = re.sub(r'[^\w\-_\.]', '_', filename)
        
        # Limit length
        if len(filename) > 100:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:95] + ('.' + ext if ext else '')
        
        return filename
