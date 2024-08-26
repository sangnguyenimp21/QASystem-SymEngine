from chatbot import *
from test_dataset import *
from evaluation_pipeline import *
    
if __name__ == '__main__':
    dataset = LogiQADataset(max_size=1)
    chatbot = OpenAIChatBot(key=os.getenv('OPENAI_API_KEY'), model='gpt-4o-mini')
    pipeline = EvaluationPipeline(dataset, chatbot)
    true_labels, pred_labels = pipeline.evaluate()
