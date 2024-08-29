from concurrent.futures import ThreadPoolExecutor


# Định nghĩa hàm tìm kiếm song song, dùng để tìm kiếm keys là node gốc dựa trên câu hỏi đưa vào, mục đích để từ node gốc cần tìm kiếm có thể duyệt các công thức liên quan nó để lấy các states.
def find_keys_from_question(elements, input_string, num_workers=4):
    # Hàm tìm kiếm trong một phần của danh sách
    def search_in_elements(elements, input_string):
        result = []
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
        return result

    # Chia danh sách thành nhiều phần và thực hiện tìm kiếm song song
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        chunk_size = len(elements) // num_workers
        for i in range(num_workers):
            chunk = elements[i * chunk_size : (i + 1) * chunk_size]
            futures.append(executor.submit(search_in_elements, chunk, input_string))

        results = []
        for future in futures:
            results.extend(future.result())

    # Trích xuất các khóa (keys)
    keys = []
    if results:
        for element in results:
            keys.append(element.current_node)

    return keys


# Dùng để duyệt đồ thị theo chiều sâu, lấy ra thông tin trạng thái cần thiết của biểu thức suy luận
def dfs(graph, element_dict, node, visited=None, result=""):
    if visited is None:
        visited = set()

    # Đánh dấu đỉnh hiện tại là đã thăm
    visited.add(node)

    # Tìm đối tượng Element cho node hiện tại
    current_element = element_dict.get(node)
    if current_element:
        result += f"{current_element.type}: {current_element.label}, State: {current_element.state}\n"

    # Duyệt qua các đỉnh kề của đỉnh hiện tại
    for neighbor in graph.get(node, []):
        if neighbor not in visited:
            result = dfs(graph, element_dict, neighbor, visited, result)

    return result


def infer_answer(data_graph, graph_links, questions):
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
        for idx, query in enumerate(questions):
            key_query = find_keys_from_question(data_graph, query)
            answer = ""
            for key in key_query:
                # Sử dụng hàm DFS bắt đầu từ đỉnh key
                answer += dfs(graph_links, element_dict, key)

            # Thêm câu trả lời vào từ điển với khóa là số câu hỏi
            results[f"Question {idx + 1}"] = answer if answer else "No result found."
    else:
        results["Error"] = "Vui lòng add câu hỏi trong file input."

    return results
