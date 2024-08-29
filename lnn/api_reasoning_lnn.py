from fol.fol import parse_fol_to_lnn
from lnn.infer_answer import infer_answer
from lnn.inference import inference


def lnn_infer_from_facts_rules(facts, rules, questions):

    variables, predicates, formulaes = parse_fol_to_lnn(rules)

    data_graph, graph_links = inference(variables, predicates, formulaes, facts)

    answer = infer_answer(data_graph, graph_links, questions)
    return answer
