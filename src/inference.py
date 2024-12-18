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
    4. Extract instantions from informal_proof as well as the ground terms in $phi_prime$ for each universally quantified sentence, and surround it with ```instantiations and ```.
    5. For each universally quantified sentence in $phi_prime$, try to replace it with all the possible extracted instantion. 
    You should get a list of quantifier-free formulas. Surround them with ```final_formula and ```.
    6. After replacement, write all these quantifier-free formulas using Z3 and try to solve them using an SMT solver. 
    If the SMT solver returns UNSAT, it means that $phi_prime$ is unsatisfiable, thereby $phi$ is valid. You should print "UNSAT, the original statement phi is valid.".
    Otherwise, you should print "SAT, the original statement phi might not be valid.
    
    For example, given the following informal_statement and informal_proof:
    informal_statement: What digit must be placed in the blank to make the four-digit integer $20\_7$ a multiple of 11? Show that it is 5.
    informal_proof: A number will be divisible by 11 if you get a multiple of 11 by alternately adding and then subtracting its digits.  If we name the blank integer $A$, then the alternating sum is $2 - 0 + A - 7 = A -5$.  This value can only be equal to 0 (as 11, 22, etc all yield $A$ that are too large), so $A = 5$ is the only digit that will work.
     
    Your response should be:
    The informal statement "What digit must be placed in the blank to make the four-digit integer $20\_7$ a multiple of 11? Show that it is 5." can be formally written as:
    ```phi
    \[ \phi = \exists A \, (0 \leq A \leq 9 \land (2 - 0 + A - 7) \equiv 0 \pmod{11}) \]
    ```
    
    Negating \(\phi\), we perform the following transformations:
    \[
    \neg \exists A \, (0 \leq A \leq 9 \land (2 - 0 + A - 7) \equiv 0 \pmod{11})
    \]

    This negation becomes:

    ```phi_prime
    \[ \phi\_prime = \\forall A \, \\neg (0 \leq A \leq 9 \land (2 - 0 + A - 7) \equiv 0 \pmod{11}) \]
    ```
    
    To skolemize $phi_prime$, $c$ is a new constant variable replacing $\exists x$:
    ```skelomization
    \[ \\text{skolemization}(\phi\_prime) = \\forall A \, (A < 0 \lor A > 9 \lor (2 - 0 + A - 7) \\not\equiv 0 \pmod{11}) \]
    ```
    
    Extract instantiations:
    ```instantiations
    \[ A = 5 \]
    ```
    
    Replace each universally quantified sentence with possible instantiation. 
    Given our skolemized formula:
    \[ A < 0 \lor A > 9 \lor (2 - 0 + A - 7) \\not\equiv 0 \pmod{11} \]
    
    using the instantiation $A = 5$, the formula becomes:
    ```final_formula
    \[ 5 < 0 \lor 5 > 9 \lor (2 - 0 + 5 - 7) \\not\equiv 0 \pmod{11} \]
    ```
    
    Z3 SMT solver:
    ```python
    from z3 import *

    # Define the formula and add the instantiation A = 5
    A = 5
    instantiation = Or(
        A < 0,          # A < 0
        A > 9,          # A > 9
        (2 - 0 + A - 7) % 11 != 0  # (2 - 0 + A - 7) not congruent to 0 mod 11
    )

    # Create a solver
    solver = Solver()

    # Add the formula with the instantiation
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

def zero_skolem_prompt_construction(input_item):
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
    6. After replacement, write all these quantifier-free formulas using Z3 and try to solve them using an SMT solver. 
    If the SMT solver returns UNSAT, it means that $phi_prime$ is unsatisfiable, thereby $phi$ is valid. You should print "UNSAT, the original statement phi is valid.".
    Otherwise, you should print "SAT, the original statement phi might not be valid.".
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
