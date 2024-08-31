from chatbot import *
from test_dataset import *
from evaluation_pipeline import *

if __name__ == "__main__":
    max_size = evaluation_size = 10

    dataset = LogiQADataset(max_size=max_size)

    chatbot = OpenAIChatBot(key=os.getenv("OPENAI_API_KEY"), model_name="gpt-4o-mini")

    pipeline = EvaluationPipeline(dataset, chatbot)
    labels, predictions = pipeline.fol_symbolic_prediction(max_size=max_size)

    print("Labels:", labels, "Predictions:", predictions)
