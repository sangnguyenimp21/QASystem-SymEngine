import os
from chatbot import *
from test_dataset import *
from evaluation_pipeline import *
from dotenv import load_dotenv

load_dotenv()
    
if __name__ == '__main__':
    max_size = evaluation_size = 100

    dataset = LogiQADataset(max_size=max_size)

    chatbot = ChatBotFactory.create_chatbot(chatbot_type='gemini', key=os.getenv('GEMINI_API_KEY'))

    pipeline = EvaluationPipeline(dataset, chatbot)
    labels, predictions = pipeline.fol_symbolic_prediction(max_size=max_size)

    print('Labels:', labels, 'Predictions:', predictions)
