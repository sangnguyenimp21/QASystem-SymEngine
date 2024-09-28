from concurrent.futures import ThreadPoolExecutor


class ElementSearch:
    def __init__(self, elements):
        self.elements = elements

    def find_keys_from_question(self, input_string, node_link, check, num_workers=4):
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            chunk_size = (len(self.elements) + num_workers - 1) // num_workers
            futures = [
                executor.submit(
                    self._search_in_elements,
                    self.elements[
                        i * chunk_size : min((i + 1) * chunk_size, len(self.elements))
                    ],
                    input_string,
                    check,
                )
                for i in range(num_workers)
            ]

            results = []
            for future in futures:
                results.extend(future.result())

        keys = [element.current_node for element in results]
        return self._remove_child_nodes(node_link, keys)

    def _search_in_elements(self, elements, input_string, check):
        result = []
        for element in elements:
            if check is False:
                parts = element.label.split("→")
                if len(parts) > 1 and input_string in parts[1].strip():
                    result.append(element)
            elif element.type == "Predicate" and element.label == input_string:
                result.append(element)
        return result

    def _remove_child_nodes(self, node_link, nodes):
        nodes_set = set(nodes)
        result = [
            node
            for node in nodes
            if not any(
                node in node_link[parent] for parent in nodes_set if parent != node
            )
        ]
        return result
