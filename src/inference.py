import openai
import os
import textwrap
from openai import OpenAI

def model_prompting(model, prompt):
    if "gpt" in model:
        return prompt_gpt(model, prompt)

def prompt_gpt(model, prompt, max_len = 4096, temp = 0, max_attempts = 6):
    attempts = 1
    response = None
    while attempts < max_attempts and not response:
        try:
            client = OpenAI(
                api_key=os.environ.get("OPENAI_API_KEY"), 
            )

            chat_completion = client.chat.completions.create(
                messages = [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model = model,
                temperature = temp,
            )
            print(chat_completion)
            response = chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Exception at attemp {attempts}: {e}")
        attempts += 1
    return response

def prompt_construction(input_item):
    # input_item: {'dataset:, 'problem_name':, 'informal_statement':, 'informal_proof':,}
    prompt = textwrap.dedent(f"""
    You are an expert of formal method and proof generation.
    Given a problem with informal_statement and informal_proof.
    You should do the following tasks step by step:
    (1) Extract instantiations from the informal_proof, and surround it with ```instantiations and ```
    (2) Using the above instantiations, you should generate a formal proof, and surround it with ```formal_proof and ```
    (3) Write the formal proof using Python Z3, print "sat" if it is valid, otherwise print "unsat", generate the python code in ```python and ```
    
    For example, given the following informal_statement and informal_proof,
    informal_statement:
    For all integers x, if x > 2, then x^2 > 4.
    
    informal_proof:
    Consider any integer x that is greater than 2. By multiplying x by itself, since x>2, the square of x (i.e., x^2) will always be greater than the square of 2, which is 4. Therefore, x^2 > 4 holds for all x>2.
    
    Example Response:
    ```instantiations
    x > 2
    ```

    ```formal_proof
    1. Let x be any integer such that x > 2. (Universal instantiation)
    2. Since x > 2, multiply x by itself to get x^2.
    3. The property of multiplication and ordering in integers tells us that if x > 2, then multiplying x by a number greater than 2 (itself in this case) results in a product greater than 4. Thus, x^2 > 4.
    4. Therefore, for any x > 2, x^2 > 4 holds. (Generalization)
    ```
    
    ```python
    from z3 import Int, Solver, And
    
    x = Int('x')
    solver = Solver()
    solver.add(x > 2)
    solver.add(x**2 <= 4)
    if solver.check() == sat:
        print("A counterexample exists:", solver.model())
    else:
        print("No counterexample exists. The statement x^2 > 4 for all x > 2 is valid.")
    ```
    Problem:
    informal_statement:
    {input_item["informal_statement"]}
    
    informal_proof
    {input_item["informal_proof"]}
    
    Your response:
    """)
    return prompt
