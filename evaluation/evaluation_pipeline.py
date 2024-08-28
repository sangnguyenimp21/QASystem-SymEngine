from abc import ABC
from test_dataset import TestDataset
from chatbot import ChatBot

class EvaluationPipeline(ABC):
    def __init__(self, dataset: TestDataset, chatbot: ChatBot) -> None:
        self.dataset = dataset
        self.chatbot = chatbot

    def fol_symbolic_prediction(self):
        true_labels = []
        predicted_labels = []

        true_labels, predicted_labels = self.dataset.run_symbolic_prediction(self.chatbot)

        return true_labels, predicted_labels
        
