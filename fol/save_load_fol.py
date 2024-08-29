# Note:
# + Phải có dấu ',' phía sau các biến, Ví dụ: ∀x,(...
# + Chỉ sử dụng dấu ngoặc tròn trong FOL
# + Nếu như có 2 lượng từ ∀ trở lên thì gộp thành 1 ∀, ví dụ: ∀x,hk

import json
import os

# Đường dẫn đến tệp JSON trong cùng thư mục với tệp Python
current_directory = os.path.dirname(__file__)
json_file_path = os.path.join(current_directory, "fol_expressions_input.json")

# Đọc dữ liệu từ tệp JSON
with open(json_file_path, "r") as file:
    data = json.load(file)

fol_expressions = data["expression"]

facts = data["facts"]
question = data["question"]


def get_fol_expressions():
    return fol_expressions


def get_facts():
    return facts


def get_question():
    return question
