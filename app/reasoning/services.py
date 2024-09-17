from fol.save_load_fol import FOLDataLoader
from reasoning.api_reasoning_lnn import *
from .models import LNNReasoningModel

def lnn_reasoning(item: LNNReasoningModel, using_explanation: bool = False):
    fol_dataloader = FOLDataLoader(data_source="api_request", request_data=item.dict())
    rules = fol_dataloader.get_fol_expressions()
    facts = fol_dataloader.get_facts()
    questions = fol_dataloader.get_question()

    if using_explanation:
        result = lnn_infer_from_facts_rules(facts, rules, questions)
    else:
        result = lnn_infer_from_facts_rules_result_only(facts, rules, questions)

    return result