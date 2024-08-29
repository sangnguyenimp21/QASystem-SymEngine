# Note:
# + Phải có dấu ',' phía sau các biến, Ví dụ: ∀x,(...
# + Chỉ sử dụng dấu ngoặc tròn trong FOL
# + Nếu như có 2 lượng từ ∀ trở lên thì gộp thành 1 ∀, ví dụ: ∀x,hk

import json
import os

class FOLDataLoader:
    def __init__(self, json_file_path: str = "fol/fol_expressions_input.json"):
        self.json_file_path = json_file_path
        self.load_data()

    def load_data(self):
        # Đọc dữ liệu từ tệp JSON
        with open(self.json_file_path, "r") as file:
            data = json.load(file)

        self.fol_expressions = data["expression"]
        self.facts = data["facts"]
        self.question = data["question"]

    def get_fol_expressions(self):
        return self.fol_expressions

    def get_facts(self):
        return self.facts

    def get_question(self):
        return self.question
