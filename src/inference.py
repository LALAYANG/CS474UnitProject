import openai
import os
import textwrap
from openai import OpenAI

def model_prompting(model, prompt, sampling):
    if "gpt" in model:
        return prompt_gpt(model, prompt, sampling)

def prompt_gpt(model, prompt, sampling, max_len = 4096, temp = 0, max_attempts = 6):
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
                temperature = 1 if sampling else temp,
            )
            print(f"temperature: {1 if sampling else temp}")
            print(chat_completion)
            response = chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Exception at attemp {attempts}: {e}")
        attempts += 1
    return response


def skolem_prompt_construction(input_item):
    # input_item: {'dataset:, 'problem_name':, 'informal_statement':, 'informal_proof':,}
    prompt = textwrap.dedent(f"""
    You are an expert of formal method and proof generation.
    For any formula $phi$, we can prove $phi$ is valid by proving that $neg phi$ is unsatisfiable.
    
    Given a problem with informal_statement and informal_proof.
    You should do the following tasks step by step:
    1. Translate informal_statement into a formula $phi$, surround it with ```phi and ```.
    2. Negate $phi$ to get $phi_prime = neg phi$ in Math. During this process, all the existing quantifiers should also get negated, surround it with ```phi_prime and ```.
    3. Skolemize the negated formula $phi_prime$ into prenex normal form, 
    namely an equisatisfiable formula which has only universal quantification. Surround it with ```skelomization and ```.
    Specifically, you need to replace all $\exists y$ with a concrete and new function computing $y$ from all the arguments $y$ depends on (i.e., the universally quantified arguments that appear before $y$). 
    If $y$ does not depend on any argument, you can replace it with a concrete and new constant variable.
    4. Extract instantions from informal_proof as well as the ground terms in $phi_prime$ for each quantified sentence, and surround it with ```instantiations and ```.
    5. For each quantified sentence in $phi_prime$, try to replace it with all the possible extracted instantion. You should get a list of quantifier-free formulas. Surround them with ```final_formula and ```.
    6. After replacement, write all these quantifier-free formulas using Z3 and try to solve them using an SMT solver. If the SMT solver returns UNSAT, it means that $phi_prime$ is unsatisfiable, thereby $phi$ is valid. Surround the code with ```python and ```
    
    For example, given the following informal_statement and informal_proof:
    informal_statement: For all integers x, if x > 2, then x^2 > 4., 
    informal_proof: Consider any integer x that is greater than 2. By multiplying x by itself, since x>2, the square of x (i.e., x^2) will always be greater than the square of 2, which is 4. Therefore, x^2 > 4 holds for all x>2.
     
    Your response should be:
    The informal statement "For all integers x, if x > 2, then x^2 > 4" can be formally written as:
    ```phi
    \[ phi = \\forall x \, (int(x) \\to (x > 2 \to x^2 > 4)) \]
    ```
    
    Negating $phi$, we perform the following transformations:
    \[
    \\neg \\forall x \, (int(x) \\to (x > 2 \\to x^2 > 4))
    \]
    This negation becomes:
    ```phi_prime
    \[ phi_prime = \exists x \, (int(x) \land (x > 2 \land x^2 \leq 4)) \]
    ```
    
    To skolemize $phi_prime$, $c$ is a new constant variable replacing $\exists x$:
    ```skelomization
    \[ skemolization(phi_prime) = int(c) \land (c > 2 \land c^2 \leq 4) \]
    ```
    
    Extract instantiations:
    ```instantiations
    \[ x = 3 \]
    ```
    
    Replace each quantified sentence with possible instantiation. 
    Given our skolemized formula:
    \[ int(c) and (c > 2 and c^2 <= 4) \]
    
    using the instantiation $x = 3$, the formula becomes:
    ```final_formula
    \[ int(3) and (3 > 2 and 3^2 <= 4) \]
    ```
    
    Z3 SMT solver:
    ```python
    from z3 import *

    # Define the formula and add the instantiation x = 3
    instantiation = And(
        3 > 2,         # x > 2
        3**2 <= 4      # x^2 <= 4
    )

    # Create a solver
    solver = Solver()

    # Add both the formula and instantiation
    solver.add(instantiation)

    # Check satisfiability
    if solver.check() == unsat:
        print("UNSAT, the original statement phi is valid.")
    else:
        print("SAT, the original statement phi might not be valid.")
    ```
    
    Problem:
    informal_statement:
    {input_item["informal_statement"]}
    
    informal_proof
    {input_item["informal_proof"]}
    
    Your response:
    """)
    return prompt
     

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
