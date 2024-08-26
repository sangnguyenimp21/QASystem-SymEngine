import os
from abc import ABC, abstractmethod
from typing import List
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


class TestDataset(ABC):
    def __init__(self, max_size=None, destination='./data', file_names: List[str] = []):
        self.max_size = max_size
        self.destination = destination
        self.file_names = file_names

    @abstractmethod
    def __getitem__(self, index):
        pass

    @abstractmethod
    def __len__(self):
        pass

class LogiQADataset(TestDataset):
    def __init__(self, max_size=None, destination='./data', file_names: List[str] = ['test_fol.jsonl']):
        super().__init__(max_size, destination, file_names)
        self.download_dataset()
        self.data = self.read_dataset()
        

    def download_dataset(self):
        """
        Downloads the dataset from a remote location and saves it to the specified destination.
        Returns:
            None
        Raises:
            None
        """
        destination = f'{self.destination}/logiQA_2.0'
        os.makedirs(destination, exist_ok=True)
        for file_name in self.file_names:
            if os.path.exists(f"{destination}/{file_name}"):
                continue

            # https://github.com/csitfun/LogiQA2.0/blob/main/logiqa/DATA/LOGIQA/test_fol.jsonl
            url = f"https://raw.githubusercontent.com/csitfun/LogiQA2.0/main/logiqa/DATA/LOGIQA/{file_name}"
            output_path = f"{destination}/{file_name}"
            response = requests.get(url, allow_redirects=True)
            
            if response.status_code != 200:
                print(f"Failed to download {file_name}")
                continue

            with open(output_path, mode="wb") as file:
                file.write(response.content)

    def read_dataset(self):
        """
        Reads the dataset from the specified destination.
        Returns:
            data: List of dictionaries containing the question, answer1, answer2, answer3, answer4, and label.
        Raises:
            ValueError: If the file type is not supported
        """
        destination = f'{self.destination}/logiQA_2.0'
        data = []
        for file_name in self.file_names:
            # check type is jsonl or txt
            if file_name.endswith('.jsonl'):
                jsonl_data = pd.read_json(f'{destination}/{file_name}', lines=True)
                for index, row in jsonl_data.iterrows():
                    data.append({
                        'text': row['text'],
                        'question': row['question'],
                        'options': row['options'],
                        'label': row['label']
                    })
                    if self.max_size and len(data) >= self.max_size:
                        break
                if self.max_size and len(data) >= self.max_size:
                    break
            else:
                raise ValueError(f"Unsupported file type: {file_name}")
        return data

    def __getitem__(self, index):
        return self.data[index]

    def __len__(self):
        if self.max_size:
            return self.max_size
        return len(self.data)