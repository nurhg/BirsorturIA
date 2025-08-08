import os

class Config:
    # Groq API configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    
    # Available models
    AVAILABLE_MODELS = {
        "llama3-8b": "llama3-8b-8192",
        "llama3-70b": "llama3-70b-8192", 
        "mixtral": "mixtral-8x7b-32768",
        "gemma": "gemma-7b-it",
        "gpt-oss-20b": "openai/gpt-oss-20b",
        "gpt-oss-120b": "openai/gpt-oss-120b"
    }
    
    # Default model
    DEFAULT_MODEL = "llama3-8b"
    
    # File processing settings
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'txt', 'pdf'}
    
    # Pro mode settings
    PRO_MODE_QUERIES = 3  # Number of queries for synthesis in pro mode
