import os
from dotenv import load_dotenv

load_dotenv()

class ChatBotConfigurations:
    OLLMA_CONFIG = {
        'key': 'ollama',
        'base_url': 'http://localhost:11434/v1',
        'model_name': 'mistral:7b'
    }

    OPENAI_GPT35_CONFIG = {
        'key': os.getenv('OPENAI_API_KEY'),
        'base_url': 'https://api.openai.com',
        'model_name': 'gpt-3.5-turbo-1106'
    }