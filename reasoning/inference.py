import logging
import re
from fol.utils_fol import TypePremise, TypeQuestion
from lnn import *
from reasoning.logger_config import setup_logger

setup_logger()


class Inference:
    def __init__(self, variables, predicates, premises, facts):
        try:
            # Free variables
            self.variables = variables
            # Predicates
            self.predicates = predicates
            # Formulas
            self.premises = premises
            # Events
            self.facts = facts
            # Initialize model
            self.model = Model()
            # Define free variables
            self.variable_objects = {var: Variable(var) for var in self.variables}
            # Define Predicates
            self.predicate_objects = {
                name: Predicate(name, arity) for name, arity in self.predicates
            }
        except Exception as e:
            logging.error(f"Error initializing Inference class: {e}")
            raise

    def execute(self, print_model=False):
        # Hàm để thay thế biến và predicate trong biểu thức chuỗi
        def add_knowledge(premise, premise_type, predicate_objects, variable_objects):
            try:
                # Thay thế các biến sau để tránh nhầm lẫn với tên predicate
                for var in variable_objects:
                    # Chỉ thay thế các biến độc lập (không phải một phần của tên predicate)
                    premise = re.sub(
                        rf"\b{var}\b", f"variable_objects['{var}']", premise
                    )
                # Thay thế các predicate
                for pred in predicate_objects:
                    # Sử dụng regex để thay thế chính xác các predicate có tham số
                    premise = re.sub(
                        rf"\b{pred}\((.*?)\)",
                        rf"predicate_objects['{pred}'](\1)",
                        premise,
                    )
                # Thêm {} quanh mỗi biểu thức và chuyển vào danh sách
                transformed_premise = eval(premise)
                if (
                    premise_type == TypePremise.FOL
                    or premise_type == TypePremise.PROPOSITIONAL_IMPLICATION
                ):
                    self.model.add_knowledge(transformed_premise, world=World.AXIOM)
                elif premise_type == TypePremise.PROPOSITIONAL_LOGIC:
                    self.model.add_knowledge(transformed_premise)
                elif (
                    premise_type == TypeQuestion.PROPOSITIONAL_LOGIC
                    or premise_type == TypeQuestion.FOL
                    or premise_type == TypeQuestion.PROPOSITIONAL_IMPLICATION
                ):
                    self.model.add_knowledge(transformed_premise)
            except Exception as e:
                logging.error(f"Error adding knowledge: {e}")

        for premise, premise_type in self.premises:
            try:
                # Cụm 1: [1] Predicate-only cluster
                if premise_type == TypePremise.PREDICATE_ONLY:
                    self.model.add_knowledge(self.predicate_objects[premise])
                # Cụm 2: [2] Propositional implication cluster
                # Cụm 3: [3, 4, 5] First-order logic cluster
                # Cụm 4: [6] Propositional logic cluster
                else:
                    add_knowledge(
                        premise,
                        premise_type,
                        self.predicate_objects,
                        self.variable_objects,
                    )
            except Exception as e:
                logging.error(f"Error processing premise '{premise}': {e}")
                continue  # Skip to the next premise on error

        # Dữ liệu cần thêm vào mô hình
        data = {}

        for predicate, variables in self.facts.items():
            try:
                data[self.predicate_objects[predicate]] = {
                    # Chuyển đổi chuỗi '(var1, var2)' thành tuple ('var1', 'var2')
                    (
                        tuple(variable.strip("()").split(", "))
                        if variable.startswith("(") and variable.endswith(")")
                        else variable
                    ): (
                        Fact.TRUE
                        if truth_value.upper() == "TRUE"
                        else (
                            Fact.FALSE
                            if truth_value.upper() == "FALSE"
                            else Fact.UNKNOWN
                        )
                    )
                    for variable, truth_value in variables.items()
                }
            except Exception as e:
                logging.error(
                    f"Error processing facts for predicate '{predicate}': {e}"
                )
                continue  # Skip to the next predicate on error

        # Add data to the model
        try:
            self.model.add_data(data)
        except Exception as e:
            logging.error(f"Error adding data to the model: {e}")

        # Running inference
        try:
            self.model.infer()
            if print_model:
                self.model.print()
            data_graph, graph_links = self.model.get_data_graph()
        except Exception as e:
            logging.error(f"Error during inference: {e}")

        return data_graph, graph_links
