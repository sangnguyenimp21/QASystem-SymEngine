from abc import ABC, abstractmethod
import requests
from openai import OpenAI
import google.generativeai as genai

class ChatBot(ABC):
    def __init__(self, key: str='', base_url: str='', model_name: str='') -> None:
        super().__init__()
        self.key = key
        self.base_url = base_url
        self.model_name = model_name
        self.single_message = False

    @abstractmethod
    def init_client(self):
        pass

    @abstractmethod
    def get_response(self, messages):
        pass

    def transform_messages(self, messages):
        formatted_message = ''
        if type(messages) == list:
            for message in messages:
                formatted_message += f"{message['content']}\n"
        else:
            formatted_message = messages

        return formatted_message

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

class GemsuraChatbot(ChatBot):
    def __init__(self, key: str='', base_url: str='', model_name: str='') -> None:
        super().__init__(key, base_url, model_name)
        self.single_message = True

    def init_client(self):
        pass

    def get_response(self, messages):
        prompt = self.transform_messages(messages) if self.single_message else messages
        response = requests.post(
            'https://ws.gvlab.org/fablab/ura/llama/api/generate',
            headers={
                'Content-Type': 'application/json'
            },
            json={
                "inputs": f"user.{prompt}.model\n",
            }
        )

        text = response.json()['generated_text']

        return text
    
class GeminiChatbot(ChatBot):
    def __init__(self, key: str='', base_url: str='', model_name: str='') -> None:
        super().__init__(key, base_url, model_name)
        self.single_message = True
        self.client = self.init_client()

    def init_client(self):
        genai.configure(api_key=self.key)
        model = genai.GenerativeModel(self.model_name)
        return model

    def get_response(self, messages):
        messages = self.transform_messages(messages) if self.single_message else messages
        response = self.client.generate_content(messages)
        return response.text

class ChatBotFactory:
    @staticmethod
    def create_chatbot(chatbot_type: str, key: str='', base_url: str='', model_name: str='') -> ChatBot:
        if chatbot_type == 'openai':
            return OpenAIChatBot(key, base_url, model_name)
        elif chatbot_type == 'ollama':
            key = 'ollama' if key == '' else key
            base_url = 'http://localhost:11434/v1' if base_url == '' else base_url
            model_name = 'mistral:7b' if model_name == '' else model_name
            return OllamaChatbot(key, base_url, model_name)
        elif chatbot_type == 'gemsura':
            return GemsuraChatbot(key, base_url, model_name)
        elif chatbot_type == "gemini":
            key = "gemini" if key == "" else key
            model_name = "gemini-1.0-pro" if model_name == "" else model_name
            return GeminiChatbot(key, base_url, model_name)
        else:
            raise ValueError(f"Invalid chatbot type: {chatbot_type}")