import os

def process_response(model, response):
    if "gpt" in model:
        rets = parse_response_gpt(response) 

    # rets = instantiations, formal_proof, z3_code
    return rets 

def parse_response_gpt(response):
    phi_prime = response.split("```phi_prime\n")[-1].split("```")[0]
    phi = response.split("```phi\n")[-1].split("```")[0]
    skelomization = response.split("```skelomization\n")[-1].split("```")[0]
    instantiations = response.split("```instantiations\n")[-1].split("```")[0]
    final_formula = response.split("```final_formula\n")[-1].split("```")[0]
    z3_code = response.split("```python")[-1].split("```")[0] 
    return phi, phi_prime, skelomization, instantiations, final_formula, z3_code