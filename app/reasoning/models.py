from pydantic import BaseModel

class LNNReasoningModel(BaseModel):
    expression: list[str]
    facts: dict[str, dict[str, str]]
    question: dict[str, str]