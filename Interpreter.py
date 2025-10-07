from Parser import *

class Env:
    def __init__(self):
        self.variables = {}

    def define(self, name, value):
        self.variables[name] = value


    def get(self, name):
        if name in self.variables:
            return self.variables[name]
        else:
            raise NameError(f"Undefined variable: {name}")
        
    
    def set(self, name, value):
        if name in self.variables:
            self.variables[name] = value
        else:
            self.define(name, value)

def evaluate(node, env):
    if isinstance(node, Number):
        return node.value
    
    elif isinstance(node, Variable):
        return env.get(node.name)
    
    elif isinstance(node, BinOp):
        left = evaluate(node.left, env)
        right = evaluate(node.right, env)

        if node.op == "+":
            return left + right
        elif node.op == "-":
            return left - right
        elif node.op == "*":
            return left * right
        elif node.op == "/":
            return left // right
        elif node.op == "%":
            return left % right
        elif node.op == "^":
            return left ** right
        elif node.op == "==":
            return left == right
        elif node.op == "<":
            return left < right
        elif node.op == ">":
            return left > right
        elif node.op == "and":
            return left and right
        elif node.op == "or":
            return left or right
        
        else:
            raise RuntimeError(f"Unknown operator: {node.op}")\


    elif isinstance(node, While):
        result = None
        while True:
            condition = evaluate(node.condition, env)  # Re-evaluate each time
            if not condition:
                break
            result = evaluate(node.body, env)  # Don't return, just store result
        return result  # Return the last result



    elif isinstance(node, If):
        condition = evaluate(node.condition, env)
        if condition:
            return evaluate(node.then_branch, env) if node.then_branch else None
        else:
            return evaluate(node.else_branch, env) if node.else_branch else None
    
    elif isinstance(node, UnaryOp):
        operand = evaluate(node.operand, env)
        if node.op == "not":
            return not operand
        else:
            raise RuntimeError(f"Unknown unary operator: {node.op}")
        
    elif isinstance(node, Assignment):
        value = evaluate(node.value, env)
        env.set(node.name, value)
        return None # Assignments return no value
    
    else:
        raise RuntimeError(f"Unknown AST node: {type(node)}")
    
def repl():
    env = Env()
    print("Welcome to the interpreter. Type 'quit' to exit.")
    while True:
        try:
            line = input(">>> ").strip()
            if line.lower() in ("quit", "exit"):
                break
            if not line:
                continue

            #handle multiple statements separated by semicolons
            statements = line.split(";")
            for stmt in statements:
                stmt = stmt.strip()
                if stmt:
                    ast = parse(stmt)
                    result = evaluate(ast, env)
            
            if result is not None:
                print(result)
        
        except Exception as e:
            print(f"Error: {e}")

def run_test_case(description, code, expected_result, env=None):
    """Run a single test case and return whether it passed"""
    if env is None:
        env = Env()
    
    try:
        # Handle multiple statements separated by semicolons
        statements = code.split(";")
        result = None
        for stmt in statements:
            stmt = stmt.strip()
            if stmt:
                ast = parse(stmt)
                result = evaluate(ast, env)
        
        # Check if we expected an error but didn't get one
        if isinstance(expected_result, str) and expected_result.startswith("ERROR"):
            # We expected an error but got a result instead
            status = "FAIL"
            passed = False
        else:
            # Compare result with expected
            passed = result == expected_result
            status = "PASS" if passed else "FAIL"
        
        print(f"Test: {description}")
        print(f"Input: {code}")
        print(f"Expected: {expected_result}")
        print(f"Got: {result}")
        print(f"Status: {status}")
        print("-" * 50)
        
        return passed
        
    except Exception as e:
        error_msg = f"ERROR - {e}"
        
        # Check if this error matches what we expected
        if isinstance(expected_result, str) and expected_result.startswith("ERROR"):
            # check if the error messages match
            passed = error_msg == expected_result
            status = "PASS" if passed else "FAIL"
        else:
            # We didn't expect an error
            passed = False
            status = "FAIL"
        
        print(f"Test: {description}")
        print(f"Input: {code}")
        print(f"Expected: {expected_result}")
        print(f"Got: {error_msg}")
        print(f"Status: {status}")
        print("-" * 50)
        return passed

def run_all_tests():
    """Run all test cases"""
    print("Running Gambl Language Tests")
    print("=" * 50)
    
    passed = 0
    total = 0
    

    
    # Basic if/else tests
    test_cases = [
        #Arithmetic precedence: 1 + 2 * 3 → 7
        ("Arithmetic precedence", "1 + 2 * 3", 7),
        
        #Parentheses override precedence: (1 + 2) + (3 + 4) → 10
        ("Parentheses override precedence", "(1 + 2) + (3 + 4)", 10),
        
        #Variable assignment and reuse: x = 4; x + 5 → 9
        ("Variable assignment and reuse", "x = 4; x + 5", 9),
        
        #Chained assignments: a = 2; b = a * 5; b → 10
        ("Chained assignments", "a = 2; b = a * 5; b", 10),
        
        #Error handling: using undefined variable (e.g., y) raises runtime error
        ("Error handling (undefined variable)", "y + 2", "ERROR - Undefined variable: y"),  # Expect error

        # Basic if/else: if 1 < 2 then 3 else 4 → 3
        ("Basic if/else (true condition)", "if 1 < 2 then 3 else 4", 3),
        
        # False branch: if 2 < 1 then 3 else 4 → 4
        ("False branch (false condition)", "if 2 < 1 then 3 else 4", 4),
        
        # Simple while: i = 0; while i < 3 { i = i + 1 }; i → 3
        ("Simple while loop", "i = 0; while i < 3 : i = i + 1; i", 3),
        
        # Edge case: while false_condition { ... } → does nothing (no infinite loop)
        ("While with false condition", "i = 5; while i < 0 : i = i + 1; i", 5),
    ]
    
    for description, code, expected in test_cases:
        if run_test_case(description, code, expected):
            passed += 1
        total += 1
    
    # Nested test case 
    nested_env = Env()
    if run_test_case("Nested while with if/else", 
                     "i = 0; while i < 5 : if i % 2 == 0 then i = i + 2 else i = i + 1; i", 
                     6, nested_env):
        passed += 1
    total += 1
    
    # Summary
    print(f"\nTest Results: {passed}/{total} tests passed")
    if passed == total:
        print("All tests PASSED! 🎉")
    else:
        print(f"{total - passed} tests FAILED")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        run_all_tests()
    else:
        repl()
   