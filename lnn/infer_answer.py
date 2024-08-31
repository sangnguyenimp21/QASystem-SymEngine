from concurrent.futures import ThreadPoolExecutor


# Định nghĩa hàm tìm kiếm song song, dùng để tìm kiếm keys là node gốc dựa trên câu hỏi đưa vào, mục đích để từ node gốc cần tìm kiếm có thể duyệt các công thức liên quan nó để lấy các states.
def find_keys_from_question(elements, input_string, node_link, check, num_workers=4):
    # Hàm tìm kiếm trong một phần của danh sách
    def search_in_elements(elements, input_string, check):
        result = []
        if check == False:
            for element in elements:
                # Tách chuỗi tại ký tự "→"
                parts = element.label.split("→")
                if len(parts) > 1:  # Kiểm tra xem có phần tử phía sau "→" hay không
                    right_part = parts[
                        1
                    ].strip()  # Lấy phần sau dấu "→" và loại bỏ khoảng trắng dư thừa
                    if (
                        input_string in right_part
                    ):  # Kiểm tra chuỗi input_string có trong phần phía sau không
                        result.append(element)
        else:
            for element in elements:
                # Tách chuỗi tại ký tự "→"
                if element.type == "Predicate" and element.label == input_string:
                    result.append(element)
        return result

    # Chia danh sách thành nhiều phần và thực hiện tìm kiếm song song
    # with ThreadPoolExecutor(max_workers=num_workers) as executor:
    #     futures = []
    #     chunk_size = len(elements) // num_workers
    #     for i in range(num_workers):
    #         chunk = elements[i * chunk_size : (i + 1) * chunk_size]
    #         futures.append(
    #             executor.submit(search_in_elements, chunk, input_string, check)
    #         )
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        chunk_size = (
            len(elements) + num_workers - 1
        ) // num_workers  # Cách chia điều chỉnh

        for i in range(num_workers):
            start = i * chunk_size
            end = min((i + 1) * chunk_size, len(elements))
            chunk = elements[start:end]
            futures.append(
                executor.submit(search_in_elements, chunk, input_string, check)
            )

        results = []
        for future in futures:
            results.extend(future.result())

    # Trích xuất các khóa (keys)
    keys = []
    if results:
        for element in results:
            keys.append(element.current_node)

    filtered_nodes = remove_child_nodes(node_link, keys)

    return filtered_nodes


def remove_child_nodes(node_link, nodes):
    nodes_set = set(nodes)  # Convert input list to a set for faster lookup
    result = []

    for node in nodes:
        # Check if the node is a child of any other node in the input array
        if not any(node in node_link[parent] for parent in nodes_set if parent != node):
            result.append(node)

    return result


def filter_keys_with_value_check(data_dict, name):
    """
    Lọc các cặp key-value trong data_dict có chứa name và value khác 'UNKNOWN'.

    :param data_dict: Từ điển chứa các cặp key-value
    :param name: Tên cần tìm kiếm trong keys
    :return: Danh sách các cặp key-value có chứa name và value khác 'UNKNOWN'
    """
    return {
        key: value
        for key, value in data_dict.items()
        # if name in key and value != "UNKNOWN"
        if name in key
    }


def find_result_only_node(data_dict, fact_query, predicate_key):
    """
    Lọc các cặp key-value trong data_dict có chứa name và value khác 'UNKNOWN'.

    :param data_dict: Từ điển chứa các cặp key-value
    :param name: Tên cần tìm kiếm trong keys
    :return: Danh sách các cặp key-value có chứa name và value khác 'UNKNOWN'
    """
    fact_query = fact_query.replace(" ", "")  # Xóa tất cả khoảng trắng trong chuỗi
    parts = fact_query.split("-")
    query = tuple(parts)

    for key, value in data_dict.items():
        if key == f"{query}":
            return f"'{predicate_key} - {fact_query}': '{value}'"


# Dùng để duyệt đồ thị theo chiều sâu, lấy ra thông tin trạng thái cần thiết của biểu thức suy luận
def dfs(
    graph,
    element_dict,
    node,
    fact_query,
    predicate_key,
    reslut_state="",
    visited=None,
    result=None,
):
    if visited is None:
        visited = set()

    if result is None:
        result = []

    if reslut_state == "":
        reslut_state = ""

    # Đánh dấu đỉnh hiện tại là đã thăm
    visited.add(node)

    # Tìm đối tượng Element cho node hiện tại
    current_element = element_dict.get(node)
    if current_element:
        state = None
        if current_element.state != None:
            state = filter_keys_with_value_check(current_element.state, fact_query)
        if (
            current_element.type == "Predicate"
            and current_element.label == predicate_key
        ):
            reslut_state = find_result_only_node(
                current_element.state, fact_query, predicate_key
            )
        # Lưu thông tin của node vào result dưới dạng dictionary
        result.append(
            {
                "type": current_element.type,
                "label": current_element.label,
                "state": state,
            }
        )

    # Duyệt qua các đỉnh kề của đỉnh hiện tại
    for neighbor in graph.get(node, []):
        if neighbor not in visited:
            result, reslut_state = dfs(
                graph,
                element_dict,
                neighbor,
                fact_query,
                predicate_key,
                reslut_state,
                visited,
                result,
            )

    return result, reslut_state


def infer_answer_include_explanation(data_graph, graph_links, questions):
    """
    Thực hiện suy luận dựa trên các câu hỏi và dữ liệu đồ thị, sau đó trả về kết quả suy luận.

    Parameters:
    data_graph (list): Danh sách các đối tượng Element trong đồ thị.
    graph_links (dict): Liên kết giữa các node trong đồ thị.
    questions (list): Danh sách các câu hỏi cần suy luận.

    Returns:
    dict: Kết quả suy luận dưới dạng từ điển, với khóa là số câu hỏi và giá trị là câu trả lời.
    """
    # Tạo từ điển cho phép truy cập nhanh đối tượng Element theo current_node
    element_dict = {e.current_node: e for e in data_graph}
    results = {}

    if questions:
        index = 0
        for key, value_to_find in questions.items():
            check = False
            root_nodes = find_keys_from_question(data_graph, key, graph_links, check)
            if root_nodes == []:
                check = True
                root_nodes = find_keys_from_question(
                    data_graph, key, graph_links, check
                )
            answers = []
            for root_node in root_nodes:
                # Sử dụng hàm DFS bắt đầu từ đỉnh
                explanation, finalResult = dfs(
                    graph_links, element_dict, root_node, value_to_find, key
                )
                answers.append(
                    (finalResult, explanation)
                )  # Gộp kết quả của dfs vào danh sách answers
            # Thêm câu trả lời vào từ điển với khóa là số câu hỏi
            results[f"Question {index + 1}"] = (
                answers if answers else "No result found."
            )
            index = index + 1

    return results


def extract_and_transform_value(s):
    # Tách chuỗi dựa trên dấu :
    parts = s.split(":")
    if len(parts) > 1:
        key = parts[0].strip()  # Phần key trước dấu :
        value = parts[1].strip().strip("'")  # Giá trị sau dấu :

        # Chuyển đổi giá trị theo yêu cầu
        if value == "TRUE":
            value = "FALSE"
        elif value == "FALSE":
            value = "TRUE"
        # Nếu giá trị là "UNKNOWN", giữ nguyên

        return f"¬{key}: '{value}'"
    return None


def infer_answer_result_only(data_graph, graph_links, questions):
    """
    Thực hiện suy luận dựa trên các câu hỏi và dữ liệu đồ thị, sau đó trả về kết quả suy luận.

    Parameters:
    data_graph (list): Danh sách các đối tượng Element trong đồ thị.
    graph_links (dict): Liên kết giữa các node trong đồ thị.
    questions (list): Danh sách các câu hỏi cần suy luận.

    Returns:
    dict: Kết quả suy luận dưới dạng từ điển, với khóa là số câu hỏi và giá trị là câu trả lời.
    """
    # Tạo từ điển cho phép truy cập nhanh đối tượng Element theo current_node
    element_dict = {e.current_node: e for e in data_graph}
    results = {}

    if questions:
        index = 0
        for key, value_to_find in questions.items():
            var_not = False
            if "¬" in key:
                var_not = True
                key = key.replace("¬", "")  # Xóa dấu ¬ khỏi chuỗi

            root_nodes = find_keys_from_question(data_graph, key, graph_links, True)
            answers = []
            for root_node in root_nodes:
                # Sử dụng hàm DFS bắt đầu từ đỉnh
                explanation, finalResult = dfs(
                    graph_links, element_dict, root_node, value_to_find, key
                )
                if var_not:
                    finalResult = extract_and_transform_value(finalResult)
                answers.append(finalResult)
            # Thêm câu trả lời vào từ điển với khóa là số câu hỏi
            results[f"Question {index + 1}"] = (
                answers if answers else "No result found."
            )
            index = index + 1

    return results


def print_generalized_result(results):
    """
    Hàm in ra kết quả của từng câu hỏi trong cấu trúc `results`.

    :param results: Từ điển chứa các câu hỏi với cặp (finalResult, explanation)
    """
    for question, answer_pairs in results.items():
        print(f"\n{question}:")

        for final_result, explanations in answer_pairs:
            # In mảng kết quả
            print("  Final Results:")
            for result in final_result:
                print(f"    {result}")

            # In mảng giải thích
            print("  Explanations:")
            for explanation in explanations:
                print(f"    - Type: {explanation['type']}")
                print(f"      Label: {explanation['label']}")

                if explanation["state"] is not None:
                    print("      State:")
                    for state_key, state_value in explanation["state"].items():
                        print(f"        {state_key}: {state_value}")
