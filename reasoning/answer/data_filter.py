class DataFilter:
    @staticmethod
    def filter_keys_with_value_check(data_dict, name):
        return {key: value for key, value in data_dict.items() if name in key}

    @staticmethod
    def find_result_only_node(data_dict, fact_query, predicate_key):
        fact_query = fact_query.replace(" ", "")
        query = tuple(fact_query.split("-"))
        return (
            f"'{predicate_key} - {fact_query}': '{data_dict.get(f'{query}')}'"
            if f"{query}" in data_dict
            else None
        )
