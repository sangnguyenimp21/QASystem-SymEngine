from reasoning.answer.data_filter import DataFilter


class GraphTraversal:
    def __init__(self, graph, element_dict):
        self.graph = graph
        self.element_dict = element_dict

    def dfs(
        self,
        node,
        fact_query,
        predicate_key,
        result_state="",
        visited=None,
        result=None,
    ):
        if visited is None:
            visited = set()
        if result is None:
            result = []
        visited.add(node)

        current_element = self.element_dict.get(node)
        if current_element:
            state = (
                DataFilter.filter_keys_with_value_check(
                    current_element.state, fact_query
                )
                if current_element.state
                else None
            )
            if (
                current_element.type == "Predicate"
                and current_element.label == predicate_key
            ):
                result_state = DataFilter.find_result_only_node(
                    current_element.state, fact_query, predicate_key
                )
            result.append(
                {
                    "type": current_element.type,
                    "label": current_element.label,
                    "state": state,
                }
            )

        for neighbor in self.graph.get(node, []):
            if neighbor not in visited:
                result, result_state = self.dfs(
                    neighbor, fact_query, predicate_key, result_state, visited, result
                )

        return result, result_state
