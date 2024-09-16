from fol.first_order_logic import parse_fol_to_lnn
from reasoning.infer_answer import (
    infer_answer_include_explanation,
    infer_answer_result_only,
    print_generalized_result,
)
from reasoning.inference import inference


def lnn_infer_from_facts_rules(facts, rules, questions):
    variables, predicates, formulaes = parse_fol_to_lnn(rules)
    data_graph, graph_links = inference(variables, predicates, formulaes, facts)
    # Bao gồm kết quả và giải thích
    answer = infer_answer_include_explanation(data_graph, graph_links, questions)
    print_generalized_result(answer)
    return answer


def lnn_infer_from_facts_rules_result_only(facts, rules, questions):
    variables, predicates, formulaes = parse_fol_to_lnn(rules)
    data_graph, graph_links = inference(variables, predicates, formulaes, facts)
    # Chỉ trả về kết quả
    answer = infer_answer_result_only(data_graph, graph_links, questions)
    return answer
