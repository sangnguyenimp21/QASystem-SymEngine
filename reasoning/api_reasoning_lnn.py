import logging
from fol.classifiers import PremiseClassifier, QuestionClassifier
from fol.fol_to_lnn_parser import FOLtoLNNParser
from fol.utils_fol import TypeQuestion
from reasoning.answer.inference_answer import InferenceAnswerEngine
from reasoning.inference import Inference
from reasoning.logger_config import setup_logger

setup_logger()


class QuestionHandler:
    def __init__(self, facts, rules):
        self.facts = facts
        self.rules = rules

    def handle(self, question: str, explain: bool, print_model: bool):
        try:
            question_type = QuestionClassifier.classify(question)
            handler = self.get_handler(question_type)
            if handler:
                return handler(question, explain, print_model)
            raise NotImplementedError(f"Question type {question_type} not supported.")
        except Exception as e:
            logging.error(f"Error handling question: {question}. Error: {str(e)}")
            return f"An error occurred while handling the question: {str(e)}"

    def get_handler(self, question_type: TypeQuestion):
        handlers = {
            TypeQuestion.PREDICATE_ONLY: self._handle_predicate_only,
            TypeQuestion.PROPOSITIONAL_LOGIC: self._handle_propositional_logic,
            TypeQuestion.FOL: self._handle_fol,
            TypeQuestion.PROPOSITIONAL_IMPLICATION: self._handle_propositional_implication,
        }
        return handlers.get(question_type)

    def _handle_predicate_only(self, question: str, explain: bool, print_model: bool):
        return self._process_inference(
            TypeQuestion.PREDICATE_ONLY, question, explain, print_model
        )

    def _handle_propositional_logic(
        self, question: str, explain: bool, print_model: bool
    ):
        return self._process_inference(
            TypeQuestion.PROPOSITIONAL_LOGIC, question, explain, print_model
        )

    def _handle_fol(self, question: str, explain: bool, print_model: bool):
        return self._process_inference(TypeQuestion.FOL, question, explain, print_model)

    def _handle_propositional_implication(
        self, question: str, explain: bool, print_model: bool
    ):
        return self._process_inference(
            TypeQuestion.PROPOSITIONAL_IMPLICATION, question, explain, print_model
        )

    def _process_inference(
        self,
        question_type: TypeQuestion,
        question: str,
        explain: bool,
        print_model: bool,
    ):
        try:
            premises = PremiseClassifier.classify_multiple(self.rules)
            if question_type != TypeQuestion.PREDICATE_ONLY:
                premises = premises + ((question, question_type),)
        except Exception as e:
            logging.error(f"Error classifying premises: {str(e)}")
            return f"An error occurred while classifying premises: {str(e)}"

        try:
            parser = FOLtoLNNParser(premises)
            variables_lnn, predicates_lnn, premises_lnn = parser.parse()
        except Exception as e:
            logging.error(f"Error parsing premises: {str(e)}")
            return f"An error occurred while parsing premises: {str(e)}"

        try:
            inference = Inference(
                variables_lnn, predicates_lnn, premises_lnn, self.facts
            )
            data_graph, graph_links = inference.execute(print_model)
        except Exception as e:
            logging.error(f"Error during inference execution: {str(e)}")
            return f"An error occurred during inference execution: {str(e)}"

        try:
            predicate_list = parser.get_predicate_dict_not_arg()
            inference_engine = InferenceAnswerEngine(
                data_graph, graph_links, predicate_list
            )
        except Exception as e:
            logging.error(f"Error initializing InferenceAnswerEngine: {str(e)}")
            return f"An error occurred while initializing the answer engine: {str(e)}"

        try:
            answer_methods = {
                TypeQuestion.PREDICATE_ONLY: inference_engine.infer_answer_predicate_only,
                TypeQuestion.PROPOSITIONAL_LOGIC: inference_engine.infer_answer_propositional_logic,
                TypeQuestion.FOL: inference_engine.infer_answer_fol,
                TypeQuestion.PROPOSITIONAL_IMPLICATION: inference_engine.infer_answer_propositional_implication,
            }
            return answer_methods[question_type](question, explain)
        except Exception as e:
            logging.error(f"Error inferring answer: {str(e)}")
            return f"An error occurred while inferring the answer: {str(e)}"


def lnn_infer_from_facts_rules(facts, rules, question: str, explain=False):
    print_model = True
    handler = QuestionHandler(facts, rules)
    return handler.handle(question, explain, print_model)
