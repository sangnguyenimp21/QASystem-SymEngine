from reasoning.api_reasoning_lnn import (
    lnn_infer_from_facts_rules,
)
from fol.save_load_fol import *

import json
import pandas as pd


# Function to load JSON from a file
def load_json(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


def process_json_elements(data, sample_size, output_file):
    if sample_size is None:
        sample_size = len(data)

    questions_list = []
    results_list = []
    labels_list = []
    for i, item in enumerate(data[:sample_size]):
        print(f"********  Processing element {i}  ***************")
        rules = item.get("premises-FOL", [])
        facts = item.get("facts", [])
        questions = item.get("conclusion-FOL", [])
        result = lnn_infer_from_facts_rules(facts, rules, questions)
        if result and "result" in result:
            result_value = result.get("result")
        else:
            result_value = "An error occurred during the inference process."
            print("No result found in inference output.")

        label = item.get("label", [])
        if label == "Uncertain":
            label = "UNKNOWN"
        elif label == "True":
            label = "TRUE"
        elif label == "False":
            label == "FALSE"

        if result_value != label:
            count = count + 1

        questions_list.append(questions)
        results_list.append(result_value)
        labels_list.append(label)

    df = pd.DataFrame(
        {
            "Question": questions_list,
            "Result": results_list,
            "Label": labels_list,
        }
    )
    df.to_excel(output_file, index=True)
    print(f"Data has been saved to {output_file}")


def main_improve_reasoning():
    file_test = "data/FOLIO/test_folio.jsonl"
    path_output = "data/FOLIO/Inference_results.xlsx"
    sample_size = None
    data = load_json(file_test)
    process_json_elements(data, sample_size, path_output)


def main():
    fol_dataloader = FOLDataLoader()
    rules = fol_dataloader.get_fol_expressions()
    facts = fol_dataloader.get_facts()
    questions = fol_dataloader.get_question()
    label = fol_dataloader.get_label()
    result = lnn_infer_from_facts_rules(facts, rules, questions)
    result_value = result.get(
        "result", "No result"
    )  # Lấy giá trị 'result', nếu không có thì trả về 'No result'
    print(f"********  Label:  {label} \n")
    print(f"********  Result:  {result_value} \n")


if __name__ == "__main__":
    main()
