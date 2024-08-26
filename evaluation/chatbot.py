from abc import ABC, abstractmethod
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class ChatBot(ABC):
    def __init__(self, key: str='', base_url: str='', model: str='') -> None:
        super().__init__()
        self.key = key
        self.base_url = base_url
        self.model = model

    @abstractmethod
    def init_client(self):
        pass

class OpenAIChatBot(ChatBot):
    def __init__(self, key: str='', base_url: str='', model='gpt-3.5-turbo-1106') -> None:
        super().__init__(key, base_url, model)
        self.client = self.init_client()

    def init_client(self):
        return OpenAI(api_key=self.key)

    def get_response(self, messages, temperature=0):
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature
        )