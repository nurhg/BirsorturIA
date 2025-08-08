import logging
from flask import Blueprint, request, jsonify
from services.file_processor import FileProcessor
from services.groq_client import GroqClient
from utils.validators import RequestValidator

logger = logging.getLogger(__name__)

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    Handle file uploads and optional AI processing.
    
    Form data:
    - file: The uploaded file (PDF or TXT)
    - process_with_ai: "true" to process with AI (optional)
    - model: AI model to use (optional)
    - question: Question about the file content (optional)
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                "error": "No file provided",
                "message": "Please upload a file"
            }), 400
        
        file = request.files['file']
        
        # Process the file
        logger.info(f"Processing uploaded file: {file.filename}")
        file_info = FileProcessor.process_file(file)
        
        # Check if AI processing is requested
        process_with_ai = request.form.get('process_with_ai', '').lower() == 'true'
        
        result = {
            "success": True,
            "file_info": {
                "filename": file_info["filename"],
                "size": file_info["size"],
                "type": file_info["type"],
                "word_count": file_info["word_count"]
            },
            "content_preview": file_info["content"][:500] + "..." if len(file_info["content"]) > 500 else file_info["content"]
        }
        
        if process_with_ai:
            # Validate API key
            if not RequestValidator.validate_groq_api_key():
                return jsonify({
                    "error": "Configuration error",
                    "message": "Groq API key not configured"
                }), 500
            
            # Get AI processing parameters
            model = request.form.get('model', 'llama3-8b')
            question = request.form.get('question', '').strip()
            
            # Validate model
            from config import Config
            if model not in Config.AVAILABLE_MODELS:
                return jsonify({
                    "error": "Invalid model",
                    "message": f"Available models: {list(Config.AVAILABLE_MODELS.keys())}"
                }), 400
            
            # Generate AI response
            groq_client = GroqClient()
            
            if question:
                # Answer specific question about the file
                message = f"Based on the uploaded document, please answer: {question}"
            else:
                # Provide general summary
                message = "Please provide a comprehensive summary and analysis of this document."
            
            logger.info(f"Processing file with AI using model: {model}")
            ai_response = groq_client.chat_completion(
                message=message,
                model=model,
                context=file_info["content"]
            )
            
            result["ai_analysis"] = {
                "response": ai_response["content"],
                "model": ai_response["model"],
                "question": question if question else "General analysis",
                "usage": ai_response.get("usage", {})
            }
        
        logger.info(f"File upload processed successfully: {file_info['filename']}")
        return jsonify(result)
        
    except ValueError as e:
        logger.warning(f"File processing validation error: {e}")
        return jsonify({
            "error": "File processing error",
            "message": str(e)
        }), 400
    
    except Exception as e:
        logger.error(f"File upload processing error: {e}")
        return jsonify({
            "error": "Upload processing error",
            "message": "Failed to process uploaded file"
        }), 500

@upload_bp.route('/analyze', methods=['POST'])
def analyze_content():
    """
    Analyze provided text content with AI.
    
    Expected JSON payload:
    {
        "content": "Text content to analyze",
        "question": "Specific question" (optional),
        "model": "llama3-8b" (optional),
        "mode": "basic|pro" (optional)
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
        
        # Validate content
        content = data.get('content', '').strip()
        if not content:
            return jsonify({
                "error": "No content provided",
                "message": "Content field is required"
            }), 400
        
        if len(content) > 50000:
            return jsonify({
                "error": "Content too large",
                "message": "Content cannot exceed 50,000 characters"
            }), 400
        
        # Get parameters
        question = data.get('question', '').strip()
        model = data.get('model', 'llama3-8b')
        mode = data.get('mode', 'basic')
        
        # Validate model
        from config import Config
        if model not in Config.AVAILABLE_MODELS:
            return jsonify({
                "error": "Invalid model",
                "message": f"Available models: {list(Config.AVAILABLE_MODELS.keys())}"
            }), 400
        
        if mode not in ['basic', 'pro']:
            return jsonify({
                "error": "Invalid mode",
                "message": "Mode must be either 'basic' or 'pro'"
            }), 400
        
        # Prepare message
        if question:
            message = f"Based on the provided content, please answer: {question}"
        else:
            message = "Please provide a comprehensive analysis and summary of this content."
        
        # Generate AI response
        groq_client = GroqClient()
        
        if mode == 'pro':
            logger.info(f"Analyzing content with pro mode using model: {model}")
            ai_response = groq_client.pro_mode_completion(
                message=message,
                model=model,
                context=content
            )
        else:
            logger.info(f"Analyzing content with basic mode using model: {model}")
            ai_response = groq_client.chat_completion(
                message=message,
                model=model,
                context=content
            )
        
        result = {
            "success": True,
            "analysis": ai_response["content"],
            "model": ai_response["model"],
            "mode": ai_response.get("mode", mode),
            "question": question if question else "General analysis",
            "content_stats": {
                "character_count": len(content),
                "word_count": len(content.split())
            },
            "usage": ai_response.get("usage", {}),
            "metadata": {
                "finish_reason": ai_response.get("finish_reason"),
                "perspectives_analyzed": ai_response.get("perspectives_analyzed")
            }
        }
        
        logger.info(f"Content analysis completed successfully with model: {model}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Content analysis error: {e}")
        return jsonify({
            "error": "Analysis error",
            "message": "Failed to analyze content"
        }), 500
