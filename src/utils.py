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
        
def prep_isabelle_proof(code, name):
    proof_folder_path = os.path.join("proof", name)
    os.makedirs(proof_folder_path, exist_ok=True)

    thy_path = os.path.join(proof_folder_path, f"{name}.thy")
    with open(thy_path, 'w') as file:
        file.write(code)
    
    root_path = os.path.join(proof_folder_path, "ROOT")
    root_content = textwrap.dedent(f"""
    session Test = HOL + 
    theories
        {name}
    """)
    with open(root_path, "w") as file:
        file.write(root_content)
        
def run_isabelle_code(filename, folder_path):
    try:
        result = subprocess.run(['../../Isabelle2024/bin/isabelle', filename], cwd=folder_path, text=True, capture_output=True, check=True)
        return result.stdout 
    except subprocess.CalledProcessError as e:
        return e.stdout + '\n' + e.stderr
        
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
    