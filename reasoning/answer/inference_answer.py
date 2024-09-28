import logging
from typing import Dict, List
from fol.utils_fol import UtilsFOL

from reasoning.answer.element_search import ElementSearch

from lnn.graph_node import GraphNode
from reasoning.answer.graph_traversal import GraphTraversal
from reasoning.answer.handle_state import HandleState
from reasoning.answer.utils_aw import UtilsAnswer
from reasoning.logger_config import setup_logger

setup_logger()


class InferenceAnswerEngine:
    def __init__(
        self,
        data_graph: List[GraphNode],
        graph_links: Dict[int, List[int]],
        predicate_list: List[str],
    ):
        # Kiểm tra kiểu dữ liệu của data_graph
        if not isinstance(data_graph, list):
            logging.error("data_graph must be a list of GraphNode.")
        if not all(isinstance(e, GraphNode) for e in data_graph):
            logging.error("All elements in data_graph must be GraphNode.")

        # Kiểm tra kiểu dữ liệu của graph_links
        if not isinstance(graph_links, dict):
            logging.error("graph_links must be a dictionary.")

        self.element_dict = {e.current_node: e for e in data_graph}
        self.graph_links = graph_links
        self.element_search = ElementSearch(data_graph)
        self.predicate_list = predicate_list

    def infer_answer_propositional_logic(self, question, explain):
        results = {}
        utils = UtilsAnswer(self.predicate_list)

        try:
            query = utils.remove_parentheses_and_arguments(question)
        except Exception as e:
            logging.error(
                f"Error removing parentheses and arguments from question: {e}"
            )
            return {"question": question, "result": "Error processing question"}

        root_node = None
        list_states = None

        try:
            for element in self.element_search.elements:
                label = utils.remove_parentheses_and_arguments(element.label)
                if query == label:
                    root_node = element.current_node
                    list_states = element.state
                    break

            if root_node is None:
                element = self.element_search.elements[0]
                root_node = element.current_node
                list_states = element.state
        except Exception as e:
            logging.error(f"Error during element search: {e}")
            return {"question": question, "result": "Error finding relevant elements"}

        if explain:
            # Todo: Implementation for explanation
            results["question"] = question
            results["result"] = "Not supported yet.."
        else:
            try:
                handle_state = HandleState(element.label, self.predicate_list)
                query_tuples = handle_state.map_query_to_label(question)
                state_result = handle_state.get_state_from_question(
                    query_tuples, list_states
                )
                results["question"] = question
                results["result"] = state_result
            except Exception as e:
                logging.error(
                    f"Error processing state result for question '{question}': {e}"
                )
                results["question"] = question
                results["result"] = "Error processing state result"

        return results

    def infer_answer_predicate_only(self, question, explain):
        results = {}

        try:
            question, is_have_negation = UtilsFOL.check_negation(question)
            utils = UtilsAnswer(self.predicate_list)
            query = utils.remove_parentheses_content(question)
        except Exception as e:
            logging.error(f"Error processing question '{question}': {e}")
            results["question"] = question
            results["result"] = "Error processing question"
            return results

        if query not in self.predicate_list:
            results["question"] = question
            results["result"] = "UNKNOWN"
            return results

        list_states = None

        try:
            for element in self.element_search.elements:
                if query == element.label:
                    list_states = element.state
                    break
        except Exception as e:
            logging.error(f"Error during element search for query '{query}': {e}")
            results["question"] = question
            results["result"] = "Error finding relevant elements"
            return results

        if explain:
            # Todo: Implementation for explanation
            results["question"] = question
            results["result"] = "Not supported yet.."
        else:
            try:
                handle_state = HandleState(element.label, self.predicate_list)
                query_tuples = handle_state.get_query_tuples_predicate_only(question)
                state_result = handle_state.get_state_from_question(
                    query_tuples, list_states
                )
                results["question"] = question
                if is_have_negation:
                    results["result"] = UtilsFOL.handle_answer_negation(state_result)
                else:
                    results["result"] = state_result
            except Exception as e:
                logging.error(
                    f"Error processing state result for predicate question '{question}': {e}"
                )
                results["question"] = question
                results["result"] = "Error processing state result"

        return results

    def infer_answer_propositional_implication(self, question, explain):
        results = {}

        try:
            utils = UtilsAnswer(self.predicate_list)
            query = utils.remove_parentheses_and_arguments(question)
        except Exception as e:
            logging.error(f"Error processing question '{question}': {e}")
            results["question"] = question
            results["result"] = "Error processing question"
            return results

        root_node = None
        list_states = None

        try:
            for element in self.element_search.elements:
                label = utils.remove_parentheses_and_arguments(element.label)
                if query == label:
                    root_node = element.current_node
                    list_states = element.state
                    break

            if root_node is None:
                element = self.element_search.elements[0]
                root_node = element.current_node
                list_states = element.state
        except Exception as e:
            logging.error(f"Error during element search for query '{query}': {e}")
            results["question"] = question
            results["result"] = "Error finding relevant elements"
            return results

        if explain:
            # Todo: Implementation for explanation
            results["question"] = question
            results["result"] = "Not supported yet.."
        else:
            try:
                handle_state = HandleState(element.label, self.predicate_list)
                query_tuples = handle_state.map_query_to_label(question)
                state_result = handle_state.get_state_from_question(
                    query_tuples, list_states
                )
                results["question"] = question
                results["result"] = state_result
            except Exception as e:
                logging.error(
                    f"Error processing state result for propositional implication question '{question}': {e}"
                )
                results["question"] = question
                results["result"] = "Error processing state result"

        return results

    def infer_answer_fol(self, question, explain):
        results = {}

        try:
            utils = UtilsAnswer(self.predicate_list)
            query = utils.remove_variables_after_quantifier(question)
            query = utils.remove_parentheses_and_arguments(query)
        except Exception as e:
            logging.error(f"Error processing question '{question}': {e}")
            results["question"] = question
            results["result"] = "Error processing question"
            return results

        root_node = None
        list_states = None

        try:
            for element in self.element_search.elements:
                label = utils.remove_variables_after_quantifier(element.label)
                label = utils.remove_parentheses_and_arguments(label)
                if query == label:
                    root_node = element.current_node
                    list_states = element.state
                    break

            if root_node is None:
                element = self.element_search.elements[0]
                root_node = element.current_node
                list_states = element.state
        except Exception as e:
            logging.error(f"Error during element search for query '{query}': {e}")
            results["question"] = question
            results["result"] = "Error finding relevant elements"
            return results

        if explain:
            # Todo: Implementation for explanation
            results["question"] = question
            results["result"] = "Not supported yet.."
        else:
            results["question"] = question
            results["result"] = list_states

        return results
