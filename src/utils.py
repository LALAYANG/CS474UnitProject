import json

def read_jsonl(jsonl_path):
    jsonl_data = []
    with open(jsonl_path, 'r') as file:
        for line in file:
            json_obj = json.loads(line)
            jsonl_data.append(json_obj)
    return jsonl_data