import logging
import re
from typing import Dict, Tuple
from reasoning.logger_config import setup_logger

setup_logger()


class PredicateExtractor:
    """Class chịu trách nhiệm phân tích và xử lý các vị từ trong biểu thức FOL."""

    @staticmethod
    def extract_predicates(fol_expression: str) -> Dict[str, str]:
        """
        Tách các vị từ từ FOL và trả về dictionary.

        Parameters:
        fol_expression (str): Chuỗi biểu thức FOL.

        Returns:
        dict: Từ điển với các vị từ duy nhất và các biến bổ sung.
        """
        try:
            # Tách các vị từ từ FOL và trả về dictionary.
            fol_expression = fol_expression.replace(" ", "")
            # Sử dụng regex để tìm tất cả các vị từ bao gồm cả biến bên trong ngoặc
            # predicates = re.findall(r"[A-Za-z_]+\([^()]*\)", fol)
            predicates = re.findall(r"[A-Za-z_][A-Za-z_0-9]*\([^()]*\)", fol_expression)
            # Loại bỏ các phần tử trùng lặp
            unique_predicates = list(set(predicates))
            unique_predicates_include_not = []
            for item in unique_predicates:
                unique_predicates_include_not.append(item)
                unique_predicates_include_not.append(f"¬{item}")
            # Tạo dictionary với key là P1, P2,... và value là các vị từ
            predicate_dict = {
                f"P{i+1}": predicate
                for i, predicate in enumerate(unique_predicates_include_not)
            }
            return predicate_dict, unique_predicates
        except Exception as e:
            logging.error(f"Error extracting predicates from expression: {e}")
            return {}, []  # Trả về từ điển rỗng và danh sách rỗng nếu có lỗi

    @staticmethod
    def count_commas_in_parentheses(predicate: str) -> Tuple[int, str]:
        # Đếm số lượng dấu phẩy bên trong dấu ngoặc và trả về số lượng biến (arity).
        """
        Hàm này đếm số dấu phẩy bên trong ngoặc đơn của một chuỗi.

        Parameters:
        expression (str): Chuỗi chứa biểu thức cần kiểm tra.

        Returns:
        int: Số lượng dấu phẩy bên trong ngoặc đơn.
        """
        try:
            # Tìm phần bên trong ngoặc đơn
            inside_parentheses = predicate[
                predicate.find("(") + 1 : predicate.find(")")
            ]
            # Đếm số dấu phẩy trong phần bên trong ngoặc đơn
            comma_count = inside_parentheses.count(",")
            # Loại bỏ các phần trong ngoặc tròn khỏi chuỗi gốc
            stripped_expression = re.sub(r"\(.*?\)", "", predicate)
            return comma_count, stripped_expression
        except Exception as e:
            logging.error(f"Error counting commas in predicate: {e}")
            return 0, predicate  # Trả về số 0 và chuỗi gốc nếu có lỗi

    @staticmethod
    def replace_predicates(fol_expression: str, predicate_dict: Dict[str, str]) -> str:
        """
        Thay thế các vị từ trong biểu thức FOL theo dictionary.

        Parameters:
        fol_expression (str): Chuỗi chứa biểu thức cần thay thế.
        predicate_dict (dict): Từ điển với các vị từ cần thay thế.

        Returns:
        str: Chuỗi biểu thức đã thay thế các vị từ.
        """
        try:
            # Thay thế các vị từ trong biểu thức FOL theo dictionary.
            fol_expression = fol_expression.replace(" ", "")
            sorted_predicate_dict = dict(
                sorted(predicate_dict.items(), key=lambda item: item[1].startswith("¬"))
            )
            # Thay thế từng predicate trong fol_expression
            for key, predicate in sorted_predicate_dict.items():
                # Chỉ thay thế nếu có chứa ¬
                if "¬" in predicate:
                    fol_expression = re.sub(re.escape(predicate), key, fol_expression)
            # Thay thế các predicate không chứa ¬
            for key, predicate in sorted_predicate_dict.items():
                if "¬" not in predicate:
                    fol_expression = re.sub(re.escape(predicate), key, fol_expression)
            return fol_expression
        except Exception as e:
            logging.error(f"Error replacing predicates in expression: {e}")
            return fol_expression  # Trả về biểu thức ban đầu nếu có lỗi
