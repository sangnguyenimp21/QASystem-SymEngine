from enum import Enum


class TypeQuestion(Enum):
    # Phân loại câu hỏi:
    # 1. Chỉ có vị từ
    # 2. Mệnh đề suy diễn ("↔|→") mà không có lượng từ ("∃|∀").
    # 3. Mệnh đề suy diễn ("↔|→") và có chứa lượng từ ("∃|∀").
    # 4. Chỉ có lượng từ ("∃|∀").
    # 5. Lượng từ ("∃|∀") và "∨", "∧", "⊕"
    # 6. "∨", "∧", "⊕"

    # Phân cụm câu hỏi:
    # Cụm 1: [1] Predicate-only cluster
    PREDICATE_ONLY = 1
    # Cụm 2: [2] Propositional implication cluster
    PROPOSITIONAL_IMPLICATION = 2
    # Cụm 3: [3, 4, 5] First-order logic cluster
    FOL = 3
    # Cụm 4: [6] Propositional logic cluster
    PROPOSITIONAL_LOGIC = 4


class TypePremise(Enum):
    # Phân loại câu hỏi:
    # 1. Chỉ có vị từ
    # 2. Mệnh đề suy diễn ("↔|→") mà không có lượng từ ("∃|∀").
    # 3. Mệnh đề suy diễn ("↔|→") và có chứa lượng từ ("∃|∀").
    # 4. Chỉ có lượng từ ("∃|∀").
    # 5. Lượng từ ("∃|∀") và "∨", "∧", "⊕"
    # 6. "∨", "∧", "⊕"

    # Phân cụm câu hỏi:
    # Cụm 1: [1] Predicate-only cluster
    PREDICATE_ONLY = 5
    # Cụm 2: [2] Propositional implication cluster
    PROPOSITIONAL_IMPLICATION = 6
    # Cụm 3: [3, 4, 5] First-order logic cluster
    FOL = 7
    # Cụm 4: [6] Propositional logic cluster
    PROPOSITIONAL_LOGIC = 8


class UtilsFOL:
    def __init__(self):
        pass

    @staticmethod
    def check_negation(expression):
        check = False
        # Kiểm tra xem chuỗi có chứa '¬' không
        if "¬" in expression:
            # Xóa '¬' khỏi chuỗi
            expression = expression.replace("¬", "")
            # Bật biến check lên true
            check = True
        return expression, check

    @staticmethod
    def handle_answer_negation(answer):
        if answer == "TRUE":
            return "FALSE"
        elif answer == "FALSE":
            return "TRUE"
        elif answer == "UNKNOWN":
            return "UNKNOWN"
        else:
            return "Result is indeterminate."
