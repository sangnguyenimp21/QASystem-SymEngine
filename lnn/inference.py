from lnn import *

import re


# Thực hiện suy luận và trả về data_graph: Thông tin graph, graph_links: Liên kết giữa các node trong graph
def inference(variables, predicates, formulaes, facts):
    """
    Hàm này thực hiện suy luận dựa trên các biến, vị từ, công thức và sự kiện đầu vào,
    sau đó trả về thông tin đồ thị và liên kết giữa các node trong đồ thị.

    Parameters:
    variables (list): Danh sách các biến tự do trong hệ thống suy luận.
    predicates (list of tuples): Danh sách các vị từ với mỗi vị từ là một tuple chứa tên vị từ và số lượng biến (arity).
    formulaes (list): Danh sách các công thức logic (FOL) cần suy luận đã chuyển sang format lnn.
    facts (dict): Tập hợp sự kiện dưới dạng một từ điển, trong đó key là tên vị từ và value là một từ điển con chứa các biến và giá trị chân lý của chúng.

    Returns:
    tuple:
        - data_graph (list): Thông tin về đồ thị sau khi suy luận.
        - graph_links (list): Danh sách các liên kết giữa các node trong đồ thị.
    """
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
                if truth_value.upper() == "TRUE"
                else Fact.FALSE if truth_value.upper() == "FALSE" else Fact.UNKNOWN
            )
            for variable, truth_value in variables.items()
        }

    # Thêm dữ liệu vào mô hình
    model.add_data(data)

    # Running inference
    model.infer()

    # Lấy dữ liệu của graph. data_graph: Thông tin graph, graph_links: Liên kết giữa các node trong graph
    data_graph, graph_links = model.get_data_graph()
    # print(graph_links)
    # for element in data_graph:
    #     print(
    #         f"Element(label={element.label}, state={element.state}, current_node={element.current_node}, neighbor_node={element.neighbor_node}, type={element.type}, key={element.key})"
    #     )
    return data_graph, graph_links
