import os
from abc import ABC, abstractmethod
from typing import List
import requests
import pandas as pd
from dotenv import load_dotenv
from chatbot import ChatBot
from lnn import *
from utils import *

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

    @abstractmethod
    def run_symbolic_prediction(self, chatbot: ChatBot):
        pass

    @abstractmethod
    def init_convert_prompt_message(self, data):
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
    
    def init_convert_prompt_message(self, data):
        prompt = f"""
        Your task is to convert the following natural language (NL) question and answers to first order logic (FOL) representation.

        The output must be in JSON format and has the following fields:
        * `predicates`: array of predicates based on context, in camel case with no space, and number of variables it takes e.g., `CamelCase(x,y)`
        * `premises`: array of premises constructed from the context, in FOL format
        * `answer_premises`: array of premises constructed from the answers and question, in FOL format

        IMPORTANT NOTES:
        * In FOL, use `→`, `↔`, `∧`, `¬`, `∨` only
        * If a sentence from the context is not necessary or not related to the question, do not include it in the FOL translation.
        * Do NOT always try to convert all NL sentences to FOL, only convert the necessary ones.

        --- Start of Example 1 ---
        # NL:
        Context: "Stranger Things" is a popular Netflix show. If a Netflix show is popular, Karen will binge-watch it.
        If and only if Karen binge-watches a Netflix show, she will download it. Karen does not download "Black Mirror".
        "Black Mirror" is a Netflix show. If Karen binge-watches a Netflix show, she will share it to Lisa.

        Question: According to the above information, which of the following can be true?

        Answer 1: Black Mirror is a popular.
        Answer 2: Black Mirror is not a popular.
        Answer 3: Karen will download Black Mirror.
        Answer 4: Karen will share Black Mirror to Lisa.

        # FOL translation:
        {{
            'predicates': [
                "NetflixShow(x)",
                "Popular(x)", 
                "BingeWatch(x, y)",
                "Download(x, y)", 
                "Share(x, y, z)"
            ],
            'premises': [
                "NetflixShow(strangerThings) ∧ Popular(strangerThings)", 
                "∀x,((NetflixShow(x) ∧ Popular(x)) → BingeWatch(karen, x))", 
                "∀x,((NetflixShow(x) ∧ BingeWatch(karen, x)) ↔ Download(karen, x))", 
                "NetflixShow(blackMirror) ∧ ¬Download(karen, blackMirror)", 
                "∀x,((NetflixShow(x) ∧ BingeWatch(karen, x)) → Share(karen, x, lisa))"
            ],
            'answer_premises': [
                "Popular(blackMirror)", 
                "¬Popular(blackMirror)", 
                "Download(karen, blackMirror)",
                "Share(karen, blackMirror, lisa)"
            ]
        }}
        --- End of Example 1 ---

        --- Start of Example 2 ---
        # NL:
        Context: The 2008 Summer Olympics were held in Beijing, China.
        The 2008 Summer Olympics were the second Summer Olympic Games to be held in a communist state.
        China won the most gold medals (48) in the 2008 Summer Olympics.
        The United States placed second in the gold medal tally but won the highest number of medals overall (112) in the 2008 Summer Olympics.
        The third place in the gold medal tally was achieved by Russia in the 2008 Summer Olympics.
        If a country places third in gold medals, then they had fewer gold medals than the team that won the most gold medals.
        87 countries won at least one medal during the 2008 Games.

        Question: According to the above information, which of the following can be true?

        Answer 1: Russia did not win fewer gold medals than China.

        # FOL translation:
        {{
            'predicates': [
                "HeldIn(x, y)",
                "SecondToBe(x, y)",
                "Won(x, y)",
                "Placed(x, y)",
                "FewerGoldMedalsThan(x, y)",
                "Country(x)"
            ],
            'premises': [
                "HeldIn(summer2008olympics, beijingchina)", 
                "SecondToBe(summer2008olympics, heldincommuniststate)", 
                "Won(china, mostgoldmedals)", 
                "Placed(unitedstates, secondingoldmedals) ∧ Won(unitedstates, highestnumberofmedals)", 
                "Placed(russia, thirdingoldmedals)", 
                "∀x∀y,(Placed(x, thirdingoldmedals) ∧ Won(y, mostgoldmedals) → FewerGoldMedalsThan(x, y))", 
                "∃x,(Country(x) ∧ Won(x, medal))",
            ],
            'answer_premises': [
                "¬FewerGoldMedalsThan(russia, china)"
            ]
        }}
        --- End of Example 2 ---

        Return only output as JSON, don't include any explaination.

        # NL: 
        Context: {data['text']}

        Question: {data['question']}

        {{Answers}}

        # FOL translation:

        """

        answers_str = ""
        for i, option in enumerate(data['options'], start=1):
            answers_str += f"Answer {i}: {option}\n"

        prompt = prompt.replace('{Answers}', answers_str)

        return prompt
    
    def run_symbolic_prediction(self, chatbot: ChatBot):
        """
        Runs symbolic prediction using the provided chatbot.

        Args:
            chatbot (ChatBot): The chatbot object used for prediction.

        Returns:
            tuple: A tuple containing the true labels and predicted labels.

        Raises:
            Exception: If there is an error while getting the response for a specific index.
        """
        true_labels = []
        predict_labels = []
        for index in range(len(self.data)):
            data = self.data[index]
            model = Model()
            true_labels.append(data['label'])

            try:
                response = chatbot.fol_to_lnn(initital_prompt=self.init_convert_prompt_message(data))
                fol_premises = response['premises']

                for fol_answer_premise in response['answer_premises']:
                    fol_premises = fol_premises + [fol_answer_premise]

                    variables, predicates, formulaes = setup_input_lnn(fol_premises)

                    predicate_objects = {name: Predicate(name, arity) for name, arity in predicates}
                    variable_objects = {var: Variable(var) for var in variables}

                    transformed_formulae = replace_predicates_and_variables(
                        formulaes, predicate_objects, variable_objects
                    )

                    model.add_knowledge(*transformed_formulae, world=World.AXIOM)

                    # Running inference
                    model.infer()

                    model.print()
            except Exception as e:
                predict_labels.append('None')
                print(f"Failed to get response for index {index}: {e}")

        return true_labels, predict_labels