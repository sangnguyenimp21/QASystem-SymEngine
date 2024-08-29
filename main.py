# Ví dụ sử dụng hàm
from lnn.api_reasoning_lnn import lnn_infer_from_facts_rules
from fol.save_load_fol import get_facts, get_fol_expressions, get_question


def main():
    rules = get_fol_expressions()
    facts = get_facts()
    questions = get_question()
    result = lnn_infer_from_facts_rules(facts, rules, questions)
    print(result)


if __name__ == "__main__":
    main()
