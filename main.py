# Ví dụ sử dụng hàm
from reasoning.api_reasoning_lnn import (
    lnn_infer_from_facts_rules_result_only,
)
from fol.save_load_fol import *


def main():
    fol_dataloader = FOLDataLoader()
    rules = fol_dataloader.get_fol_expressions()
    facts = fol_dataloader.get_facts()
    questions = fol_dataloader.get_question()
    result = lnn_infer_from_facts_rules_result_only(facts, rules, questions)
    print(result)


if __name__ == "__main__":
    main()
