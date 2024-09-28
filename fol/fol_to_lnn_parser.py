import logging
import re
from typing import List, Dict, Tuple

from fol.formula_converter import FormulaConverter
from fol.logical_connective_replacer import LogicalConnectiveReplacer
from fol.predicate_extractor import PredicateExtractor
from fol.utils_fol import TypePremise
from fol.variable_extractor import VariableExtractor
from reasoning.logger_config import setup_logger

setup_logger()


class FOLtoLNNParser:
    """Class chịu trách nhiệm chính cho việc phân tích biểu thức FOL và chuyển đổi sang LNN."""

    def __init__(self, fol_expressions: List[Tuple[str, str]]):
        self.fol_expressions = fol_expressions
        self.variables_lnn = []
        self.predicates_lnn = []
        self.formulas_lnn = []
        self.predicate_dict_arg = []
        self.variables_list = []

    def parse(self) -> Tuple[List[str], List[Tuple[str, int]], List[Tuple[str, str]]]:
        for fol_expression, fol_expression_type in self.fol_expressions:
            try:
                # Phân tích các biến
                variables_dict, variables_ol = VariableExtractor.extract_variables(
                    fol_expression
                )
                self._add_unique_elements(self.variables_lnn, variables_dict.values())
                self.variables_list = variables_ol
                new_fol_expression = VariableExtractor.replace_variables(
                    fol_expression, variables_dict
                )

                # Phân tích các vị từ
                # predicate_dict: đã được mã hóa thành các key như P1, P2...
                # predicate_ol: Nguyên bản, chưa được mã hóa
                predicate_dict, predicate_ol = PredicateExtractor.extract_predicates(
                    new_fol_expression
                )
                for item in predicate_ol:
                    if item not in self.predicate_dict_arg:
                        self.predicate_dict_arg.append(item)

                self._add_predicates(predicate_dict, fol_expression_type)
                if fol_expression_type == TypePremise.PREDICATE_ONLY:
                    continue

                new_fol_expression = PredicateExtractor.replace_predicates(
                    new_fol_expression, predicate_dict
                )
                lnn_expression = LogicalConnectiveReplacer.replace_connectives(
                    new_fol_expression, list(predicate_dict.keys())
                )
                lnn_expression = LogicalConnectiveReplacer.replace_forall(
                    lnn_expression
                )
                lnn_expression = LogicalConnectiveReplacer.replace_exists(
                    lnn_expression
                )
                lnn_expression = LogicalConnectiveReplacer.replace_xor(
                    lnn_expression, list(predicate_dict.keys())
                )
                lnn_expression = LogicalConnectiveReplacer.replace_negation(
                    lnn_expression
                )
                lnn_expression = LogicalConnectiveReplacer.replace_implies(
                    lnn_expression
                )
                lnn_expression = LogicalConnectiveReplacer.replace_equivalence(
                    lnn_expression
                )

                # Chuyển đổi sang LNN
                formulae_lnn = FormulaConverter.convert_keys_to_value_lnn(
                    lnn_expression, predicate_dict, variables_dict
                )
                self.formulas_lnn.append((formulae_lnn, fol_expression_type))
            except Exception as e:
                logging.error(
                    f"Error while processing FOL expression '{fol_expression}': {e}"
                )

        return self.variables_lnn, self.predicates_lnn, self.formulas_lnn

    def get_predicate_dict_not_arg(self):
        """Loại bỏ dấu ngoặc và nội dung bên trong dấu ngoặc khỏi các vị từ."""
        cleaned_predicates = []
        try:
            for predicate in self.predicate_dict_arg:
                # Loại bỏ nội dung trong dấu ngoặc và dấu ngoặc
                cleaned_predicate = re.sub(r"\([^)]*\)", "", predicate)
                cleaned_predicates.append(cleaned_predicate)
        except Exception as e:
            logging.error(f"Error while cleaning predicates: {e}")
        return cleaned_predicates

    def get_variables(self):
        return self.variables_list

    def _add_unique_elements(self, target_list: List[str], new_elements: List[str]):
        try:
            for element in new_elements:
                if element not in target_list:
                    target_list.append(element)
        except Exception as e:
            logging.error(f"Error while adding unique elements: {e}")

    def _add_predicates(self, predicate_dict: Dict[str, str], fol_expression_type: str):
        try:
            for predicate in predicate_dict.values():
                num_variables, stripped_expression = (
                    PredicateExtractor.count_commas_in_parentheses(predicate)
                )
                new_element = (stripped_expression, num_variables + 1)
                if new_element not in self.predicates_lnn:
                    self.predicates_lnn.append(new_element)
                if fol_expression_type == TypePremise.PREDICATE_ONLY:
                    self.formulas_lnn.append((stripped_expression, fol_expression_type))
        except Exception as e:
            logging.error(f"Error while adding predicates: {e}")
