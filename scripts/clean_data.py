import pathlib
import glob
import json

## scan all the files under root_dir
def proof_filter(root_path, keywords):
    cleaned_results = []
    if 'MINI_F2F' in root_path:
        dataset = "MINI_F2F"
    elif 'FIMO' in root_path:
        dataset = "FIMO"
    path = root_path + "/**"
    for path in glob.glob(path, recursive=True):
        if not path.endswith(".json"):
            continue
        data = json.load(open(path, 'r'))
        
        informal_statement = data["informal_statement"]
        informal_proof  = data["informal_proof"]
        
        ## check if informal_statement or informal proof contains any of the 'keyword'
        if any(kw in informal_statement or kw in informal_proof for kw in keywords):
            data_for_all = {
                "dataset": dataset,
                "problem_name": data["problem_name"],
                "informal_statement": data["informal_statement"],
                "informal_proof": data["informal_proof"]
            }
            cleaned_results.append(data_for_all)
    return cleaned_results
        
        

if __name__ == "__main__":
    write_path = "../filtered.jsonl"
    keywords = ["for all", "for any", "forall"]
    root_mini = "../dataset/MINI_F2F"
    root_fimo = "../dataset/FIMO"
    data_mini = proof_filter(root_mini, keywords)
    data_fimo = proof_filter(root_fimo, keywords)
    
    data = data_mini + data_fimo
    with open(write_path, 'w') as wr:
        for d in data:
            json.dump(d, wr)
            wr.write("\n")