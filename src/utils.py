import json
import subprocess

def read_jsonl(jsonl_path):
    jsonl_data = []
    with open(jsonl_path, 'r') as file:
        for line in file:
            json_obj = json.loads(line)
            jsonl_data.append(json_obj)
    return jsonl_data

def write_file(file_path, content):
    with open(file_path, 'w') as file:
        file.write(content)
        
def run_python_code(filename):
    try:
        result = subprocess.run(['python3', filename], text=True, capture_output=True, check=True)
        return result.stdout 
    except subprocess.CalledProcessError as e:
        return e.stdout + '\n' + e.stderr  # Return both stdout and stderr if an error occurs

def evaluate_z3_code(tag, code):
    tmp_file = f".tmp/{tag}_tmp.py"
    write_file(tmp_file, code)
    result = run_python_code(tmp_file)
    return result
    