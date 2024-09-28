import os
from pathlib import Path
import sys
from abc import ABC

import pandas as pd
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

    def nl_to_fol(self, initial_prompt: str = "", recorrect: bool = True):
        messages = [
            {
                "role": "system",
                "content": "You are a mathematician who is expert in first order logic (FOL) representation",
            },
            {"role": "user", "content": initial_prompt},
        ]

        response_text = self.chatbot.get_response(messages)

        response_text = (
            response_text.replace("```json\n", "").replace("```", "").strip()
        )

        return json.loads(response_text)

    def fol_to_lnn(self, fol):
        formatted_fol = dict()
        formatted_fol["expression"] = fol["premises"]
        formatted_fol["facts"] = fol["facts"]
        formatted_fol["question"] = fol["answers"]

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

            try:
                initial_prompt = self.dataset.build_initial_prompt(data)
                fol = self.nl_to_fol(initial_prompt=initial_prompt, recorrect=False)

                try:
                    rules, facts, questions = self.fol_to_lnn(fol)
                    result = api_reasoning_lnn.lnn_infer_from_facts_rules_result_only(
                        facts=facts, rules=rules, questions=questions
                    )
                    predictions.append(result)
                    print(f"Result: {result}")
                except Exception as e:
                    print(f"Failed to infer from FOL: {e}")
                    predictions.append("Fail_FOL_to_LNN")
                    continue
            except Exception as e:
                print(f"Failed to convert NL to FOL: {e}")
                predictions.append("Fail_NL_to_FOL")
                continue

        return labels, predictions


class EvaluationPipelineFOLIO(ABC):
    def __init__(self, dataset: TestDataset, chatbot: ChatBot) -> None:
        self.dataset = dataset
        self.chatbot = chatbot

    def _nl_to_fol(self, initial_prompt: str = "", recorrect: bool = True):
        response_text = GeminiChatbot.get_response(self.chatbot, initial_prompt)
        response_text = (
            response_text.replace("```json\n", "").replace("```", "").strip()
        )
        return json.loads(response_text)

    def _save_to_excel(
        self, questions_list, results_list, labels_list, output_file_path
    ):
        df = pd.DataFrame(
            {
                "Question": questions_list,
                "Result": results_list,
                "Label": labels_list,
            }
        )
        df.to_excel(output_file_path, index=True)
        print(f"Data has been saved to {output_file_path}")

    def fol_to_lnn(self, fol):
        formatted_fol = dict()
        formatted_fol["expression"] = fol["premises-FOL"]
        formatted_fol["facts"] = fol["facts"]
        formatted_fol["question"] = fol["conclusion-FOL"]

        fol_dataloader = save_load_fol.FOLDataLoader(
            data_source="api_request", request_data=formatted_fol
        )
        rules = fol_dataloader.get_fol_expressions()
        facts = fol_dataloader.get_facts()
        questions = fol_dataloader.get_question()

        return rules, facts, questions

    def convert_natural_language_to_fol(self, max_size: int) -> None:
        print("Convert From Natural Language To FOL...")
        print("-------------------------------------")
        for i in range(max_size):
            try:
                # Lấy dữ liệu từ dataset
                data = self.dataset[i]
                initial_prompt = self.dataset.build_initial_prompt(data)
                # Chuyển đổi ngôn ngữ tự nhiên sang FOL
                fol = self._nl_to_fol(initial_prompt=initial_prompt, recorrect=False)
                # Ghi kết quả vào file JSON
                file_name = "nl_to_fol_folio.json"
                with open(file_name, "a", encoding="utf-8") as json_file:
                    json.dump(fol, json_file, ensure_ascii=False, indent=4)
                print(f"Data has been saved to file {file_name}")

            except KeyError as e:
                print(f"KeyError encountered for index {i}: {e}")

            except FileNotFoundError as e:
                print(f"FileNotFoundError: {e}")
                break  # Thoát khỏi vòng lặp nếu không thể mở file

            except Exception as e:
                print(f"An error occurred at index {i}: {e}")

    def fol_symbolic_prediction(self, max_size: int) -> None:
        print("Evaluating FOL symbolic prediction...")
        print("-------------------------------------")

        questions_list = []
        results_list = []
        labels_list = []
        data = self.dataset.get_data_record()
        for i, item in enumerate(data[:max_size]):
            try:
                print(f"********  Processing element {i}  ***************")
                label = item.get("label", [])
                if label == "Uncertain":
                    label = "UNKNOWN"
                elif label == "True":
                    label = "TRUE"
                elif label == "False":
                    label = "FALSE"

                rules, facts, questions = self.fol_to_lnn(item)
                print(f"********  rules:  {rules} \n")
                print(f"********  facts:  {facts} \n")
                print(f"********  questions:  {questions} \n")

                # Sử dụng API để suy luận từ facts và rules
                result = api_reasoning_lnn.lnn_infer_from_facts_rules(
                    facts, rules, questions
                )
                # result_value = result.get("result")
                print(f"********  Label:  {label} \n")
                print(f"********  Result:  {result} \n")

                questions_list.append(questions)
                results_list.append(result)
                labels_list.append(label)

            except KeyError as e:
                print(f"KeyError encountered for element {i}: {e}")
            except Exception as e:
                print(f"An unexpected error occurred while processing element {i}: {e}")

        try:
            output_file = (
                f"../{self.dataset.get_data_directory()}/{"Inference_results.xlsx"}"
            )
            self._save_to_excel(
                questions_list,
                results_list,
                labels_list,
                output_file,
            )
        except Exception as e:
            print(f"An error occurred while saving to Excel: {e}")
