import os
from chatbot import *
from test_dataset import *
from evaluation_pipeline import *
from dotenv import load_dotenv

load_dotenv()


def logicQA_dataset():
    max_size = evaluation_size = int(os.getenv("MAX_SIZE"))

    dataset = LogiQADataset(max_size=max_size)

    chatbot = ChatBotFactory.create_chatbot(chatbot_type="ollama")

    pipeline = EvaluationPipeline(dataset, chatbot)
    labels, predictions = pipeline.fol_symbolic_prediction(max_size=max_size)

    print("Labels:", labels, "Predictions:", predictions)


def folio_dataset(infer_from_available_fols: bool, file_test: str):
    if infer_from_available_fols:
        max_size = 10
        dataset = FOLIODataset(max_size=max_size, file_names=[file_test])
        pipeline = EvaluationPipelineFOLIO(dataset, chatbot=None)
        pipeline.fol_symbolic_prediction(max_size=max_size)
    else:
        max_size = evaluation_size = int(os.getenv("MAX_SIZE"))
        dataset = FOLIODataset(max_size=max_size)
        chatbot = ChatBotFactory.create_chatbot(chatbot_type="genmini")
        pipeline = EvaluationPipelineFOLIO(dataset, chatbot)
        pipeline.convert_natural_language_to_fol()
        pipeline.fol_symbolic_prediction(
            max_size=max_size,
        )


if __name__ == "__main__":
    file_test = "pass.jsonl"
    folio_dataset(infer_from_available_fols=True, file_test=file_test)
