import logging
import re
from typing import List, Dict, Tuple

from reasoning.logger_config import setup_logger

setup_logger()


class VariableExtractor:
    """Class chịu trách nhiệm phân tích và xử lý các biến trong biểu thức FOL."""

    @staticmethod
    def extract_variables(fol_expression: str) -> Dict[str, str]:
        # Tách và phân tích các biến từ FOL.
        """
        Hàm này trích xuất tất cả các biến bên trong dấu ngoặc tròn của mỗi vị từ trong biểu thức FOL,
        đồng thời loại bỏ các biến trùng lặp khi lưu vào từ điển.

        Parameters:
        expression (str): Chuỗi chứa biểu thức cần kiểm tra.

        Returns:
        dict: Từ điển với các khóa V1, V2, V3,... và các giá trị là các biến tương ứng không trùng lặp.
        """
        try:
            # Biểu thức chính quy để tìm tất cả các phần bên trong ngoặc tròn của vị từ
            pattern = r"\w+\((.*?)\)"
            # Tìm tất cả các vị từ trong chuỗi
            matches = re.findall(pattern, fol_expression)
            # Tách các biến bằng dấu phẩy và loại bỏ khoảng trắng thừa
            variables = [var.strip() for match in matches for var in match.split(",")]
            # Loại bỏ các biến trùng lặp
            unique_variables = []
            for var in variables:
                if var not in unique_variables:
                    unique_variables.append(var)
            # Tạo từ điển với key là V1, V2,... và value là các biến không trùng lặp
            variables_dict = {f"V{i+1}": var for i, var in enumerate(unique_variables)}
            return variables_dict, unique_variables
        except Exception as e:
            logging.error(f"Error extracting variables from expression: {e}")
            return {}, []

    @staticmethod
    def replace_variables(fol_expression: str, variables_dict: Dict[str, str]) -> str:
        try:
            # Thay thế các biến trong FOL theo dictionary.
            fol_expression = fol_expression.replace(" ", "")

            # Sử dụng hàm re.sub để thay thế các biến trong fol_expression bằng các key trong variables_dict
            def replace_match(match):
                return {v: k for k, v in variables_dict.items()}[match.group(0)]

            # Tạo pattern để bắt các biến (các chữ cái đơn lẻ)
            pattern = re.compile(r"\b" + r"\b|\b".join(variables_dict.values()) + r"\b")
            # Thay thế các biến bằng key tương ứng
            return pattern.sub(replace_match, fol_expression)
        except Exception as e:
            logging.error(f"Error replacing variables in expression: {e}")
            return fol_expression  # Trả về biểu thức ban đầu nếu có lỗi
