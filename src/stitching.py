import ast
import os
import re
import textwrap
from inference import model_prompting


def parse_name_from_error(error_message):
    matches = re.findall(r"name '(\w+)' is not defined", error_messages)
    return matches

def stitch_z3_code(code, error_msg):
    tree = ast.parse(code)
    
    import_statement = ast.ImportFrom(
        module='z3',
        names=[
            ast.alias(name='Solver', asname=None),
            ast.alias(name='Real', asname=None),
            ast.alias(name='And', asname=None),
            ast.alias(name='Or', asname=None),
            ast.alias(name='Not', asname=None),
            ast.alias(name='sat', asname=None),
            ast.alias(name='unsat', asname=None)
        ],
        level=0 
    )
    
    if "NameError" in error_msg:
        tree.body.insert(0, import_statement)
        code = ast.unparse(tree)
    return code

def parse_python_code(response):
    code = response.split("```python")[-1].split("```")[0]
    return code
    
def llm_fix_z3(code, error_msg, model, sampling):
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
    response = model_prompting(model, prompt, sampling)
    code = parse_python_code(response)
    return code
