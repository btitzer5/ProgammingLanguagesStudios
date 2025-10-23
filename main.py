# Gambl/main.py
# Main entry point 

import sys
from environment import Env
from parser import parse
from interpreter import evaluate

def run_test_case(description, code, expected_result, env=None):
    """Run a single test case and return whether it passed"""
    if env is None:
        env = Env()
    
    try:
        # Use the multi-statement parser directly
        ast = parse(code)
        result = evaluate(ast, env)
        
        # Check if expected error but didn't get one
        if isinstance(expected_result, str) and expected_result.startswith("ERROR"):
            # expected an error but got a result instead
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
            # didn't expect an error
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
    
    # Basic arithmetic and control flow tests
    test_cases = [
        # Arithmetic precedence: 1 + 2 * 3 → 7
        ("Arithmetic precedence", "1 + 2 * 3", 7),
        
        # Parentheses override precedence: (1 + 2) + (3 + 4) → 10
        ("Parentheses override precedence", "(1 + 2) + (3 + 4)", 10),
        
        # Variable assignment and reuse: x = 4; x + 5 → 9
        ("Variable assignment and reuse", "x = 4; x + 5", 9),
        
        # Chained assignments: a = 2; b = a * 5; b → 10
        ("Chained assignments", "a = 2; b = a * 5; b", 10),
        
        # Error handling: using undefined variable (e.g., y) raises runtime error
        ("Error handling (undefined variable)", "y + 2", "ERROR - Undefined variable: y"),
        
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
    
    # Function tests - use shared environment
    func_env = Env()

    function_test_cases = [
        # ...existing code...
        ("Simple function definition and call", "def add(a, b) : return a + b; add(2, 3)", 5),
        ("Function with no parameters", "def get_ten() : return 10; get_ten()", 10),
        ("Function with local variable", "def complex_add(a, b) : x = a + b; return x; complex_add(3, 4)", 7),
        ("Function with conditional", "def abs_val(x) : if x < 0 then return 0 - x else return x; abs_val(-5)", 5),
        ("Recursive function", "def factorial(n) : if n <= 1 then return 1 else return n * factorial(n - 1); factorial(4)", 24),
        ("Function with multiple statements", "def multi_stmt(x, y) : a = x * 2; b = y + 1; return a + b; multi_stmt(3, 4)", 11),
        ("Function calling function", "def double(x) : return x * 2; def quadruple(x) : return double(double(x)); quadruple(3)", 12),
        ("Function with closure", "y = 100; def add_y(x) : return x + y; add_y(5)", 105),
        ("Variable scope test", "x = 10; def test_scope(x) : return x + 1; test_scope(5); x", 10),

        # --- New tests for reference semantics ---
        ("Call by VALUE does not update caller", "x = 10; def f(y) : y = y + 5; f(x); x", 10),
        ("Call by REFERENCE updates caller", "x = 10; def f(ref y) : y = y + 5; f(x); x", 15),
    ]

    for description, code, expected in function_test_cases:
        if run_test_case(description, code, expected, func_env):
            passed += 1
        total += 1
    
    # Error test cases
    error_env = Env()
    
    error_test_cases = [
        # Test: Undefined function call
        ("Undefined function error", 
         "undefined_func()", 
         "ERROR - Undefined variable: undefined_func"),
        
        # Test: Wrong number of arguments setup
        ("Wrong argument count setup", 
         "def two_param(x, y) : return x + y", 
         None),
        
        ("Too many arguments error", 
         "two_param(1, 2, 3)", 
         "ERROR - Function two_param expects 2 arguments, got 3"),
        
        ("Too few arguments error", 
         "two_param(1)", 
         "ERROR - Function two_param expects 2 arguments, got 1"),
    ]
    
    for description, code, expected in error_test_cases:
        if run_test_case(description, code, expected, error_env):
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

def repl():
    """Run the Read-Eval-Print Loop for interactive use."""
    env = Env()
    print("Welcome to the Gambl interpreter. Type 'quit' to exit.")
    
    while True:
        try:
            line = input(">>> ").strip()
            if line.lower() in ("quit", "exit"):
                break
            if not line:
                continue

            # Handle multiple statements separated by semicolons
            statements = line.split(";")
            result = None
            for stmt in statements:
                stmt = stmt.strip()
                if stmt:
                    ast = parse(stmt)
                    result = evaluate(ast, env)
            
            if result is not None:
                print(result)
        
        except EOFError:
            # Handle EOF gracefully (Ctrl+D on Unix, Ctrl+Z on Windows, or piped input)
            print("\nGoodbye!")
            break
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Main entry point for the Gambl interpreter."""
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        run_all_tests()
    else:
        repl()

if __name__ == "__main__":
    main()