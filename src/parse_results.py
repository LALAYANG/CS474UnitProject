import os
import sys
import json
from utils import read_jsonl


# if "UNSAT" in item["final_eval_result"]:
#     print(item["final_eval_result"])
#     unsuccess.append(item)
            

def main(input_file, output_file):
    jsonl_data = read_jsonl(input_file)
    unsuccess = []
    for item in jsonl_data:
        if ("UNSAT" not in item["final_eval_result"]) or \
            ("UNSAT" in item["final_eval_result"] and item["stitched_times"] > 0):
            new_item = {
                "dataset": item["dataset"],
                "problem_name": item["problem_name"],
                "informal_statement": item["informal_statement"],
                "informal_proof": item["informal_proof"]
            }
            unsuccess.append(new_item)

    with open(output_file, 'a') as file:
        for new_item in unsuccess:
            json.dump(new_item, file)
            file.write('\n')
    print(len(unsuccess))

if __name__ == "__main__":
    args = sys.argv[1:]
    input_file = args[0]
    output_file = args[1]
    #python3 parse_results.py ../results/few_shot_gpt4o_outputs.jsonl unsucess.jsonl
    
    if not os.path.exists(output_file):
        with open(output_file, 'w') as file:
            pass 
        
    main(input_file, output_file)