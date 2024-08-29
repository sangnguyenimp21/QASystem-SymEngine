from abc import ABC, abstractmethod
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


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
        return OpenAI(api_key=self.key)

    def get_response(self, messages, temperature=0):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature
        )

        text = response.choices[0].message.content

        return text