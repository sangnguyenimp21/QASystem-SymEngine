import re

def extract_predicates(fol):
    fol = fol.replace(" ", "")
    predicates = re.findall(r"[A-Za-z_][A-Za-z_0-9]*\([^()]*\)", fol)

    unique_predicates = list(set(predicates))

    predicate_dict = {
        f"P{i+1}": predicate for i, predicate in enumerate(unique_predicates)
    }

    return predicate_dict

def get_predicate_dict(premises: str):
    predicate_values = list()

    premises = premises.split("\n")

    for premise in premises:
        if premise:
            predicates = extract_predicates(premise)
            for key, value in predicates.items():
                value = value[:value.index("(")]
                if value not in predicate_values:
                    predicate_values.append(value)

    return predicate_values