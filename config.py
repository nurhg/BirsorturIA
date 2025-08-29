import os


class Config:
    # Groq API configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

    # Available models with their descriptions
    AVAILABLE_MODELS = {
        'llama3-8b': {
            'id': 'llama3-8b-8192',
            'name': 'Llama 3 8B',
            'description': 'Fast and efficient for general tasks',
            'context_window': 8192
        },
        'llama3-70b': {
            'id': 'llama3-70b-8192',
            'name': 'Llama 3 70B',
            'description': 'Most capable model for complex reasoning',
            'context_window': 8192
        },
        'mixtral': {
            'id': 'mixtral-8x7b-32768',
            'name': 'Mixtral 8x7B',
            'description': 'Excellent for long context tasks',
            'context_window': 32768
        },
        'gemma': {
            'id': 'gemma-7b-it',
            'name': 'Gemma 7B',
            'description': 'Google\'s efficient instruction-tuned model',
            'context_window': 8192
        },
        'gpt-oss-20b': {
            'id': 'openai/gpt-oss-20b',
            'name': 'GPT-OSS 20B',
            'description': 'OpenAI\'s Como ChatGPT rapido',
            'context_window': 131072
        },
        'gpt-oss-120b': {
            'id': 'openai/gpt-oss-120b',
            'name': 'GPT-OSS 20B',
            'description': 'OpenAI\'s Como ChatGPT Potente',
            'context_window': 131072
        }
    }

    # Vision models for image analysis
    VISION_MODELS = {
        'meta-llama/llama-4-scout-17b-16e-instruct': {
            'name': 'Meta llama 4',
            'description': 'Advanced vision-language model for image analysis',
            'context_window': 8192
        }
    }

    # Default model
    DEFAULT_MODEL = "llama3-8b"

    # File processing settings
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'txt', 'pdf'}

    # Pro mode settings
    PRO_MODE_QUERIES = 3  # Number of queries for synthesis in pro mode
