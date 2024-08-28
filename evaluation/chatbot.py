from abc import ABC, abstractmethod
import json
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

    @abstractmethod
    def get_response(self, messages):
        pass

    def fol_to_lnn(self, initital_prompt=''):
        response = self.get_fol_response(initital_prompt=initital_prompt)
        json_response = json.loads(response)

        # predicates = json_response['predicates']
        premises = json_response['premises']
        answer_premises = json_response['answer_premises']

        return {
            # 'predicates': predicates,
            'premises': premises,
            'answer_premises': answer_premises
        }
    
    def get_fol_response(self, initital_prompt=''):
        prompt = initital_prompt

        messages = [
            {'role': 'system', 'content': 'You are expert in first order logic (FOL)'},
            {'role': 'user', 'content': prompt}
        ]

        response = self.get_response(messages)
            
        content = response.choices[0].message.content

        correct_prompt = f"""
        Given the following FOL translation:

        {content}

        Please check, correct them and provide a new translation in the correct format (no further explanation needed). You can redefine the predicates if needed. Some tips:
        * In FOL logic, there are no mathematic operators like <, >, =, ∑, +, -, *, /, etc. For example, `Joe has age less than 30 years old` can be translated as `LessThan30YearsOld(joe)`.
        * Always check for number of parentheses and ensure each open parenthesis should have a corresponding close parenthesis.
        * Nested predicates e.g., `P1(P2(x))` are invalid. Instead, you should define new variable and/or predicate to represent the natural language statement.
        * Make sure the premises are logically consistent and use the provided predicates.

        RETURN ONLY THE JSON OUTPUT, DO NOT INCLUDE ANY EXPLANATION.
        """

        correct_messages = [
            {
                'role': 'system',
                'content': 'You are QC who is expert in first order logic (FOL)'
            },
            {
                'role': 'user',
                'content': correct_prompt
            }
        ]

        correct_response = self.get_response(correct_messages)

        correct_content = correct_response.choices[0].message.content

        correct_response = correct_content.replace('```json\n', '').replace('```', '')

        correct_response = correct_response[correct_response.find('{'):correct_response.rfind('}')+1]

        return correct_response

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