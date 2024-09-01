# Note:
# + Phải có dấu ',' phía sau các biến, Ví dụ: ∀x,(...
# + Chỉ sử dụng dấu ngoặc tròn trong FOL
# + Nếu như có 2 lượng từ ∀ trở lên thì gộp thành 1 ∀, ví dụ: ∀x,hk

import json
import os

class FOLDataLoader:
    def __init__(self, data_source: str = "file",
                 json_file_path: str = "fol/fol_expressions_input.json", request_data = None):
        self.json_file_path = json_file_path
        self.data_source = data_source

        if self.data_source == "file" and os.path.exists(self.json_file_path):
            self.load_data()

        if self.data_source == "api_request" and request_data is not None:
            self.load_request_data(request_data)

    def load_data(self):
        # Đọc dữ liệu từ tệp JSON
        with open(self.json_file_path, "r") as file:
            data = json.load(file)

        self.fol_expressions = data["expression"]
        self.facts = data["facts"]
        self.question = data["question"]

    def load_request_data(self, request_data):
        self.fol_expressions = request_data["expression"]
        self.facts = request_data["facts"]
        self.question = request_data["question"]

    def get_fol_expressions(self):
        return self.fol_expressions

    def get_facts(self):
        def process_item(item):
            if isinstance(item, dict):
                return {
                    tuple(k.split("-")) if "-" in k else k: process_item(v)
                    for k, v in item.items()
                }
            return item

        return {key: process_item(value) for key, value in self.facts.items()}

    def get_question(self):
        return self.question
