from fol_lnn import get_input_lnn
from save_load_fol import get_facts, get_question
import lnn
from lnn import *

import matplotlib.pyplot as plt
import re
from concurrent.futures import ThreadPoolExecutor


# Thực hiện suy luận và trả về data_graph: Thông tin graph, graph_links: Liên kết giữa các node trong graph
def inference(variables, predicates, formulaes, facts):
    # Initialize the model
    model = Model()

    # Định nghĩa các Predicate
    predicate_objects = {name: Predicate(name, arity) for name, arity in predicates}

    # Định nghĩa biến tự do
    variable_objects = {var: Variable(var) for var in variables}

    # Hàm để thay thế biến và predicate trong biểu thức chuỗi
    def replace_predicates_and_variables(
        formulaes, predicate_objects, variable_objects
    ):
        updated_formulae = []

        for formula in formulaes:
            # Thay thế các biến sau để tránh nhầm lẫn với tên predicate
            for var in variable_objects:
                # Chỉ thay thế các biến độc lập (không phải một phần của tên predicate)
                formula = re.sub(rf"\b{var}\b", f"variable_objects['{var}']", formula)

                # Thay thế các predicate trước
            for pred in predicate_objects:
                # Sử dụng regex để thay thế chính xác các predicate có tham số
                formula = re.sub(
                    rf"\b{pred}\((.*?)\)", rf"predicate_objects['{pred}'](\1)", formula
                )

            # Thêm {} quanh mỗi biểu thức và chuyển vào danh sách
            updated_formulae.append(eval(formula))

        return updated_formulae

    # Thực hiện thay thế trên danh sách formulae
    transformed_formulae = replace_predicates_and_variables(
        formulaes, predicate_objects, variable_objects
    )

    # Add formulae to the model
    model.add_knowledge(*transformed_formulae, world=World.AXIOM)

    # Dữ liệu cần thêm vào mô hình
    data = {}
    for predicate, variables in facts.items():
        data[predicate_objects[predicate]] = {
            variable: (
                Fact.TRUE
                if truth_value == "True" or truth_value == "TRUE"
                else Fact.FALSE
            )
            for variable, truth_value in variables.items()
        }

    # Thêm dữ liệu vào mô hình
    model.add_data(data)

    # Running inference
    model.infer()

    model.print()

    # Lấy dữ liệu của graph. data_graph: Thông tin graph, graph_links: Liên kết giữa các node trong graph
    data_graph, graph_links = model.get_data_graph()
    # print(graph_links)
    # for element in data_graph:
    #     print(
    #         f"Element(label={element.label}, state={element.state}, current_node={element.current_node}, neighbor_node={element.neighbor_node}, type={element.type}, key={element.key})"
    #     )
    return data_graph, graph_links


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
def dfs(graph, element_dict, node, visited=None):
    if visited is None:
        visited = set()

    # Đánh dấu đỉnh hiện tại là đã thăm
    visited.add(node)

    # Tìm đối tượng Element cho node hiện tại
    current_element = element_dict.get(node)
    if current_element:
        print(
            f"{current_element.type}: {current_element.label}, State: {current_element.state}",
            end=" ",
        )
        print("\n")

    # Duyệt qua các đỉnh kề của đỉnh hiện tại
    for neighbor in graph.get(node, []):
        if neighbor not in visited:
            dfs(graph, element_dict, neighbor, visited)
