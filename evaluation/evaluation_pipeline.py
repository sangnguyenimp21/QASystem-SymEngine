import sys
from abc import ABC
from test_dataset import TestDataset
from chatbot import ChatBot
import json

sys.path.append('../')

from fol import save_load_fol
from lnn import api_reasoning_lnn


class EvaluationPipeline(ABC):
    def __init__(self, dataset: TestDataset, chatbot: ChatBot) -> None:
        self.dataset = dataset
        self.chatbot = chatbot

    def nl_to_fol(self, initial_prompt: str = '', recorrect: bool = True):
        messages = [
            {'role': 'system', 'content': 'You are a mathematician who is expert in first order logic (FOL) representation'},
            {'role': 'user', 'content': initial_prompt}
        ]

        response_text = self.chatbot.get_response(messages)
            
        if recorrect:
            correct_prompt = f"""
            Given the following FOL translation:

            {response_text}

            Please check, correct them and provide a new translation in the correct format (no further explanation needed). You can redefine the predicates if needed. Some tips:
            * In FOL logic, there are no mathematic operators like <, >, =, ∑, +, -, *, /, etc. For example, `Joe has age less than 30 years old` can be translated as `LessThan30YearsOld(joe)`.
            * Always check for number of parentheses and ensure each open parenthesis should have a corresponding close parenthesis.
            * Nested predicates e.g., `P1(P2(x))` are invalid. Instead, you should define new variable and/or predicate to represent the natural language statement.
            * Make sure the premises are logically consistent and use the provided predicates.

            RETURN ONLY THE JSON OUTPUT, DO NOT INCLUDE ANY EXPLANATION.
            """

            correct_messages = [
                {'role': 'system', 'content': 'You are a mathematician who is expert in first order logic (FOL) representation'},
                {'role': 'user', 'content': correct_prompt}
            ]

            response_text = self.chatbot.get_response(correct_messages)

        response_text = response_text.replace('```json\n', '').replace('```', '').strip()

        return json.loads(response_text)

    def fol_to_lnn(self, fol, filename: str='fol', file_type: str='json'):
        formatted_fol = dict()
        formatted_fol['expression'] = fol['premises']
        formatted_fol['facts'] = fol['facts']
        formatted_fol['question'] = fol['answer_premises'][0]

        filename = f'{self.dataset.get_data_directory()}/{filename}.{file_type}'
        with open(filename, 'w') as f:
            json.dump(formatted_fol, f)

        fol_dataloader = save_load_fol.FOLDataLoader(json_file_path=filename)
        rules = fol_dataloader.get_fol_expressions()
        facts = fol_dataloader.get_facts()
        questions = fol_dataloader.get_question()

        return rules, facts, questions

    def fol_symbolic_prediction(self, max_size: int) -> None:

        labels = []
        predictions = []

        print('Evaluating FOL symbolic prediction...')
        print('-------------------------------------')

        for i in range(max_size):
            data = self.dataset[i]
            labels.append(data['label'])

            initial_prompt = self.dataset.build_initial_prompt(data)

            try:
                fol = self.nl_to_fol(initial_prompt=initial_prompt, recorrect=True)
                
                try:
                    facts, rules, questions = self.fol_to_lnn(fol, filename=f'fol_{i}')
                    result = api_reasoning_lnn.lnn_infer_from_facts_rules(facts, rules, questions)
                    print(f"Result: {result}")
                except Exception as e:
                    print(f"Failed to infer from FOL: {e}")
                    predictions.append('Fail_FOL_to_LNN')
                    continue
            except Exception as e:
                print(f"Failed to convert NL to FOL: {e}")
                predictions.append('Fail_NL_to_FOL')
                continue

        return labels, predictions
        
