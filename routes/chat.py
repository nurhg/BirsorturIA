import logging
from flask import Blueprint, request, jsonify
from services.groq_client import GroqClient
from utils.validators import RequestValidator

logger = logging.getLogger(__name__)

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
def chat():
    """
    Handle chat messages and return AI responses.
    
    Expected JSON payload:
    {
        "message": "Your message here",
        "model": "llama3-8b" (optional),
        "mode": "basic|pro" (optional),
        "context": "Additional context" (optional)
    }
    """
    try:
        # Validate API key
        if not RequestValidator.validate_groq_api_key():
            return jsonify({
                "error": "Configuration error",
                "message": "Groq API key not configured"
            }), 500
        
        # Get and validate request data
        data = request.get_json()
        if not data:
            return jsonify({
                "error": "Invalid request",
                "message": "JSON payload required"
            }), 400
        
        # Validate request
        validated_data = RequestValidator.validate_chat_request(data)
        
        # Initialize Groq client
        groq_client = GroqClient()
        
        # Generate response based on mode
        if validated_data['mode'] == 'pro':
            logger.info(f"Processing pro mode request with model: {validated_data['model']}")
            response = groq_client.pro_mode_completion(
                message=validated_data['message'],
                model=validated_data['model'],
                context=validated_data['context']
            )
        else:
            logger.info(f"Processing basic mode request with model: {validated_data['model']}")
            response = groq_client.chat_completion(
                message=validated_data['message'],
                model=validated_data['model'],
                context=validated_data['context']
            )
        
        # Build response
        result = {
            "success": True,
            "response": response["content"],
            "model": response["model"],
            "mode": response.get("mode", validated_data['mode']),
            "usage": response.get("usage", {}),
            "metadata": {
                "finish_reason": response.get("finish_reason"),
                "perspectives_analyzed": response.get("perspectives_analyzed")
            }
        }
        
        logger.info(f"Chat request completed successfully with model: {validated_data['model']}")
        return jsonify(result)
        
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return jsonify({
            "error": "Validation error",
            "message": str(e)
        }), 400
    
    except Exception as e:
        logger.error(f"Chat processing error: {e}")
        return jsonify({
            "error": "Processing error",
            "message": "Failed to process chat request"
        }), 500

@chat_bp.route('/models', methods=['GET'])
def get_models():
    """Get available AI models."""
    from config import Config
    
    return jsonify({
        "success": True,
        "models": Config.AVAILABLE_MODELS,
        "default_model": Config.DEFAULT_MODEL
    })
