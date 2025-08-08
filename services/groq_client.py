import requests
import logging
from typing import Dict, List, Optional
from config import Config

logger = logging.getLogger(__name__)

class GroqClient:
    def __init__(self):
        self.api_key = Config.GROQ_API_KEY
        self.api_url = Config.GROQ_API_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, payload: Dict) -> Dict:
        """Make a request to the Groq API."""
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Groq API request failed: {e}")
            raise Exception(f"Failed to communicate with Groq API: {str(e)}")
    
    def chat_completion(self, 
                       message: str, 
                       model: str = Config.DEFAULT_MODEL,
                       context: Optional[str] = None,
                       system_prompt: Optional[str] = None) -> Dict:
        """Get a chat completion from Groq."""
        
        # Validate model
        if model not in Config.AVAILABLE_MODELS:
            raise ValueError(f"Invalid model. Available models: {list(Config.AVAILABLE_MODELS.keys())}")
        
        model_id = Config.AVAILABLE_MODELS[model]
        
        # Build messages
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        if context:
            messages.append({"role": "system", "content": f"Context information: {context}"})
        
        messages.append({"role": "user", "content": message})
        
        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000,
            "stream": False
        }
        
        logger.debug(f"Sending request to Groq with model: {model_id}")
        response = self._make_request(payload)
        
        return {
            "content": response["choices"][0]["message"]["content"],
            "model": model,
            "usage": response.get("usage", {}),
            "finish_reason": response["choices"][0].get("finish_reason")
        }
    
    def pro_mode_completion(self, 
                           message: str, 
                           model: str = Config.DEFAULT_MODEL,
                           context: Optional[str] = None) -> Dict:
        """Generate enhanced response using multiple queries and synthesis."""
        
        try:
            # Step 1: Generate multiple perspective queries
            perspectives = [
                f"Analyze this comprehensively: {message}",
                f"Provide detailed insights about: {message}",
                f"What are the key aspects and implications of: {message}"
            ]
            
            responses = []
            
            # Step 2: Get responses for each perspective
            for i, perspective in enumerate(perspectives):
                try:
                    response = self.chat_completion(
                        perspective, 
                        model=model, 
                        context=context,
                        system_prompt="Provide a detailed, analytical response with specific examples and insights."
                    )
                    responses.append(response["content"])
                    logger.debug(f"Pro mode query {i+1} completed")
                except Exception as e:
                    logger.warning(f"Pro mode query {i+1} failed: {e}")
                    continue
            
            if not responses:
                raise Exception("All pro mode queries failed")
            
            # Step 3: Synthesize all responses
            synthesis_prompt = f"""
            Based on the following multiple analytical responses to the question "{message}", 
            create a comprehensive, well-structured final answer that synthesizes the best insights:
            
            {chr(10).join([f"Response {i+1}: {resp}" for i, resp in enumerate(responses)])}
            
            Provide a detailed, authoritative response that combines the best elements from all perspectives.
            """
            
            final_response = self.chat_completion(
                synthesis_prompt,
                model=model,
                context=context,
                system_prompt="You are an expert synthesizer. Create comprehensive, well-structured responses."
            )
            
            return {
                "content": final_response["content"],
                "model": model,
                "mode": "pro",
                "perspectives_analyzed": len(responses),
                "usage": final_response.get("usage", {})
            }
            
        except Exception as e:
            logger.error(f"Pro mode completion failed: {e}")
            # Fallback to basic mode
            logger.info("Falling back to basic mode")
            basic_response = self.chat_completion(message, model=model, context=context)
            basic_response["mode"] = "basic (fallback)"
            return basic_response
