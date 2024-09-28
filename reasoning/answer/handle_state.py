import re


class HandleState:
    def __init__(self, label, predicates):
        self.label = label
        self.predicates = predicates
        self.label_args = self.extract_arguments()

    def extract_arguments(self):
        # Code này chưa xử lý đc 'From(0, 1) ∨ From(0, 2)'
        predicate_args = {}
        for predicate in self.predicates:
            matches = re.findall(rf"{predicate}\((.*?)\)", self.label)
            if matches:
                for match in matches:
                    args = match.split(", ")
                    # Nếu chỉ có một đối số, lưu trực tiếp
                    if len(args) == 1:
                        predicate_args[predicate] = int(args[0])
                    else:
                        # Nếu có nhiều đối số, lưu dưới dạng danh sách
                        predicate_args[predicate] = [int(arg) for arg in args]
        return predicate_args

    def map_query_to_label(self, query):
        # Code này chưa xử lý đc 'From(0, 1) ∨ From(0, 2)'
        position_map = {}
        query = query.replace(" ", "")
        matches = re.findall(r"(\w+)\((.*?)\)", query)

        for match in matches:
            predicate, args = match
            args = args.split(",")

            if predicate in self.label_args:
                label_indices = self.label_args[predicate]
                if isinstance(label_indices, int):
                    position_map[label_indices] = args[0]
                else:
                    for i, index in enumerate(label_indices):
                        position_map[index] = args[i]

        query_tuples = tuple(position_map[i] for i in sorted(position_map.keys()))
        return query_tuples

    def get_query_tuples_predicate_only(self, query):
        # Tìm các vị từ và đối số trong query
        matches = re.findall(r"(\w+)\((.*?)\)", query)

        for match in matches:
            predicate, args = match
            args = args.split(", ")

            # Chỉ xử lý nếu vị từ có trong danh sách predicates
            if predicate in self.predicates:
                if len(args) == 1:
                    # Chỉ có một đối số, trả về dưới dạng tuple
                    return (args[0],)  # Kết quả là ('arg1',)
                else:
                    # Nhiều đối số, trả về dạng tuple
                    return tuple(args)  # Kết quả là ('arg1', 'arg2', ...)

        return ()  # Nếu không tìm thấy gì, trả về tuple rỗng

    @staticmethod
    def get_state_from_question(query_tuple, argument):
        # Xóa khoảng trắng trong key của query_tuple
        key = str(query_tuple).replace(" ", "")
        # Tạo một dictionary mới với các key đã xóa khoảng trắng
        cleaned_argument = {k.replace(" ", ""): v for k, v in argument.items()}
        if key in cleaned_argument:
            return cleaned_argument[key]
        print("Unable to determine state.")
        return "UNKNOWN"
