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

def iter_evaulate_fix_z3(item, model, code, attempts = 3):
    new_eval_result, new_code = None, None
    tag = item["dataset"]
    initial_eval_result = evaluate_z3_code(tag, code)
    print(f"*** Initial result: {initial_eval_result}")
    
    time = 0
    prev_eval_result = initial_eval_result
    prev_code = code
    final_eval_result = None
    final_code = None
    offline_stitch_applied = False
    
    while time < attempts and "Traceback" in prev_eval_result:
        new_eval_result, new_code = offline_fix_z3(initial_eval_result, tag, prev_code)
        
        print(f"*** Offline stitched code:\n{new_code}\n*** Offline stitched result: {new_eval_result}")
        
        if new_eval_result != prev_eval_result:
            offline_stitch_applied = True
        
        if "Traceback" in new_eval_result:
            new_code = llm_fix_z3(new_code, new_eval_result, model)
            new_eval_result = evaluate_z3_code(tag, new_code)
            print(f"*** LLM stitched code:\n{new_code}\n*** LLM stitched result: {new_eval_result}")
        else:
            print(f"*** offline stitching fixed {item['problem_name']}")
            # offline_stitch_applied = True
            
        prev_eval_result = new_eval_result
        prev_code = new_code
        time += 1
        
    final_eval_result = prev_eval_result
    final_code = prev_code
    
    results = {
        "initial_eval_result": initial_eval_result,
        "final_code": final_code,
        "final_eval_result": final_eval_result,
        "stitched_times": time,
        "offline_stitch_applied": offline_stitch_applied
    }

    return results

def offline_fix_z3(eval_result, tag, code):
    new_code = stitch_z3_code(code, eval_result)
    new_eval_result = evaluate_z3_code(tag, new_code)
    return new_eval_result, new_code

def main(input_file, output_file):
    jsonl_data = read_jsonl(input_file)
    results = []
    model = "gpt-4o-mini"
    for item in jsonl_data:
        try:
            print(f"*** Working on item {item['problem_name']}...")
            prompt = get_prompt(item)
            print(f"*** Prompt:\n{prompt}")
            response = prompt_model(model, prompt)
            print(f"*** Response:\n{response}")
            instantiations, formal_proof, z3_code  = get_post_result(model, response)
            eval_result = iter_evaulate_fix_z3(item, model, z3_code)
            
            item["instantiations"], item["formal_proof"], item["initial_z3_code"] = instantiations, formal_proof, z3_code
            item["prompt"], item["response"], item["model"] = prompt, response, model
            item["final_z3_code"], item["final_eval_result"] = eval_result["final_code"], eval_result["final_eval_result"]
            item["stitched_times"] = eval_result["stitched_times"]
            item["initial_eval_result"] = eval_result["initial_eval_result"]
            item["offline_stitch_applied"] = eval_result["offline_stitch_applied"]
            
            results.append(item)
            with open(output_file, 'a') as file:
                json.dump(item, file)
                file.write('\n')
            print(f"*** Done with {item['problem_name']}")
        except Exception as e:
            print(f"*** Exceptions with {item['problem_name']} with {e}")
        # exit(0)
    
if __name__ == "__main__":
    input_file = "/home/yang/CS474UnitProject/filtered.jsonl"
    output_file = "gpt_outputs.jsonl"
    main(input_file, output_file)