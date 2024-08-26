import json
from abc import ABC, abstractmethod
from test_dataset import TestDataset
from chatbot import ChatBot

class EvaluationPipeline(ABC):
    def __init__(self, dataset: TestDataset, chatbot: ChatBot) -> None:
        self.dataset = dataset
        self.chatbot = chatbot

    def create_prompt_message(self, data):
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
                "∀x (NetflixShow(x) ∧ Popular(x) → BingeWatch(karen, x))", 
                "∀x (NetflixShow(x) ∧ BingeWatch(karen, x) ↔ Download(karen, x))", 
                "NetflixShow(blackMirror) ∧ ¬Download(karen, blackMirror)", 
                "∀x (NetflixShow(x) ∧ BingeWatch(karen, x) → Share(karen, x, lisa))"
            ],
            'answer_premises': [
                "Popular(blackMirror)", 
                "¬Popular(blackMirror)", 
                "Download(karen, blackMirror)",
                "Share(karen, blackMirror, lisa)"
            ]
        }}
        --- End of Example 1 ---

        Return only output as JSON, don't include any explaination.

        # NL: 
        Context: {data['text']}

        Question: {data['question']}

        Answer 1: {data['options'][0]}
        Answer 2: {data['options'][1]}
        Answer 3: {data['options'][2]}
        Answer 4: {data['options'][3]}

        # FOL translation:

        """

        return prompt
    
    def get_prompt_response(self, data):
        prompt = self.create_prompt_message(data) 

        messages = [
            {'role': 'system', 'content': 'You are expert in first order logic (FOL)'},
            {'role': 'user', 'content': prompt}
        ]

        response = self.chatbot.get_response(messages)
            
        content = response.choices[0].message.content

        correct_prompt = f"""
        Given the following FOL translation:

        {content}

        Please check, correct them and provide a new translation in the correct format (no further explanation needed). You can redefine the predicates if needed. Some tips:
        * In FOL logic, there are no mathematic operators like <, >, =, ∑, +, -, *, /, etc. For example, `Joe has age less than 30 years old` can be translated as `LessThan30YearsOld(joe)`.
        * Always check for number of parentheses and ensure each open parenthesis should have a corresponding close parenthesis.
        * Nested predicates e.g., `P1(P2(x))` are invalid. Instead, you should define new variable and/or predicate to represent the natural language statement.
        * Make sure the premises are logically consistent and use the provided predicates.
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

        correct_response = self.chatbot.get_response(correct_messages)

        correct_content = correct_response.choices[0].message.content

        correct_response = correct_content.replace('```json\n', '').replace('```', '')

        return correct_response
    
    def fol_to_lnn(self, data):
        response = self.get_prompt_response(data)
        json_response = json.loads(response)

        print(json_response)

        return json_response

    def evaluate(self):
        true_labels = []
        pred_labels = []
        for index in range(len(self.dataset)):
            data = self.dataset[index]
            true_labels.append(data['label'])

            try:
                response = self.fol_to_lnn(data)
                # pred_labels.append(response['label'])
            except Exception as e:
                print(f"Failed to get response for index {index}: {e}")
                pred_labels.append('None')

        return true_labels, pred_labels