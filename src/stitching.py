import os
import textwrap
from inference import model_prompting


def stitch_z3_code(code, error_msg):
    if "NameError" in error_msg:
        code = "from z3 import Solver, Real, And, Or, Not, sat, unsat\n" + code
    
    return code

def parse_python_code(response):
    code = response.split("```python")[-1].split("```")[0]
    return code
    
def llm_fix_z3(code, error_msg, model):
    print(code, error_msg)
    prompt = textwrap.dedent(f"""
    You are an expert of python coding.
    The following python code has some errors, you should fix it. Put the fixed code between ```python and ```.
    
    Problemetic python code:
    {code}
    
    Error message:
    {error_msg}
    
    Your response:
    """)
    response = model_prompting(model, prompt)
    code = parse_python_code(response)
    return code
