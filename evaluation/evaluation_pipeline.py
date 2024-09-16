import sys
from abc import ABC
from test_dataset import TestDataset
from chatbot import ChatBot, GeminiChatbot
import json

sys.path.append("../")
from fol import save_load_fol

from reasoning import api_reasoning_lnn


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

        response_text = response_text.replace('```json\n', '').replace('```', '').strip()
        
        return json.loads(response_text)

    def fol_to_lnn(self, fol):
        formatted_fol = dict()
        formatted_fol['expression'] = fol['premises']
        formatted_fol['facts'] = fol['facts']
        formatted_fol['question'] = fol['answers']

        fol_dataloader = save_load_fol.FOLDataLoader(data_source='api_request', request_data=formatted_fol)
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

            try:
                initial_prompt = self.dataset.build_initial_prompt(data)
                fol = self.nl_to_fol(initial_prompt=initial_prompt, recorrect=False)
                
                try:
                    rules, facts, questions = self.fol_to_lnn(fol)
                    result = api_reasoning_lnn.lnn_infer_from_facts_rules_result_only(facts=facts, rules=rules, questions=questions)
                    predictions.append(result)
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


class EvaluationPipelineFOLIO(ABC):
    def __init__(self, dataset: TestDataset, chatbot: ChatBot) -> None:
        self.dataset = dataset
        self.chatbot = chatbot

    def nl_to_fol(self, initial_prompt: str = "", recorrect: bool = True):
        response_text = GeminiChatbot.get_response(self.chatbot, initial_prompt)
        response_text = (
            response_text.replace("```json\n", "").replace("```", "").strip()
        )
        return json.loads(response_text)

    def fol_to_lnn(self, fol):
        formatted_fol = dict()
        formatted_fol["expression"] = fol["premises-FOL"]
        formatted_fol["facts"] = fol["facts"]
        formatted_fol["question"] = fol["answers-FOL"]

        fol_dataloader = save_load_fol.FOLDataLoader(
            data_source="api_request", request_data=formatted_fol
        )
        rules = fol_dataloader.get_fol_expressions()
        facts = fol_dataloader.get_facts()
        questions = fol_dataloader.get_question()

        return rules, facts, questions

    def fol_symbolic_prediction(self, max_size: int) -> None:

        labels = []
        predictions = []

        print("Evaluating FOL symbolic prediction...")
        print("-------------------------------------")

        for i in range(max_size):
            data = self.dataset[i]
            labels.append(data["label"])

            initial_prompt = self.dataset.build_initial_prompt(data)
            fol = self.nl_to_fol(initial_prompt=initial_prompt, recorrect=False)

            file_name = "output.json"
            with open(file_name, "a", encoding="utf-8") as json_file:
                json.dump(fol, json_file, ensure_ascii=False, indent=4)
            print(f"Dữ liệu đã được lưu vào file {file_name}")

            rules, facts, questions = self.fol_to_lnn(fol)
            result = api_reasoning_lnn.lnn_infer_from_facts_rules_result_only(
                facts=facts, rules=rules, questions=questions
            )
            print(f"Result: {result}")

            # try:
            #     initial_prompt = self.dataset.build_initial_prompt(data)
            #     fol = self.nl_to_fol(initial_prompt=initial_prompt, recorrect=False)

            #     try:
            #         facts, rules, questions = self.fol_to_lnn(fol)
            #         result = api_reasoning_lnn.lnn_infer_from_facts_rules(facts, rules, questions)
            #         print(f"Result: {result}")
            #     except Exception as e:
            #         print(f"Failed to infer from FOL: {e}")
            #         predictions.append('Fail_FOL_to_LNN')
            #         continue
            # except Exception as e:
            #     print(f"Failed to convert NL to FOL: {e}")
            #     predictions.append('Fail_NL_to_FOL')
            #     continue

        return labels, predictions
