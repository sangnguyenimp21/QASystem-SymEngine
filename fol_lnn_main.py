import re


# Tách các vị từ và trả về dictionary
def extract_predicates(fol):
    fol = fol.replace(" ", "")
    # Sử dụng regex để tìm tất cả các vị từ bao gồm cả biến bên trong ngoặc
    predicates = re.findall(r"[A-Za-z_]+\([^()]*\)", fol)

    # Loại bỏ các phần tử trùng lặp
    unique_predicates = list(set(predicates))

    # Tạo dictionary với key là P1, P2,... và value là các vị từ
    predicate_dict = {
        f"P{i+1}": predicate for i, predicate in enumerate(unique_predicates)
    }

    return predicate_dict


# Thay thế các vị từ dựa trên dictionary, mục đích cho đơn giản biểu thức FOL
def replace_predicates(fol, predicate_dict):
    fol = fol.replace(" ", "")
    for key, predicate in predicate_dict.items():
        # Sử dụng re.escape để thoát các ký tự đặc biệt trong predicate
        escaped_predicate = re.escape(predicate)
        # Thay thế toàn bộ vị từ bằng key
        fol = re.sub(escaped_predicate, key, fol)
    return fol


# Tạo từ điển cho các variables
def extract_variables(fol):
    fol = fol.replace(" ", "")
    # Tìm tất cả các nội dung trong dấu ngoặc tròn
    expressions = re.findall(r"\((.*?)\)", fol)

    # Danh sách lưu biến
    variables = set()

    # Xử lý từng đối số
    for expr in expressions:
        # Tách từng phần nếu có dấu phẩy
        parts = expr.split(",")
        for part in parts:
            part = part.strip()
            # Nếu phần là một ký tự đơn (biến)
            if len(part) == 1 and part.isalpha():
                variables.add(part)

    # Chuyển set thành list và sắp xếp
    variables_list = sorted(list(variables))

    # Tạo từ điển với key là V1, V2,... và value là các biến
    variables_dict = {f"V{i+1}": var for i, var in enumerate(variables_list)}

    return variables_dict


def check_and_or_not_before(expression):
    # Sử dụng biểu thức chính quy để tìm phần trước dấu ∨
    match = re.search(r"\b(And\([^)]*\)|Not\([^)]*\)|Or\([^)]*\))\s*∨", expression)
    if match:
        return match.group(1)
    return False


def get_left_side(expression, predicate_list, connectives):
    """
    Tìm và trả về phần bên trái của dấu ∧ trong biểu thức.
    """
    expression = expression.replace(" ", "")
    # Tìm vị trí của dấu ∧ đầu tiên
    and_index = expression.find(connectives)

    if and_index != -1:
        # Tìm phần bên trái của dấu ∧
        left_side = expression[:and_index].strip()

        if left_side[-1] == ")":
            check_before = check_and_or_not_before(expression)
            if check_before != False:
                return check_before

        """
        Tìm và trả về biến hợp lệ gần nhất với dấu ∧ trong phần bên trái.
        """  # Biểu thức chính quy để tìm các phần có định dạng như P1, P2, ...
        pattern = (
            r"\bP\d+\b"  # Tìm tất cả các vị từ có định dạng hợp lệ trong phần bên trái
        )
        matches = list(re.finditer(pattern, left_side))

        # Nếu không tìm thấy vị từ hợp lệ, trả về kết quả không hợp lệ
        if not matches:
            return "Không tìm thấy vị từ hợp lệ."  # Tìm vị từ gần nhất với dấu ∧
        closest_predicate = None
        min_distance = float("inf")

        left_side = left_side + connectives
        and_index = left_side.find(connectives)

        for match in matches:
            predicate = match.group(0)
            start_index = match.start()
            distance = abs(and_index - start_index)

            if predicate in predicate_list and distance < min_distance:
                min_distance = distance
                closest_predicate = predicate

        return (
            closest_predicate if closest_predicate else "Không tìm thấy vị từ hợp lệ."
        )
    else:
        # Nếu không tìm thấy dấu ∧, toàn bộ biểu thức là phần bên trái
        return expression


def find_and_indices(expression, connective):
    and_indices = []
    if connective == "∧":
        # Lặp qua chuỗi để tìm kiếm ký tự '∧' và ghi lại chỉ số của nó
        num = 0
        for i, char in enumerate(expression):
            if num == 1:
                break
            if char == "∧":
                and_indices.append(i)
                num = 1
            if len(and_indices) >= 1:
                # Biến theo dõi mức độ ngoặc đơn
                parentheses_level = 0  # Biến kiểm tra nếu đã gặp ký tự '→'
                found_implication = False  # Lặp qua chuỗi để tìm kiếm ký tự '∧'
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
                    elif char == "→":
                        found_implication = True
                    elif (
                        char == "∧"
                        and parentheses_level == 0
                        and not found_implication
                        and valid
                    ):
                        and_indices.append(j)
    if connective == "∨":
        # Lặp qua chuỗi để tìm kiếm ký tự '∧' và ghi lại chỉ số của nó
        num = 0
        for i, char in enumerate(expression):
            if num == 1:
                break
            if char == "∨":
                and_indices.append(i)
                num = 1
            if len(and_indices) >= 1:
                # Biến theo dõi mức độ ngoặc đơn
                parentheses_level = 0  # Biến kiểm tra nếu đã gặp ký tự '→'
                found_implication = False  # Lặp qua chuỗi để tìm kiếm ký tự '∧'
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
                    elif char == "→":
                        found_implication = True
                    elif (
                        char == "∨"
                        and parentheses_level == 0
                        and not found_implication
                        and valid
                    ):
                        and_indices.append(j)
    return and_indices


def get_right_side(expression, predicate_list, connective):
    """
    Tìm vị từ hợp lệ gần nhất với dấu ∧ ở bên phải trong biểu thức.

    Args:
        expression: Biểu thức logic.
        predicate_list: Danh sách các vị từ hợp lệ.

    Returns:
        Vị từ hợp lệ gần nhất, hoặc thông báo lỗi nếu không tìm thấy.
    """
    expression = expression.replace(" ", "")
    # list bao gồm các phần tử của and
    list_and = []
    and_indices = []
    # Lặp qua chuỗi để tìm kiếm ký tự '∧' và ghi lại chỉ số của nó
    and_indices = find_and_indices(expression, connective)

    for i in and_indices:
        first_and_index = i
        # Tìm vị trí của dấu ∧ đầu tiên
        # first_and_index = expression.find(connectives)
        # if first_and_index == -1:
        #     return "Không tìm thấy dấu ∧ trong biểu thức."

        # Lấy phần bên phải sau dấu ∧
        right_part = expression[first_and_index + 1 :].strip()

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


def And(left, right):
    """
    Trả về biểu thức dạng And(left, right).
    """
    return f"And({left},{right})"


# Chuyển đổi ∧ , ∨ của FOL thành biểu thức And() Or() của LNN
def replace_expression(original_expression, predicate_list):
    """
    Thay thế phần bên trái và bên phải của dấu ∧ trong biểu thức gốc.
    """
    while "∧" in original_expression:
        connectives = "∧"
        original_expression = original_expression.replace(" ", "")
        # Tìm phần cần thay thế (phần bên trái và bên phải của dấu ∧) trong biểu thức gốc
        left_side = get_left_side(original_expression, predicate_list, connectives)
        right_side = get_right_side(original_expression, predicate_list, connectives)

        left_side_list = []
        left_side_list.append(left_side)
        combined_side = left_side_list + right_side
        and_format_lnn = f"And({','.join(combined_side)})"
        and_format_fol = f"{'∧'.join(combined_side)}"
        # Tìm chuỗi cũ và thay thế bằng chuỗi And mới
        new_expression = original_expression.replace(and_format_fol, and_format_lnn)
        original_expression = new_expression

    while "∨" in original_expression:
        connectives = "∨"
        original_expression = original_expression.replace(" ", "")
        # Tìm phần cần thay thế (phần bên trái và bên phải của dấu ∧) trong biểu thức gốc
        left_side = get_left_side(original_expression, predicate_list, connectives)
        right_side = get_right_side(original_expression, predicate_list, connectives)

        left_side_list = []
        left_side_list.append(left_side)
        combined_side = left_side_list + right_side
        and_format_lnn = f"Or({','.join(combined_side)})"
        and_format_fol = f"{'∨'.join(combined_side)}"
        # Tìm chuỗi cũ và thay thế bằng chuỗi And mới
        new_expression = original_expression.replace(and_format_fol, and_format_lnn)
        original_expression = new_expression

    return original_expression


# Thay thế các key của từ điển vào FOL, mục đích cho đơn giản biểu thức FOL
def replace_variables(fol, variables_dict):
    fol = fol.replace(" ", "")

    # Sử dụng hàm re.sub để thay thế các biến trong fol_expression bằng các key trong variables_dict
    def replace_match(match):
        return {v: k for k, v in variables_dict.items()}[match.group(0)]

    # Tạo pattern để bắt các biến (các chữ cái đơn lẻ)
    pattern = re.compile(r"\b" + r"\b|\b".join(variables_dict.values()) + r"\b")

    # Thay thế các biến bằng key tương ứng
    return pattern.sub(replace_match, fol)


# Thay thế ∀ của FOL thành Forall() của LNN
def replace_forall(expression):
    # Tìm vị trí của dấu ∀
    if expression.startswith("∀"):
        # Thay thế ∀ bằng 'Forall' và bao toàn bộ mệnh đề trong dấu ngoặc đơn
        expression = expression.replace("∀", "Forall(", 1)
        # Thêm dấu ngoặc đơn cuối cùng
        expression += ")"
    return expression


# Thay thế ∃ của FOL thành Exist() của LNN
def replace_exists(expression):
    # Tìm vị trí của dấu ∀
    if expression.startswith("∃"):
        # Thay thế ∀ bằng 'Forall' và bao toàn bộ mệnh đề trong dấu ngoặc đơn
        expression = expression.replace("∃", "Exists(", 1)
        # Thêm dấu ngoặc đơn cuối cùng
        expression += ")"
    return expression


# Thay thế ¬ của FOL thành Not() của LNN
def replace_negation(expression):
    # Sử dụng biểu thức chính quy để tìm và thay thế ¬P6 bằng Not(P6)
    # Tìm và thay thế ¬ theo sau bởi một hoặc nhiều chữ cái và số
    modified_expression = re.sub(r"¬(\w+)", r"Not(\1)", expression)
    return modified_expression


def extract_substring_left_of_arrow(expression):
    arrow_index = expression.find("→")
    if arrow_index == -1:
        return None  # Không tìm thấy ký tự →

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
        # Trả về chuỗi từ dấu ngoặc mở đầu tiên đến ký tự →
        return expression[first_open_index:arrow_index]
    else:
        return None


def extract_substring_after_arrow(expression):
    arrow_index = expression.find("→")
    if arrow_index == -1:
        return None  # Không tìm thấy ký tự →

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
        # Trả về chuỗi từ ký tự → cho đến dấu ngoặc đóng đầu tiên
        return expression[arrow_index + 1 : first_unpaired_close_index + 1]
    else:
        return None


# Thay thế → của FOL thành implies của LNN
def replace_implies(expression):
    before = extract_substring_left_of_arrow(expression)
    after = extract_substring_after_arrow(expression)
    format_fol = before + "→" + after
    format_lnn = f"Implies{before},{after}"
    # Tìm chuỗi cũ và thay thế bằng chuỗi And mới
    return expression.replace(format_fol, format_lnn)


# Thay thế predicates trước
def convert_key_predicates(expression, predicates_dict):
    # Hàm để thay thế khóa predicates bằng giá trị từ từ điển
    def replace_predicate_match(match):
        key = match.group(0)
        return predicates_dict.get(key, key)  # Thay thế theo từ điển predicate

    # Tạo biểu thức chính quy cho các khóa predicate
    predicate_keys = set(predicates_dict.keys())
    predicate_pattern = re.compile(
        r"\b(?:" + "|".join(re.escape(k) for k in predicate_keys) + r")\b"
    )

    # Thay thế các khóa predicate trong biểu thức
    intermediate_expression = predicate_pattern.sub(replace_predicate_match, expression)

    return intermediate_expression


# Thay thế variables
def convert_key_variables(expression, variables_dict):
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


# Trả về LNN hoàn chỉnh bằng cách thay key bằng value
def convert_keys_to_value_lnn(expression, predicates_dict, variables_dict):
    # Thay thế predicates trước
    expression_with_predicates = convert_key_predicates(expression, predicates_dict)
    # Sau đó thay thế variables
    final_expression = convert_key_variables(expression_with_predicates, variables_dict)

    return final_expression


def main():
    # Biểu thức FOL
    fol_expression = "∀x,(HocPhan(x) ∧ ThuocMucBa(x) ∧ ¬DaMien(x)  → XetMien(x))"

    # Tạo từ điển cho các variables
    variables_dict = extract_variables(fol_expression)

    # Thay thế các key của từ điển vào FOL, mục đích cho đơn giản biểu thức FOL
    new_fol_expression = replace_variables(fol_expression, variables_dict)

    # Tách các vị từ và trả về dictionary
    predicate_dict = extract_predicates(new_fol_expression)

    # Thay thế các vị từ dựa trên dictionary, mục đích cho đơn giản biểu thức FOL
    new_fol_expression = replace_predicates(new_fol_expression, predicate_dict)

    # Chuyển dictionary thành một list
    predicate_list = list(predicate_dict.keys())

    # Chuyển đổi ∧ , ∨ của FOL thành biểu thức And() Or() của LNN
    lnn_expression = replace_expression(new_fol_expression, predicate_list)

    # Thay thế ∀ của FOL thành Forall() của LNN
    lnn_expression = replace_forall(lnn_expression)

    # Thay thế ∃ của FOL thành Exist() của LNN
    lnn_expression = replace_exists(lnn_expression)

    # Thay thế ¬ của FOL thành Not() của LNN
    format_lnn = replace_negation(lnn_expression)

    # Thay thế → của FOL thành implies của LNN
    format_lnn = replace_implies(format_lnn)

    # Trả về LNN hoàn chỉnh bằng cách thay key bằng value
    formulae_lnn = convert_keys_to_value_lnn(format_lnn, predicate_dict, variables_dict)
    print("FOL to LNN:", formulae_lnn)


if __name__ == "__main__":
    main()
