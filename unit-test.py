from drafts.querydata import query_rag
from langchain_ollama import OllamaLLM


EVAL = """
Expected Response: {expected}
Actual Response: {actual}
---
(Answer with 'true' or 'false') Does the actual response match the expected response? 
"""
##################### UNIT TEST FUNCTION ####################################

def testing():
    assert validate(
        question="Who takes Empty Nest Syndrome more deeply, mothers or fathers?",
        expected="mothers"
    )


################################## VALIDATION FUNCTION #############################
def validate(question, expected):
    reply  = query_rag(question)

    pr = EVAL.format(expected = expected, actual = reply)

    model = OllamaLLM(model='llama3.2:1b')

    evalres = model.invoke(pr)
    evalres_clean = evalres.strip().lower()
    print(pr)

    if "true" in evalres_clean:
        # Print response in Green if it is correct.
        print("\033[92m" + f"Response: {evalres_clean}" + "\033[0m")
        return True
    
    elif "false" in evalres_clean:
        # Print response in Red if it is incorrect.
        print("\033[91m" + f"Response: {evalres_clean}" + "\033[0m")
        return False
    
    else:
        raise ValueError(
            f"Invalid evaluation result. Cannot determine if 'true' or 'false'."
        )

testing()




