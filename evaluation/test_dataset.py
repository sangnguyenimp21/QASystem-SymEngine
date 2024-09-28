import json
import os
from abc import ABC, abstractmethod
from typing import List
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


class TestDataset(ABC):
    def __init__(self, max_size=None, destination="./data", file_names: List[str] = []):
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
    def get_data_directory(self):
        pass

    @abstractmethod
    def get_data_record(self):
        pass

    @abstractmethod
    def build_initial_prompt(self, data):
        pass


class LogiQADataset(TestDataset):
    def __init__(
        self,
        max_size=None,
        destination="./data",
        file_names: List[str] = ["test_fol.jsonl"],
    ):
        super().__init__(max_size, destination, file_names)
        self.data_directory = f"{destination}/logiQA_2.0"
        self.download_dataset()
        self.data = self.read_dataset()

    def __getitem__(self, index):
        return self.data[index]

    def __len__(self):
        if self.max_size:
            return self.max_size
        return len(self.data)

    def download_dataset(self):
        """
        Downloads the dataset from a remote location and saves it to the specified destination.
        Returns:
            None
        Raises:
            None
        """
        destination = self.data_directory
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
        destination = f"{self.destination}/logiQA_2.0"
        data = []
        for file_name in self.file_names:
            # check type is jsonl or txt
            if file_name.endswith(".jsonl"):
                jsonl_data = pd.read_json(f"{destination}/{file_name}", lines=True)
                for index, row in jsonl_data.iterrows():
                    data.append(
                        {
                            "text": row["text"],
                            "question": row["question"],
                            "options": row["options"],
                            "label": row["label"],
                        }
                    )
                    if self.max_size and len(data) >= self.max_size:
                        break
                if self.max_size and len(data) >= self.max_size:
                    break
            else:
                raise ValueError(f"Unsupported file type: {file_name}")
        return data

    def build_initial_prompt(self, data):
        prompt = f"""
        Your task is to convert the following natural language (NL) question and answers to first order logic (FOL) representation.

        The output must be in JSON format and has the following fields:
        * `predicates`: array of predicates based on context, in camel case with no space, and number of variables it takes e.g., `CamelCase(x,y)`
        * `premises`: array of premises in FOL logic based on the predicates
        * `facts`: dictionary like `{{"Predicate": {{"variable": "value"}}}}` (value can be "TRUE", "FALSE", or "UNKNOWN")
        * `answers`: dictionary `{{"Predicate": "variable"}}` (variable here is the same as the one in the facts)

        IMPORTANT NOTES:
        * In FOL, use `→`, `↔`, `∧`, `¬`, `∨` only
        * In FOL logic, there are no mathematic operators like <, >, ≥, ≤, =, ∑, +, -, *, /, etc. For example, `Joe has age less than 30 years old` can be translated as `LessThan30YearsOld(joe)`.
        * Nested predicates e.g., `P1(P2(x))` are invalid. Instead, you should define new variable and/or predicate to represent the natural language statement.
        * Make sure the premises are logically consistent and use the provided predicates.
        * DO NOT always try to convert all sentences to FOL, only convert the necessary ones.
        * For predicate with multiple variables, use hyphen `-` to separate the variables e.g., 'karen-strangerThings' means Karen and Stranger Things.
        * In premises, use `∃x,y,z,`, `∀x,y,z,`, instead of `∃x, ∃y, ∃z,`, `∀x, ∀y, ∀z,`. For example, `∀x,∀y,∀z,` = `∀x,y,z,`

        --- Start of Example ---
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
                "Share(x, y)",
                "IsBlackMirror(x)",
            ],
            'premises': [
                "∀x,y, (NetflixShow(x) ∧ Popular(x) → BingeWatch(y, x))",
                "∀x,y, (NetflixShow(x) ∧ IsBlackMirror(x) → ¬Download(y, x))",
                "∀x,y,z, (NetflixShow(x) ∧ BingeWatch(y, x) → Share(x, z) ∧ Download(y, x))"
            ],
            'facts': {{
                "NetflixShow": {{"strangerThings": "TRUE", "blackMirror": "TRUE"}},
                "Popular": {{"strangerThings": "TRUE", "blackMirror": "UNKNOWN"}},
                "BingeWatch": {{"karen-strangerThings": "UNKNOWN"}},
                "Download": {{"karen-strangerThings": "UNKNOWN", "karen-blackMirror": "UNKNOWN"}},
                "Share": {{"strangerThings-lisa": "UNKNOWN", "blackMirror-lisa": "UNKNOWN"}},
                "IsBlackMirror": {{"blackMirror": "TRUE"}}
            }},
            'answers': {{
                "Popular": "blackMirror", 
                "¬Popular": "blackMirror", 
                "Download": "karen-blackMirror", // karen and blackMirror are the variables
                "Share": "strangerThings-lisa"
            }}
        }}
        --- End of Example ---

        Return only output as JSON format, don't include any explaination.

        # NL: 
        Context: {data['text']}

        Question: {data['question']}

        {{Answers}}

        # FOL translation:

        """

        answers_str = ""
        for i, option in enumerate(data["options"], start=1):
            answers_str += f"Answer {i}: {option}\n"

        prompt = prompt.replace("{Answers}", answers_str)

        return prompt

    def get_data_directory(self):
        return self.data_directory


class FOLIODataset(TestDataset):
    def __init__(
        self,
        max_size=None,
        destination="./data",
        file_names: List[str] = ["folio-validation.jsonl"],
    ):
        super().__init__(max_size, destination, file_names)
        self.data_directory = f"{destination}/FOLIO"
        # self.download_dataset()
        self.data = self.read_dataset()

    def __getitem__(self, index):
        return self.data[index]

    def __len__(self):
        if self.max_size:
            return self.max_size
        return len(self.data)

    def download_dataset(self):
        """
        Downloads the dataset from a remote location and saves it to the specified destination.
        Returns:
            None
        Raises:
            None
        """
        destination = self.data_directory
        os.makedirs(destination, exist_ok=True)
        for file_name in self.file_names:
            if os.path.exists(f"{destination}/{file_name}"):
                continue

            # https://github.com/Yale-LILY/FOLIO/blob/main/data/v0.0/folio-train.jsonl
            url = f"https://github.com/Yale-LILY/FOLIO/blob/main/data/v0.0/{file_name}"
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
        destination = f"{self.destination}/FOLIO"
        data = []
        for file_name in self.file_names:
            # check type is jsonl or txt
            if file_name.endswith(".jsonl"):
                current_file_path = os.path.abspath(__file__)
                current_directory = os.path.dirname(current_file_path)
                parent_directory = os.path.dirname(current_directory)
                jsonl_data = pd.read_json(
                    f"{parent_directory}/{destination}/{file_name}", lines=False
                )
                for index, row in jsonl_data.iterrows():
                    # Khởi tạo dict với các trường bắt buộc
                    data_entry = {
                        "premises": row["premises"],
                        "premises-FOL": row["premises-FOL"],
                        "conclusion": row["conclusion"],
                        "conclusion-FOL": row["conclusion-FOL"],
                        "label": row["label"],
                    }
                    # Thêm trường 'facts' nếu nó tồn tại
                    if "facts" in row:
                        data_entry["facts"] = row["facts"]
                    # Thêm entry vào data
                    data.append(data_entry)

                    if self.max_size and len(data) >= self.max_size:
                        break
                if self.max_size and len(data) >= self.max_size:
                    break
            else:
                raise ValueError(f"Unsupported file type: {file_name}")
        return data

    def build_initial_prompt(self, data):
        prompt = f"""
                This is a mission related to First Order Logic.
                Please create facts for the FOL below.

                Note: Facts should be in a dictionary format like {{"Predicate": {{"variable": "value"}}}} (where value can be "TRUE", "FALSE", or "UNKNOWN"). If the facts for a predicate have more than two arguments, they must be in the form {{"Predicate": {{"(variable1, variable2)": "value"}}}}.

                Variables in statements with quantifiers should not be added to the facts. For example, in "∀x (Rabbit(x) → Cute(x))", x does not need to be listed in the facts.

                Add to the facts only when there is specific information available.
                
                                --- Start of Example ---
                # NL:
                "premises": [
                    "A Japanese game company created the game the Legend of Zelda.",
                    "All games in the Top 10 list are made by Japanese game companies.",
                    "[BG] If a game sells more than one million copies, then it will be selected into the Top 10 list.",
                    "The Legend of Zelda sold more than one million copies.",
                ],
                
                "premises-FOL": [
                    "∃x (Japanese(x) ∧ VideoGameCompany(x) ∧ Game(thelegendofzelda) ∧ Created(x, thelegendofzelda))",
                    "∀x ∀y (Game(x) ∧ InTop10(x) ∧ Created(x, y) → Japanese(y))",
                    "∀x (Game(x) ∧ SellsMoreThan(x, onemillioncopies) → Top10(x))",
                    "SellsMoreThan(thelegendofzelda, onemillioncopies)"
                ],

                # Facts translation:
                {{
                    'facts' = {{
                        "Japanese": {{}},  # No information on specific Japanese companies
                        "VideoGameCompany": {{}},  # No information about specific game company
                        "Game": {{("thelegendofzelda"): "TRUE"}},  # The Legend of Zelda is a game
                        "Created": {{("x", "thelegendofzelda"): "TRUE"}}, # From "A Japanese game company that created the game The Legend of Zelda."
                        "InTop10": {{}},  # No specific information about the game in the Top 10
                        "SellsMoreThan": {{("thelegendofzelda", "onemillioncopies"): "TRUE"}}  # The Legend of Zelda sells over a million copies
                    }}
                }}
                --- End of Example ---

                Return only output as JSON format, don't include any explaination.
                
        # NL:
        Context: {data['premises']}

        Question: {data['premises-FOL']}

        # Facts translation:
        """
        return prompt

    def get_data_directory(self):
        return self.data_directory

    def get_data_record(self):
        return self.data
