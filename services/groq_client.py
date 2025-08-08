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
                       system_prompt: Optional[str] = None,
                       conversation_history: Optional[List[Dict]] = None) -> Dict:
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
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
        
        # Always add the current message
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
                           context: Optional[str] = None,
                           conversation_history: Optional[List[Dict]] = None) -> Dict:
        """Generate enhanced response using multiple queries and synthesis."""
        
        try:
            # Construir contexto conversacional si existe historial
            conversation_context = ""
            if conversation_history and len(conversation_history) > 0:
                conversation_context = "\n\nContexto de la conversación anterior:\n"
                for msg in conversation_history[-4:]:  # Solo últimos 4 mensajes para no saturar
                    role_text = "Usuario" if msg["role"] == "user" else "Asistente"
                    conversation_context += f"{role_text}: {msg['content'][:200]}...\n"
                conversation_context += "\nTen en cuenta este contexto para responder de manera coherente.\n"
            
            # Step 1: Generate multiple perspective queries with context
            perspectives = [
                f"{conversation_context}Analiza esto de manera integral considerando el contexto previo: {message}",
                f"{conversation_context}Proporciona información detallada sobre: {message}",
                f"{conversation_context}¿Cuáles son los aspectos clave e implicaciones de: {message}?"
            ]
            
            responses = []
            
            # Step 2: Get responses for each perspective
            for i, perspective in enumerate(perspectives):
                try:
                    response = self.chat_completion(
                        perspective, 
                        model=model, 
                        context=context,
                        system_prompt="Proporciona una respuesta detallada y analítica con ejemplos específicos e información útil. Responde siempre en español."
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
            Basándote en las siguientes múltiples respuestas analíticas a la pregunta "{message}", 
            crea una respuesta final integral y bien estructurada que sintetice las mejores ideas:
            
            {chr(10).join([f"Respuesta {i+1}: {resp}" for i, resp in enumerate(responses)])}
            
            Proporciona una respuesta detallada y autoritativa que combine los mejores elementos de todas las perspectivas.
            """
            
            final_response = self.chat_completion(
                synthesis_prompt,
                model=model,
                context=context,
                system_prompt="Eres un experto sintetizador. Crea respuestas integrales y bien estructuradas. Responde siempre en español de manera clara y útil."
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
            basic_response = self.chat_completion(
                message, 
                model=model, 
                context=context, 
                conversation_history=conversation_history
            )
            basic_response["mode"] = "basic (fallback)"
            return basic_response
