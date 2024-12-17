import os
import json
import signal
import sys
from datetime import datetime
from inference import skolem_prompt_construction, model_prompting
from post_processing import process_response
from utils import read_jsonl, evaluate_z3_code
from stitching import stitch_z3_code, llm_fix_z3

def get_prompt(input_item):
    prompt = skolem_prompt_construction(input_item)
    return prompt

def prompt_model(model, prompt, sampling):
    response = model_prompting(model, prompt, sampling)
    return response

def get_post_result(model, response):
    phi, phi_prime, skelomization, instantiations, final_formula, z3_code = process_response(model, response)
    return phi, phi_prime, skelomization, instantiations, final_formula, z3_code 

def iter_evaulate_fix_z3(item, model, code, sampling, attempts = 3):
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
    
    if sampling:
        results = {
            "initial_eval_result": initial_eval_result,
            "final_code": code,
            "final_eval_result": initial_eval_result,
            "stitched_times": time,
            "offline_stitch_applied": offline_stitch_applied
        }
        return results
    
    while time < attempts and "Traceback" in prev_eval_result:
        new_eval_result, new_code = offline_fix_z3(initial_eval_result, tag, prev_code)
        
        print(f"*** Offline stitched code:\n{new_code}\n*** Offline stitched result: {new_eval_result}")
        
        if new_eval_result != prev_eval_result:
            offline_stitch_applied = True
        
        if "Traceback" in new_eval_result:
            new_code = llm_fix_z3(new_code, new_eval_result, model, sampling)
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

def timeout_handler(signum, frame):
    raise TimeoutError

signal.signal(signal.SIGALRM, timeout_handler)

def main(input_file, output_file, sampling):
    jsonl_data = read_jsonl(input_file)
    results = []
    model = "gpt-4o"
    for item in jsonl_data:
        signal.alarm(300) 
        try:
            if is_item_in_jsonl(output_file, item):
                print(f"{item['problem_name']} is already done!")
                continue
            print(f"*** Working on item {item['problem_name']} starting at {datetime.now().strftime('%H:%M:%S')}...")
            prompt = get_prompt(item)
            print(f"*** Prompt:\n{prompt}")
            response = prompt_model(model, prompt, sampling)
            print(f"*** Response:\n{response}")
            phi, phi_prime, skelomization, instantiations, final_formula, z3_code   = get_post_result(model, response)
            eval_result = iter_evaulate_fix_z3(item, model, z3_code, sampling)
            
            item["phi"], item["phi_prime"], item["skelomization"] = phi, phi_prime, skelomization
            item["instantiations"], item["final_formula"], item["initial_z3_code"] = instantiations, final_formula, z3_code
            item["prompt"], item["response"], item["model"] = prompt, response, model
            item["final_z3_code"], item["final_eval_result"] = eval_result["final_code"], eval_result["final_eval_result"]
            item["stitched_times"] = eval_result["stitched_times"]
            item["initial_eval_result"] = eval_result["initial_eval_result"]
            item["offline_stitch_applied"] = eval_result["offline_stitch_applied"]
            
            results.append(item)
            with open(output_file, 'a') as file:
                json.dump(item, file)
                file.write('\n')
            print(f"*** Done with {item['problem_name']} ending at {datetime.now().strftime('%H:%M:%S')}")
        except TimeoutError:
            print(f"*** Exceptions with {item['problem_name']} with TimeoutError")
            item["final_eval_result"] = "TimeoutError"
        except Exception as e:
            print(f"*** Exceptions with {item['problem_name']} with {e}")
        signal.alarm(0)
        # exit(0)

def is_item_in_jsonl(file_path, item):
    with open(file_path, 'r') as file:
        for line in file:
            json_data = json.loads(line)
            if item["problem_name"] == json_data["problem_name"]:
                return True
    return False
    
if __name__ == "__main__":
    args = sys.argv[1:]
    input_file = args[0]
    output_file = args[1]
    sampling = True if args[2] == "True" else False
    # input_file = "/home/yang/CS474UnitProject/MINI_F2F_test.jsonl"
    # output_file = "few_shot_gpt4o_outputs.jsonl"
    
    print(f"if sampling: {sampling}")
    if not os.path.exists(output_file):
        with open(output_file, 'w') as file:
            pass 
        
    main(input_file, output_file, sampling)
