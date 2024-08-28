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

    def fol_to_lnn(self, data):
        response = self.get_fol_response(data)
        json_response = json.loads(response)

        # predicates = json_response['predicates']
        premises = json_response['premises']
        answer_premises = json_response['answer_premises']

        return {
            # 'predicates': predicates,
            'premises': premises,
            'answer_premises': answer_premises
        }
    
    def get_fol_response(self, data):
        prompt = self.init_convert_prompt_message(data) 

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
    
    def init_convert_prompt_message(self, data):
        prompt = f"""
        Your task is to convert the following natural language (NL) question and answers to first order logic (FOL) representation.

        The output must be in JSON format and has the following fields:
        * `predicates`: array of predicates based on context, in camel case with no space, and number of variables it takes e.g., `CamelCase(x,y)`
        * `premises`: array of premises constructed from the context, in FOL format
        * `answer_premises`: array of premises constructed from the answers and question, in FOL format

        IMPORTANT NOTES:
        * In FOL, use `→`, `↔`, `∧`, `¬`, `∨` only
        * If a sentence from the context is not necessary or not related to the question, do not include it in the FOL translation.
        * Do NOT always try to convert all NL sentences to FOL, only convert the necessary ones.

        --- Start of Example 1 ---
        # NL:
        Context: "Stranger Things" is a popular Netflix show. If a Netflix show is popular, Karen will binge-watch it.
        If and only if Karen binge-watches a Netflix show, she will download it. Karen does not download "Black Mirror".
        "Black Mirror" is a Netflix show. If Karen binge-watches a Netflix show, she will share it to Lisa.

        Question: According to the above information, which of the following can be true?

        Answer 1: Black Mirror is a popular.
        Answer 2: Black Mirror is not a popular.
        Answer 3: Karen will download Black Mirror.
        Answer 4: Karen will share Black Mirror to Lisa.

        # FOL translation:
        {{
            'predicates': [
                "NetflixShow(x)",
                "Popular(x)", 
                "BingeWatch(x, y)",
                "Download(x, y)", 
                "Share(x, y, z)"
            ],
            'premises': [
                "NetflixShow(strangerThings) ∧ Popular(strangerThings)", 
                "∀x,((NetflixShow(x) ∧ Popular(x)) → BingeWatch(karen, x))", 
                "∀x,((NetflixShow(x) ∧ BingeWatch(karen, x)) ↔ Download(karen, x))", 
                "NetflixShow(blackMirror) ∧ ¬Download(karen, blackMirror)", 
                "∀x,((NetflixShow(x) ∧ BingeWatch(karen, x)) → Share(karen, x, lisa))"
            ],
            'answer_premises': [
                "Popular(blackMirror)", 
                "¬Popular(blackMirror)", 
                "Download(karen, blackMirror)",
                "Share(karen, blackMirror, lisa)"
            ]
        }}
        --- End of Example 1 ---

        --- Start of Example 2 ---
        # NL:
        Context: The 2008 Summer Olympics were held in Beijing, China.
        The 2008 Summer Olympics were the second Summer Olympic Games to be held in a communist state.
        China won the most gold medals (48) in the 2008 Summer Olympics.
        The United States placed second in the gold medal tally but won the highest number of medals overall (112) in the 2008 Summer Olympics.
        The third place in the gold medal tally was achieved by Russia in the 2008 Summer Olympics.
        If a country places third in gold medals, then they had fewer gold medals than the team that won the most gold medals.
        87 countries won at least one medal during the 2008 Games.

        Question: According to the above information, which of the following can be true?

        Answer 1: Russia did not win fewer gold medals than China.

        # FOL translation:
        {{
            'predicates': [
                "HeldIn(x, y)",
                "SecondToBe(x, y)",
                "Won(x, y)",
                "Placed(x, y)",
                "FewerGoldMedalsThan(x, y)",
                "Country(x)"
            ],
            'premises': [
                "HeldIn(summer2008olympics, beijingchina)", 
                "SecondToBe(summer2008olympics, heldincommuniststate)", 
                "Won(china, mostgoldmedals)", 
                "Placed(unitedstates, secondingoldmedals) ∧ Won(unitedstates, highestnumberofmedals)", 
                "Placed(russia, thirdingoldmedals)", 
                "∀x∀y,(Placed(x, thirdingoldmedals) ∧ Won(y, mostgoldmedals) → FewerGoldMedalsThan(x, y))", 
                "∃x,(Country(x) ∧ Won(x, medal))",
            ],
            'answer_premises': [
                "¬FewerGoldMedalsThan(russia, china)"
            ]
        }}
        --- End of Example 2 ---

        Return only output as JSON, don't include any explaination.

        # NL: 
        Context: {data['text']}

        Question: {data['question']}

        {{Answers}}

        # FOL translation:

        """

        answers_str = ""
        for i, option in enumerate(data['options'], start=1):
            answers_str += f"Answer {i}: {option}\n"

        prompt = prompt.replace('{Answers}', answers_str)

        return prompt

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