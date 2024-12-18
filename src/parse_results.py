import os
import sys
import json
from utils import read_jsonl


def main(input_file, output_file):
    jsonl_data = read_jsonl(input_file)
    unsuccess, unsuccess_iter0 = [], []
    succuss, succuss_iter0 = [], []
    succuss_offline_stitch_applied = []
    applied = []
    qi_success = []
    for item in jsonl_data:
        if "forall" in item["phi_prime"]:
            # print(item["problem_name"])
            # print(item["phi_prime"])
            
            new_item = {
                "dataset": item["dataset"],
                "problem_name": item["problem_name"],
                "informal_statement": item["informal_statement"],
                "informal_proof": item["informal_proof"]
            }
            applied.append(new_item)
            # print(item["phi_prime"])
            if "UNSAT" in item["final_eval_result"]:# and item["stitched_times"] > 0:
                # print(item["problem_name"])
                # print(item["stitched_times"])
                qi_success.append(item)
        continue
        if ("UNSAT" not in item["final_eval_result"]) or \
            ("UNSAT" in item["final_eval_result"] and item["stitched_times"] > 0):
            new_item = {
                "dataset": item["dataset"],
                "problem_name": item["problem_name"],
                "informal_statement": item["informal_statement"],
                "informal_proof": item["informal_proof"]
            }
            unsuccess_iter0.append(new_item)
        if "UNSAT" in item["final_eval_result"]:
            succuss.append(item)
        if "UNSAT" in item["final_eval_result"] and item["stitched_times"] == 0:
            succuss_iter0.append(item)
        if "UNSAT" in item["final_eval_result"] and item["offline_stitch_applied"] == True:
            succuss_offline_stitch_applied.append(item)
            # print(item["problem_name"])
        if "UNSAT" not in item["final_eval_result"]:
            unsuccess.append(item)

    # with open(output_file, 'a') as file:
    #     for new_item in applied:
    #         json.dump(new_item, file)
    #         file.write('\n')
    print(len(applied))
    # with open(output_file, 'a') as file:
    #     for new_item in applied:
    #         json.dump(new_item, file)
    #         file.write('\n')
    print(len(qi_success))
    print(f"unsuccess: {len(unsuccess)}, unsuccess_iter0: {len(unsuccess_iter0)},succuss:{len(succuss)}, succuss_iter0:{len(succuss_iter0)}, succuss_offline_stitch_applied: {len(succuss_offline_stitch_applied)}")

if __name__ == "__main__":
    args = sys.argv[1:]
    input_file = args[0]
    output_file = args[1]
    #python3 parse_results.py ../results/few_shot_gpt4o_outputs.jsonl unsucess.jsonl
    
    if not os.path.exists(output_file):
        with open(output_file, 'w') as file:
            pass 
        
    main(input_file, output_file)