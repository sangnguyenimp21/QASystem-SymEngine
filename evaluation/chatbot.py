from abc import ABC, abstractmethod
from openai import OpenAI

class ChatBot(ABC):
    def __init__(self, key: str='', base_url: str='', model_name: str='') -> None:
        super().__init__()
        self.key = key
        self.base_url = base_url
        self.model_name = model_name

    @abstractmethod
    def init_client(self):
        pass

    @abstractmethod
    def get_response(self, messages):
        pass

class OpenAIChatBot(ChatBot):
    def __init__(self, key: str='', base_url: str='', model_name='gpt-3.5-turbo-1106') -> None:
        super().__init__(key, base_url, model_name)
        self.client = self.init_client()

    def init_client(self):
        return OpenAI(api_key=self.key, base_url=self.base_url)

    def get_response(self, messages, temperature=0):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature
        )

        text = response.choices[0].message.content

        return text

class OllamaChatbot(OpenAIChatBot):
    def __init__(self, key: str='ollama', base_url: str='http://localhost:11434/v1', model_name='mistral:7b') -> None:
        super().__init__(key, base_url, model_name)
    
class ChatBotFactory:
    @staticmethod
    def create_chatbot(chatbot_type: str, key: str='', base_url: str='', model_name: str='') -> ChatBot:
        if chatbot_type == 'openai':
            return OpenAIChatBot(key, base_url, model_name)
        elif chatbot_type == 'ollama':
            key = 'ollama'
            base_url = 'http://localhost:11434/v1'
            model_name = 'mistral:7b'
            
            return OllamaChatbot(key, base_url, model_name)
        else:
            raise ValueError(f'Invalid chatbot type: {chatbot_type}')