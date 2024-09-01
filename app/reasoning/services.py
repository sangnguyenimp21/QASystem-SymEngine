from fol.save_load_fol import FOLDataLoader
from lnn.api_reasoning_lnn import lnn_infer_from_facts_rules_result_only
from .models import LNNReasoningModel

def lnn_reasoning(item: LNNReasoningModel):
    fol_dataloader = FOLDataLoader(data_source="api_request", request_data=item.dict())
    rules = fol_dataloader.get_fol_expressions()
    facts = fol_dataloader.get_facts()
    questions = fol_dataloader.get_question()
    result = lnn_infer_from_facts_rules_result_only(facts, rules, questions)

    return result