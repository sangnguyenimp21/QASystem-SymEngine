import logging
import re
from reasoning.logger_config import setup_logger

setup_logger()


class UtilsAnswer:
    def __init__(self, predicates):
        self.predicates = predicates

    def _remove_outer_parentheses(self, expression):
        """Remove outer parentheses of the expression if they surround the whole."""
        try:
            while expression.startswith("(") and expression.endswith(")"):
                # Kiểm tra số lượng ngoặc để đảm bảo chỉ loại bỏ ngoặc ngoài cùng
                opened = 0
                for i, char in enumerate(expression):
                    if char == "(":
                        opened += 1
                    elif char == ")":
                        opened -= 1
                    # Nếu ở giữa có ngoặc đóng tương ứng với ngoặc mở đầu tiên, thì dừng
                    if opened == 0 and i != len(expression) - 1:
                        return expression  # Không loại bỏ ngoặc ngoài
                expression = expression[1:-1].strip()  # Loại bỏ ngoặc ngoài cùng
            return expression
        except Exception as e:
            logging.error(f"Error removing outer parentheses from '{expression}': {e}")
            return expression  # Return the original expression on error

    def remove_parentheses_and_arguments(self, expression):
        """Remove arguments of all predicates and outer parentheses."""
        try:
            # Tạo regex để loại bỏ đối số của tất cả các vị từ
            for predicate in self.predicates:
                expression = re.sub(
                    rf"\b{predicate}\s*\([^)]*\)", predicate, expression
                )
            # Loại bỏ dấu ngoặc ngoài cùng
            expression = self._remove_outer_parentheses(expression)
            expression = expression.replace(" ", "")
            expression = expression.replace("(", "").replace(")", "")
            return expression
        except Exception as e:
            logging.error(
                f"Error removing parentheses and arguments from '{expression}': {e}"
            )
            return expression  # Return the original expression on error

    def remove_variables_after_quantifier(self, expression):
        """Remove characters from the quantifier to the first parenthesis."""
        try:
            # Tìm và xóa ký tự từ lượng từ đến dấu ngoặc đầu tiên
            updated_expression = re.sub(r"([∀∃])[^(\(]*\(", r"\1(", expression)
            return updated_expression
        except Exception as e:
            logging.error(
                f"Error removing variables after quantifier in '{expression}': {e}"
            )
            return expression  # Return the original expression on error

    def remove_parentheses_content(self, expression):
        """Use regex to find and remove all content within parentheses."""
        try:
            new_expression = re.sub(r"\(.*?\)", "", expression)
            return new_expression
        except Exception as e:
            logging.error(
                f"Error removing parentheses content from '{expression}': {e}"
            )
            return expression  # Return the original expression on error
