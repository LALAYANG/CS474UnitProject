import os
import json
from inference import prompt_construction, model_prompting
from post_processing import process_response
from utils import read_jsonl, evaluate_z3_code
from stitching import stitch_z3_code, llm_fix_z3

def get_prompt(input_item):
    prompt = prompt_construction(input_item)
    return prompt

def prompt_model(model, prompt):
    response = model_prompting(model, prompt)
    return response

def get_post_result(model, response):
    instantiations, formal_proof, z3_code = process_response(model, response)
    return instantiations, formal_proof, z3_code 

def evaulate_and_fix_z3(tag, code, attemps = 3):
    new_eval_result, new_code = None, None
    initial_eval_result = evaluate_z3_code(tag, code)
    print(f"*** Initial result: {initial_eval_result}")
    
    time = 0
    prev_eval_result = initial_eval_result
    prev_code = code
    final_eval_result = None
    final_code = None
    
    while time < attempts and "Traceback" in prev_eval_result:
        new_eval_result, new_code = offline_fix_z3(initial_eval_result, tag, prev_code)
        if "Traceback" in new_eval_result:
            llm_fix_z3(new_code, new_eval_result)
            
            
    # return initial_eval_result, new_eval_result, new_code

def offline_fix_z3(eval_result, tag, code):
    new_code = stitch_z3_code(code, eval_result)
    new_eval_result = evaluate_z3_code(tag, new_code)
    return new_eval_result, new_code

def main(input_file, output_file):
    jsonl_data = read_jsonl(input_file)
    results = []
    model = "gpt-4o-mini"
    for item in jsonl_data:
        print(f"*** Working on item {item['problem_name']}...")
        prompt = get_prompt(item)
        print(f"*** Prompt:\n{prompt}")
        # response = prompt_model(model, prompt)
        response='```instantiations\nx = 2b\ny = a + 1\nx^2 + y^2 \\geq 2xy\n```\n\n```formal_proof\n1. Consider the inequality \\( x^2 + y^2 \\geq 2xy \\) which holds for all real numbers \\( x \\) and \\( y \\). (Cauchy-Schwarz inequality)\n2. Instantiate \\( x = 2b \\) and \\( y = a + 1 \\).\n3. Substitute these values into the inequality: \\((2b)^2 + (a+1)^2 \\geq 2(2b)(a+1)\\).\n4. Simplify the left-hand side: \\(4b^2 + (a+1)^2\\).\n5. Simplify the right-hand side: \\(4b(a+1)\\).\n6. Thus, we have \\(4b^2 + (a+1)^2 \\geq 4b(a+1)\\).\n7. Therefore, for any real numbers \\( a \\) and \\( b \\), \\( 4b(a+1) \\leq 4b^2 + (a+1)^2 \\) holds. (Generalization)\n```\n\n```python\nfrom z3 import Real, Solver, And\n\na = Real(\'a\')\nb = Real(\'b\')\nsolver = Solver()\n\n# Define the inequality to prove\nlhs = 4*b*(a+1)\nrhs = 4*b**2 + (a+1)**2\n\n# Add the negation of the inequality to the solver\nsolver.add(lhs > rhs)\n\n# Check for counterexamples\nif solver.check() == sat:\n    print("A counterexample exists:", solver.model())\nelse:\n    print("No counterexample exists. The statement 4b(a+1) <= 4b^2 + (a+1)^2 for all real a, b is valid.")\n```'
        print(f"*** Response:\n{response}")
        instantiations, formal_proof, z3_code  = get_post_result(model, response)
        eval_result = evaulate_and_fix_z3(item['dataset'], z3_code)
        
        item["instantiations"], item["formal_proof"], item["z3_code"] = instantiations, formal_proof, z3_code
        item["prompt"], item["response"], item["model"] = prompt, response, model
        
        results.append(item)
        with open(output_file, 'a') as file:
            json.dump(item, file)
            file.write('\n')
        exit(0)
    
if __name__ == "__main__":
    input_file = "/home/yang/CS474UnitProject/filtered.jsonl"
    output_file = "outputs.jsonl"
    main(input_file, output_file)