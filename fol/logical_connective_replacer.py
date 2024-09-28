import logging
import re
from typing import List
from reasoning.logger_config import setup_logger

setup_logger()


class LogicalConnectiveReplacer:
    """Class chịu trách nhiệm thay thế các phép nối logic trong biểu thức FOL bằng cú pháp LNN."""

    @staticmethod
    def replace_connectives(fol_expression: str, predicate_list: List[str]) -> str:
        # Thay thế các ký hiệu ∧, ∨ thành các phép nối LNN.
        """
        Thay thế phần bên trái và bên phải của dấu ∧ trong biểu thức gốc.
        """
        count_and = 0
        try:
            while "∧" in fol_expression:
                connectives = "∧"
                fol_expression = fol_expression.replace(" ", "")
                # Tìm phần cần thay thế (phần bên trái và bên phải của dấu ∧)
                left_side = LogicalConnectiveReplacer.get_left_side(
                    fol_expression, predicate_list, connectives
                )
                right_side = LogicalConnectiveReplacer.get_right_side(
                    fol_expression, predicate_list, connectives
                )
                # Đảm bảo left_side và right_side là danh sách
                left_side_list = (
                    [left_side] if isinstance(left_side, str) else left_side
                )
                right_side_list = (
                    [right_side] if isinstance(right_side, str) else right_side
                )
                combined_side = left_side_list + right_side_list
                and_format_lnn = f"And({','.join(combined_side)})"
                and_format_fol = f"{'∧'.join(combined_side)}"
                # Tìm chuỗi cũ và thay thế bằng chuỗi And mới
                new_expression = fol_expression.replace(and_format_fol, and_format_lnn)
                fol_expression = new_expression
                count_and = count_and + 1
                if count_and > 50:
                    logging.error("While ∧ lặp hơn 50 lần. Có lỗi xảy ra.")
                    return fol_expression

            count_or = 0
            while "∨" in fol_expression:
                connectives = "∨"
                fol_expression = fol_expression.replace(" ", "")
                # Tìm phần cần thay thế (phần bên trái và bên phải của dấu ∧)
                left_side = LogicalConnectiveReplacer.get_left_side(
                    fol_expression, predicate_list, connectives
                )
                right_side = LogicalConnectiveReplacer.get_right_side(
                    fol_expression, predicate_list, connectives
                )
                # Đảm bảo left_side và right_side là danh sách
                left_side_list = (
                    [left_side] if isinstance(left_side, str) else left_side
                )
                right_side_list = (
                    [right_side] if isinstance(right_side, str) else right_side
                )
                # Xử lý phủ định
                combined_side = left_side_list + right_side
                and_format_lnn = f"Or({','.join(combined_side)})"
                and_format_fol = f"{'∨'.join(combined_side)}"
                # Tìm chuỗi cũ và thay thế bằng chuỗi And mới
                new_expression = fol_expression.replace(and_format_fol, and_format_lnn)
                fol_expression = new_expression
                count_or = count_or + 1
                if count_or > 50:
                    logging.error("While ∨ lặp hơn 50 lần. Có lỗi xảy ra.")
                    return fol_expression
        except Exception as e:
            logging.error(f"Error replacing connectives: {e}")
        return fol_expression

    @staticmethod
    def replace_forall(fol_expression: str) -> str:
        # Thay thế ∀ trong FOL bằng Forall() của LNN.
        try:
            while "∀" in fol_expression:
                # Thay thế ∀ bằng 'Forall' và bao toàn bộ mệnh đề trong dấu ngoặc đơn
                fol_expression = fol_expression.replace("∀", "Forall(", 1)
                # Thêm dấu ngoặc đơn cuối cùng
                fol_expression += ")"
        except Exception as e:
            logging.error(f"Error replacing Forall: {e}")
        return fol_expression

    @staticmethod
    def replace_exists(fol_expression: str) -> str:
        """Thay thế ∃ trong FOL bằng Exists() của LNN."""
        try:
            # Chỉ xử lý nếu có "∃" trong chuỗi
            while "∃" in fol_expression:
                # Thay thế ∃ bằng 'Exists' và bao toàn bộ mệnh đề trong dấu ngoặc đơn
                fol_expression = fol_expression.replace("∃", "Exists(", 1)
                # Thêm dấu ngoặc đơn cuối cùng
                fol_expression += ")"

            return fol_expression
        except Exception as e:
            logging.error(f"Error replacing '∃' in expression: {e}")
            return fol_expression

    @staticmethod
    def replace_negation(fol_expression: str) -> str:
        """Thay thế ¬ trong FOL bằng Not() của LNN."""
        try:
            # Thay thế ¬ trong FOL bằng Not() cho các biểu thức phù hợp
            # Tìm và thay thế ¬ theo sau bởi một hoặc nhiều chữ cái và số
            modified_expression = re.sub(r"¬(\w+)", r"Not(\1)", fol_expression)
            # Khớp với ¬ theo sau là một cụm (có thể trong ngoặc hoặc không)
            modified_expression = re.sub(
                r"¬\(([^)]+)\)", r"Not(\1)", modified_expression
            )
            return modified_expression
        except Exception as e:
            logging.error(f"Error replacing '¬' in expression: {e}")
            return fol_expression

    @staticmethod
    def replace_implies(fol_expression: str) -> str:
        """Thay thế → trong FOL bằng Implies() của LNN."""
        # First-order logic
        # x, y = Variables('x', 'y')
        # A = Predicate('A')
        # B = Predicate('B', arity=2)
        # Implies(A(x), B(x, y)))
        try:
            if "→" in fol_expression:
                format_fol = ""
                format_lnn = ""
                if "Forall" in fol_expression or "Exists" in fol_expression:
                    before = LogicalConnectiveReplacer.extract_substring_left_of_arrow(
                        fol_expression
                    )
                    after = LogicalConnectiveReplacer.extract_substring_after_arrow(
                        fol_expression
                    )
                    format_fol = before + "→" + after
                    format_lnn = f"Implies{before},{after}"
                    return fol_expression.replace(format_fol, format_lnn)
                else:
                    before = LogicalConnectiveReplacer.extract_substring_left_of_arrow_no_quantifier(
                        fol_expression
                    )
                    after = LogicalConnectiveReplacer.extract_substring_after_arrow_no_quantifier(
                        fol_expression
                    )
                    format_fol = before + "→" + after
                    format_lnn = f"Implies({before},{after})"
                    # Tìm chuỗi cũ và thay thế bằng chuỗi And mới
                    return fol_expression.replace(format_fol, format_lnn)
            else:
                return fol_expression
        except Exception as e:
            logging.error(f"Error replacing '→' in expression: {e}")
            return fol_expression

    @staticmethod
    def replace_xor(fol_expression: str, predicate_list: List[str]) -> str:
        """Thay thế ⊕ trong FOL bằng XOr() của LNN."""
        # First-order logic
        # x, y = Variables('x', 'y')
        # A, C = Predicates('A', 'C')
        # B = Predicate('B', arity=2)
        # XOr(A(x), B(x, y), C(y)))
        count_XOr = 0
        try:
            while "⊕" in fol_expression:
                left_side = LogicalConnectiveReplacer.get_left_side(
                    fol_expression, predicate_list, "⊕"
                )
                right_side = LogicalConnectiveReplacer.get_right_side(
                    fol_expression, predicate_list, "⊕"
                )
                # Đảm bảo left_side và right_side là danh sách
                left_side_list = (
                    [left_side] if isinstance(left_side, str) else left_side
                )
                right_side_list = (
                    [right_side] if isinstance(right_side, str) else right_side
                )
                combined_side = left_side_list + right_side_list
                and_format_lnn = f"XOr({','.join(combined_side)})"
                and_format_fol = f"{"⊕".join(combined_side)}"
                # Tìm chuỗi cũ và thay thế bằng chuỗi And mới
                new_expression = fol_expression.replace(and_format_fol, and_format_lnn)
                fol_expression = new_expression
                count_XOr += 1
                if count_XOr > 50:
                    print("While ⊕ lặp hơn 50 lần. Có lỗi xãy ra.")
                    return
            else:
                return fol_expression
        except Exception as e:
            logging.error(f"Error replacing '⊕' in expression: {e}")
            return fol_expression

    @staticmethod
    def replace_equivalence(fol_expression: str) -> str:
        """Thay thế ↔ trong FOL bằng Equivalence() của LNN."""
        try:
            if "↔" in fol_expression:
                before = LogicalConnectiveReplacer.extract_substring_left_of_arrow(
                    fol_expression
                )
                after = LogicalConnectiveReplacer.extract_substring_after_arrow(
                    fol_expression
                )
                format_fol = before + "↔" + after
                # First-order logic
                # x, y = Variables('x', 'y')
                # A = Predicate('A')
                # B = Predicate('B', arity=2)
                # Iff(A(x), B(x, y)))
                format_lnn = f"Iff{before},{after}"
                # Tìm chuỗi cũ và thay thế bằng chuỗi And mới
                return fol_expression.replace(format_fol, format_lnn)
            return fol_expression
        except Exception as e:
            logging.error(
                f"Error replacing equivalence in expression '{fol_expression}': {e}"
            )
            return fol_expression

    @staticmethod
    def get_left_side(
        fol_expression: str, predicate_list: List[str], connectives: str
    ) -> str:
        """
        Tìm và trả về phần bên trái của dấu ∧ trong biểu thức, bao gồm cả phủ định nếu có.
        """
        try:
            fol_expression = fol_expression.replace(" ", "")
            # Tìm vị trí của dấu ∧ đầu tiên
            and_index = fol_expression.find(connectives)

            if and_index != -1:
                # Tìm phần bên trái của dấu ∧
                left_side = fol_expression[:and_index].strip()
                # Kiểm tra nếu phần bên trái kết thúc bằng dấu ngoặc )
                if left_side[-1] == ")":
                    check_before = (
                        LogicalConnectiveReplacer.find_matching_opening_parenthesis(
                            left_side
                        )
                    )
                    if check_before != False:
                        return check_before
                # Biểu thức chính quy để tìm các vị từ hợp lệ, bao gồm cả phủ định
                pattern = (
                    r"\bP\d+\b"  # Tìm các vị từ hợp lệ với hoặc không có phủ định ¬
                )
                matches = list(re.finditer(pattern, left_side))
                # Nếu không tìm thấy vị từ hợp lệ, trả về kết quả không hợp lệ
                if not matches:
                    return "Không tìm thấy vị từ hợp lệ."
                closest_predicate = None
                min_distance = float("inf")
                # Thêm dấu connectives vào cuối chuỗi left_side để tính khoảng cách đúng
                left_side = left_side + connectives
                and_index = left_side.find(connectives)
                for match in matches:
                    predicate = match.group(0)
                    start_index = match.start()
                    distance = abs(and_index - start_index)

                    # So sánh khoảng cách và cập nhật predicate gần nhất
                    if predicate in predicate_list and distance < min_distance:
                        min_distance = distance
                        closest_predicate = predicate
                return (
                    closest_predicate
                    if closest_predicate
                    else "Không tìm thấy vị từ hợp lệ."
                )
            else:
                # Nếu không tìm thấy dấu ∧, toàn bộ biểu thức là phần bên trái
                return fol_expression
        except Exception as e:
            logging.error(
                f"Error in get_left_side with expression '{fol_expression}': {e}"
            )
            return "Có lỗi xảy ra trong quá trình tìm kiếm phần bên trái."

    @staticmethod
    def get_right_side(expression, predicate_list, connective):
        """
        Tìm vị từ hợp lệ gần nhất với dấu ∧ ở bên phải trong biểu thức.

        Args:
            expression: Biểu thức logic.
            predicate_list: Danh sách các vị từ hợp lệ.

        Returns:
            Vị từ hợp lệ gần nhất, hoặc thông báo lỗi nếu không tìm thấy.
        """
        try:
            expression = expression.replace(" ", "")
            # list bao gồm các phần tử của and
            list_and = []
            and_indices = []
            # Lặp qua chuỗi để tìm kiếm ký tự '∧' và ghi lại chỉ số của nó
            and_indices = LogicalConnectiveReplacer.find_and_indices(
                expression, connective
            )

            for i in and_indices:
                first_and_index = i
                # Lấy phần bên phải sau dấu ∧
                right_part = expression[first_and_index + 1 :].strip()
                isNot = False
                if right_part[0] == "¬":
                    isNot = True
                    right_part = right_part.replace("¬", "")

                # Kiểm tra xem phần này có bắt đầu bằng dấu ngoặc không
                if right_part[0] == "(":
                    # Tìm ngoặc đóng cuối cùng, phải là ngoặc đóng phù hợp với ngoặc mở
                    open_parentheses = 0
                    for i, char in enumerate(right_part):
                        if char == "(":
                            open_parentheses += 1
                        elif char == ")":
                            open_parentheses -= 1
                            if open_parentheses == 0:
                                if isNot == True:
                                    list_and.append("¬" + right_part[: i + 1].strip())
                                else:
                                    list_and.append(right_part[: i + 1].strip())
                                break
                else:
                    # Nếu không có dấu ngoặc, tìm vị từ hợp lệ gần nhất
                    pattern = r"\bP\d+\b"
                    matches = list(re.finditer(pattern, right_part))
                    if not matches:
                        return "Không tìm thấy vị từ hợp lệ."
                    # Tìm vị từ gần nhất với đầu chuỗi
                    closest_predicate, min_distance = None, float("inf")
                    for match in matches:
                        predicate = match.group()
                        if predicate in predicate_list and match.start() < min_distance:
                            closest_predicate, min_distance = predicate, match.start()
                    if closest_predicate:
                        pattern = r"\s*(Or|Not|¬)"
                        match = re.match(pattern, right_part)
                        if match:
                            closest_predicate = f"{match.group(1)}{closest_predicate}"
                        list_and.append(closest_predicate)
            return list_and
        except Exception as e:
            logging.error(f"Error in get_left_side with expression '{expression}': {e}")
            return "Có lỗi xảy ra trong quá trình tìm kiếm phần bên trái."

    @staticmethod
    def extract_substring_left_of_arrow(expression):
        """
        Tìm và trả về chuỗi con bên trái của dấu mũi tên (→ hoặc ↔) trong biểu thức.
        """
        try:
            arrow_index = expression.find("→")
            if arrow_index == -1:
                arrow_index = expression.find("↔")
                if arrow_index == -1:
                    return None  # Không tìm thấy ký tự → hoac "↔"

            open_count = 0
            first_open_index = None

            for i in range(arrow_index - 1, -1, -1):
                if expression[i] == ")":
                    open_count += 1
                elif expression[i] == "(":
                    if open_count > 0:
                        open_count -= 1
                    else:
                        first_open_index = i
                        break

            if first_open_index is not None:
                # Trả về chuỗi từ dấu ngoặc mở đầu tiên đến ký tự → hoạc "↔"
                return expression[first_open_index:arrow_index]
            else:
                return None
        except Exception as e:
            logging.error(
                f"Error in extract_substring_left_of_arrow with expression '{expression}': {e}"
            )
            return None

    def extract_substring_left_of_arrow_no_quantifier(expression):
        """
        Tìm và trả về chuỗi con bên trái của dấu mũi tên (→ hoặc ↔) trong biểu thức,
        không bao gồm bất kỳ quantifier nào.
        """
        try:
            # Tìm vị trí của dấu → hoặc ↔
            arrow_index = expression.find("→")
            if arrow_index == -1:
                arrow_index = expression.find("↔")
                if arrow_index == -1:
                    return None  # Không tìm thấy ký tự → hoặc ↔

            # Khởi tạo các biến kiểm soát số lượng dấu ngoặc
            open_count = 0
            first_open_index = None

            # Duyệt ngược chuỗi từ trước vị trí dấu → hoặc ↔
            for i in range(arrow_index - 1, -1, -1):
                if expression[i] == ")":
                    open_count += 1
                elif expression[i] == "(":
                    if open_count > 0:
                        open_count -= 1
                    else:
                        first_open_index = i
                        break

            # Nếu tìm thấy dấu ngoặc mở, trả về chuỗi trong ngoặc
            if first_open_index is not None:
                return expression[first_open_index:arrow_index].strip()

            # Nếu không tìm thấy dấu ngoặc, chỉ trả về chuỗi bên trái của dấu →
            return expression[:arrow_index].strip()
        except Exception as e:
            logging.error(
                f"Error in extract_substring_left_of_arrow_no_quantifier with expression '{expression}': {e}"
            )
            return None

    @staticmethod
    def extract_substring_after_arrow(expression):
        """
        Tìm và trả về chuỗi con bên phải của dấu mũi tên (→ hoặc ↔) trong biểu thức.
        """
        try:
            arrow_index = expression.find("→")
            if arrow_index == -1:
                arrow_index = expression.find("↔")
                if arrow_index == -1:
                    return None  # Không tìm thấy ký tự → hoac "↔"

            open_count = 0
            close_count = 0
            first_unpaired_close_index = None

            for i in range(arrow_index + 1, len(expression)):
                if expression[i] == "(":
                    open_count += 1
                elif expression[i] == ")":
                    close_count += 1

                # Nếu số dấu ngoặc đóng vượt quá số dấu ngoặc mở
                if close_count > open_count:
                    first_unpaired_close_index = i
                    break

            if first_unpaired_close_index is not None:
                # Trả về chuỗi từ ký tự → hoac "↔" cho đến dấu ngoặc đóng đầu tiên
                return expression[arrow_index + 1 : first_unpaired_close_index + 1]
            else:
                return None
        except Exception as e:
            logging.error(
                f"Error in extract_substring_after_arrow with expression '{expression}': {e}"
            )
            return None

    def extract_substring_after_arrow_no_quantifier(expression):
        """
        Tìm và trả về chuỗi con bên phải của dấu mũi tên (→ hoặc ↔) trong biểu thức,
        không bao gồm bất kỳ phần định lượng nào.
        """
        try:
            # Tìm vị trí của dấu → hoặc ↔
            arrow_index = expression.find("→")
            if arrow_index == -1:
                arrow_index = expression.find("↔")
                if arrow_index == -1:
                    return None  # Không tìm thấy ký tự → hoặc ↔

            open_count = 0
            close_count = 0
            first_unpaired_close_index = None

            # Duyệt chuỗi từ sau dấu → hoặc ↔
            for i in range(arrow_index + 1, len(expression)):
                if expression[i] == "(":
                    open_count += 1
                elif expression[i] == ")":
                    close_count += 1

                # Nếu số dấu ngoặc đóng vượt số dấu ngoặc mở
                if close_count > open_count:
                    first_unpaired_close_index = i
                    break

            # Nếu có dấu ngoặc đóng không ghép đôi
            if first_unpaired_close_index is not None:
                return expression[
                    arrow_index + 1 : first_unpaired_close_index + 1
                ].strip()

            # Nếu không có dấu ngoặc, trả về chuỗi từ sau dấu →
            return expression[arrow_index + 1 :].strip()
        except Exception as e:
            logging.error(
                f"Error in extract_substring_after_arrow_no_quantifier with expression '{expression}': {e}"
            )
            return None

    @staticmethod
    def find_and_indices(expression: str, connective: str) -> list:
        and_indices = []
        try:
            if not isinstance(expression, str) or not isinstance(connective, str):
                logging.error(f"Cả 'expression' và 'connective' đều phải là chuỗi.")

            def find_first_connective(connective):
                num = 0
                for i, char in enumerate(expression):
                    if num == 1:
                        break
                    if char == connective:
                        and_indices.append(i)
                        num = 1
                    if len(and_indices) >= 1:
                        parentheses_level = 0
                        found_implication = False
                        check_close = False
                        check_open = False
                        valid = True
                        for j, char in enumerate(expression[i + 1 :], start=i + 1):
                            if char == "(":
                                parentheses_level += 1
                                check_open = True
                            elif char == ")":
                                check_close = True
                                if not check_open and check_close:
                                    valid = False
                                parentheses_level -= 1
                            elif char in ("→", "↔"):
                                found_implication = True
                            elif (
                                char == connective
                                and parentheses_level == 0
                                and not found_implication
                                and valid
                            ):
                                and_indices.append(j)

            # Gọi hàm để tìm kiếm kết nối đầu tiên
            find_first_connective(connective)
        except ValueError as ve:
            logging.error(f"Lỗi giá trị: {ve}")
        except Exception as e:
            logging.error(f"Có lỗi xảy ra: {e}")
        return and_indices

    @staticmethod
    def find_matching_opening_parenthesis(left_side):
        try:
            # Kiểm tra nếu chuỗi kết thúc bằng dấu )
            if not left_side.endswith(")"):
                return None  # Không có dấu ngoặc đóng ở cuối

            # Tìm vị trí của dấu ngoặc đóng cuối
            closing_index = len(left_side) - 1
            opening_index = closing_index - 1
            balance = 1  # Bắt đầu với 1 dấu ngoặc đóng

            # Lặp để tìm dấu ngoặc mở tương ứng
            while opening_index >= 0:
                if left_side[opening_index] == ")":
                    balance += 1
                elif left_side[opening_index] == "(":
                    balance -= 1

                if balance == 0:
                    break

                opening_index -= 1

            if balance != 0:
                return None  # Không tìm thấy dấu ngoặc mở tương ứng

            # Trả về nội dung bao gồm ngoặc và nội dung bên trong
            if left_side[opening_index - 1]:
                if left_side[opening_index - 1] == "¬":
                    return left_side[opening_index - 1 : closing_index + 1]
            return left_side[opening_index : closing_index + 1]
        except ValueError as ve:
            logging.error(f"Lỗi giá trị: {ve}")
        except Exception as e:
            logging.error(f"Có lỗi xảy ra: {e}")
