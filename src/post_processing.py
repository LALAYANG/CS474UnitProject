import os

def process_response(model, response):
    if "gpt" in model:
        rets = parse_response_gpt(response) 

    # rets = instantiations, formal_proof, z3_code
    return rets 

def parse_response_gpt(response):
    instantiations = response.split("```instantiations")[-1].split("```")[0]
    formal_proof = response.split("```formal_proof")[-1].split("```")[0]
    z3_code = response.split("```python")[-1].split("```")[0] 
    return instantiations, formal_proof, z3_code