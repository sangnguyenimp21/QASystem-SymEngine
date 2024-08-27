# Ví dụ sử dụng hàm
from fol_lnn import get_input_lnn
from inference import dfs, find_keys_from_question, inference
from save_load_fol import get_facts, get_question


def main():

    variables, predicates, formulaes = get_input_lnn()
    facts = get_facts()
    # Kiểm tra xem các mảng có phải là không rỗng
    if not variables:
        print("Error: 'variables' array is empty.")
        return

    if not predicates:
        print("Error: 'predicates' array is empty.")
        return

    if not formulaes:
        print("Error: 'formulaes' array is empty.")
        return

    if not facts:
        print("Error: 'formulaes' array is empty.")
        return

    data_graph, graph_links = inference(variables, predicates, formulaes, facts)
    # Tạo từ điển cho phép truy cập nhanh đối tượng Element theo current_node
    element_dict = {e.current_node: e for e in data_graph}
    queries = get_question()
    if queries:
        for query in queries:
            key_query = find_keys_from_question(data_graph, query)
            print("\n The result of the inference is: \n")
            for key in key_query:
                # Sử dụng hàm DFS bắt đầu từ đỉnh key
                dfs(graph_links, element_dict, key)
    else:
        print("Vui lòng add câu hỏi trong file input.")


if __name__ == "__main__":
    main()
