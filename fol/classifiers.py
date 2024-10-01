import re
from fol.utils_fol import TypePremise, TypeQuestion


class QuestionClassifier:
    """Lớp phân loại câu hỏi."""

    @staticmethod
    def classify(string: str) -> TypeQuestion:
        """
        Phân loại câu hỏi.

        Args:
            string: Chuỗi cần phân loại.

        Returns:
            Phân cụm câu hỏi tương ứng với TypeQuestion.
        """
        if re.search(r"∃|∀", string):
            return TypeQuestion.FOL
        elif re.search(r"↔|→", string):
            return TypeQuestion.PROPOSITIONAL_IMPLICATION
        elif re.search(r"∨|∧|⊕", string):
            return TypeQuestion.PROPOSITIONAL_LOGIC
        return TypeQuestion.PREDICATE_ONLY


class PremiseClassifier:
    """Lớp phân loại premises."""

    @staticmethod
    def classify(premise: str) -> TypePremise:
        """Phân loại một premise."""
        if re.search(r"∀", premise):
            return TypePremise.FOL_FORALL
        if re.search(r"∃", premise):
            return TypePremise.FOL_EXISTS
        elif re.search(r"↔|→", premise):
            return TypePremise.PROPOSITIONAL_IMPLICATION
        elif re.search(r"∨|∧|⊕", premise):
            return TypePremise.PROPOSITIONAL_LOGIC
        return TypePremise.PREDICATE_ONLY

    @staticmethod
    def classify_multiple(arr_premises: list) -> tuple:
        """
        Phân loại nhiều premises.

        Args:
            arr_premises: Mảng các premises cần phân loại.

        Returns:
            Một tuple chứa các tuple, trong đó mỗi tuple biểu diễn một premise và loại của nó.
        """
        premises_type = []
        for premise in arr_premises:
            question_type = PremiseClassifier.classify(premise)
            premises_type.append((premise, question_type))
        return tuple(premises_type)
