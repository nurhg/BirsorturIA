import logging
from flask import Blueprint, request, jsonify
from services.groq_client import GroqClient
from utils.validators import RequestValidator
import base64

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

        # Get conversation history if provided
        conversation_history = data.get('conversation_history', [])

        # Generate response based on mode
        if validated_data['mode'] == 'pro':
            logger.info(f"Processing pro mode request with model: {validated_data['model']}")
            response = groq_client.pro_mode_completion(
                message=validated_data['message'],
                model=validated_data['model'],
                context=validated_data['context'],
                conversation_history=conversation_history
            )
        else:
            logger.info(f"Processing basic mode request with model: {validated_data['model']}")
            response = groq_client.chat_completion(
                message=validated_data['message'],
                model=validated_data['model'],
                context=validated_data['context'],
                conversation_history=conversation_history
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

@chat_bp.route('/chat/vision', methods=['POST'])
def vision_chat():
    """
    Handle chat requests with image analysis using vision models.

    Form data:
    - image: The image file to analyze
    - message: User's message/question about the image
    - model: Vision model to use (optional, defaults to llava-v1.5-7b-4096-preview)
    """
    try:
        # Validate API key
        if not RequestValidator.validate_groq_api_key():
            return jsonify({
                "error": "Configuration error",
                "message": "Groq API key not configured"
            }), 500

        # Check if image is present
        if 'image' not in request.files:
            return jsonify({
                "error": "No image provided",
                "message": "Please upload an image"
            }), 400

        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({
                "error": "No image selected",
                "message": "Please select an image file"
            }), 400

        # Validate image type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
        if image_file.content_type not in allowed_types:
            return jsonify({
                "error": "Invalid image type",
                "message": "Supported formats: JPEG, PNG, GIF, WebP"
            }), 400

        # Check file size (max 10MB)
        image_file.seek(0, 2)  # Seek to end
        file_size = image_file.tell()
        image_file.seek(0)  # Reset to beginning

        if file_size > 10 * 1024 * 1024:
            return jsonify({
                "error": "Image too large",
                "message": "Image size cannot exceed 10MB"
            }), 400

        # Get message and model
        message = request.form.get('message', 'Describe what you see in this image').strip()
        model = request.form.get('model', 'llama-3.2-11b-vision-preview')

        # Validate model (ensure it's a vision model)
        from config import Config
        vision_models = list(Config.VISION_MODELS.keys())
        if model not in vision_models:
            return jsonify({
                "error": "Invalid vision model",
                "message": f"Available vision models: {vision_models}"
            }), 400

        # Convert image to base64
        image_data = image_file.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')

        # Determine image format for data URL
        content_type = image_file.content_type
        
        # Ensure proper image format for Groq
        if content_type in ['image/jpeg', 'image/jpg']:
            mime_type = 'image/jpeg'
        elif content_type == 'image/png':
            mime_type = 'image/png'
        elif content_type == 'image/gif':
            mime_type = 'image/gif'
        elif content_type == 'image/webp':
            mime_type = 'image/webp'
        else:
            mime_type = 'image/jpeg'  # Default fallback
            
        image_url = f"data:{mime_type};base64,{image_base64}"

        logger.info(f"Processing vision request with model: {model}, image type: {mime_type}")

        # Generate AI response with image
        groq_client = GroqClient()
        ai_response = groq_client.vision_completion(
            message=message,
            image_url=image_url,
            model=model
        )

        result = {
            "success": True,
            "response": ai_response["content"],
            "model": ai_response["model"],
            "mode": "vision",
            "usage": ai_response.get("usage", {}),
            "metadata": {
                "image_analyzed": True,
                "image_size": file_size,
                "image_type": content_type,
                "finish_reason": ai_response.get("finish_reason")
            }
        }

        logger.info(f"Vision chat completed successfully with model: {model}")
        return jsonify(result)

    except ValueError as e:
        logger.warning(f"Vision chat validation error: {e}")
        return jsonify({
            "error": "Validation error",
            "message": str(e)
        }), 400

    except Exception as e:
        logger.error(f"Vision chat processing error: {e}")
        return jsonify({
            "error": "Vision processing error",
            "message": "Failed to process image analysis request"
        }), 500