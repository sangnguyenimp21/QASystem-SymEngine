import logging
import re
from typing import Dict
from reasoning.logger_config import setup_logger

setup_logger()


class FormulaConverter:
    """Class chịu trách nhiệm chuyển đổi các biểu thức FOL thành các công thức của LNN."""

    @staticmethod
    def convert_keys_to_value_lnn(
        lnn_expression: str,
        predicate_dict: Dict[str, str],
        variables_dict: Dict[str, str],
    ) -> str:
        try:
            # Chuyển đổi các key trong biểu thức LNN thành giá trị tương ứng.
            expression_with_predicates = FormulaConverter.convert_key_predicates(
                lnn_expression, predicate_dict
            )
            # Sau đó thay thế variables
            final_expression = FormulaConverter.convert_key_variables(
                expression_with_predicates, variables_dict
            )
            return final_expression
        except Exception as e:
            logging.error(f"Lỗi trong convert_keys_to_value_lnn: {e}")
            return lnn_expression  # Trả về biểu thức ban đầu nếu có lỗi

    @staticmethod
    def convert_key_predicates(expression: str, predicates_dict: Dict[str, str]):
        try:
            predicates_dict_extract = {}
            # Thay thế các giá trị chứa ký tự ¬
            for key, value in predicates_dict.items():
                if "¬" in value:
                    # Lấy phần nội dung sau ký tự ¬
                    inner_expression = value[1:]  # Lấy mọi ký tự sau ký tự ¬
                    # Gán lại giá trị với Not(...)
                    predicates_dict_extract[key] = f"Not({inner_expression})"
                else:
                    predicates_dict_extract[key] = value

            # Hàm để thay thế khóa predicates bằng giá trị từ từ điển
            def replace_predicate_match(match):
                key = match.group(0)
                return predicates_dict_extract.get(
                    key, key
                )  # Thay thế theo từ điển predicate

            # Tạo biểu thức chính quy cho các khóa predicate
            predicate_keys = set(predicates_dict_extract.keys())
            predicate_pattern = re.compile(
                r"\b(?:" + "|".join(re.escape(k) for k in predicate_keys) + r")\b"
            )
            # Thay thế các khóa predicate trong biểu thức
            intermediate_expression = predicate_pattern.sub(
                replace_predicate_match, expression
            )
            return intermediate_expression
        except Exception as e:
            logging.error(f"Error convert_key_predicates: {e}")
            return expression

    @staticmethod
    def convert_key_variables(expression: str, variables_dict: Dict[str, str]):
        try:
            # Hàm để thay thế khóa variables bằng giá trị từ từ điển
            def replace_variable_match(match):
                key = match.group(0)
                return variables_dict.get(key, key)  # Thay thế theo từ điển biến

            # Tạo biểu thức chính quy cho các khóa variable
            variable_keys = set(variables_dict.keys())
            variable_pattern = re.compile(
                r"\b(?:" + "|".join(re.escape(k) for k in variable_keys) + r")\b"
            )
            # Thay thế các khóa variable trong biểu thức
            final_expression = variable_pattern.sub(replace_variable_match, expression)
            return final_expression
        except Exception as e:
            logging.error(f"Lỗi trong convert_key_variables: {e}")
            return expression
