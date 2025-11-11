from environment import Env
from parser import parse
from interpreter import evaluate
from ast_nodes import String

def gambl_len(x):
    if isinstance(x, String):
        x = x.value
    if isinstance(x, (list, str)):
        return len(x)
    raise TypeError("object of type 'int' has no len()")

def run_test_case(description, code, expected_result, env=None):
    if env is None:
        env = Env()
        env.set("len", gambl_len)
    try:
        ast = parse(code)
        result = evaluate(ast, env)
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
        passed = isinstance(expected_result, str) and expected_result in error_msg
        status = "PASS" if passed else "FAIL"
        print(f"Test: {description}")
        print(f"Input: {code}")
        print(f"Expected: {expected_result}")
        print(f"Got: {error_msg}")
        print(f"Status: {status}")
        print("-" * 50)
        return passed

def run_all_tests():
    print("Studios 1–5: Comprehensive Feature Test")
    print("=" * 50)
    passed = 0
    total = 0

    test_cases = [
        # Studio 1: Arithmetic, assignment, print
        ("Addition", "a = 2 + 3; a", 5),
        ("Multiplication", "b = 4 * 5; b", 20),
        ("Parentheses", "c = (2 + 3) * 4; c", 20),

        # Studio 2: Conditionals, while loops
        ("If-then", "if 1 == 1 then 42 else 0", 42),
        ("If-then-else", "if 2 == 3 then 1 else 99", 99),
        ("While loop", "x = 0; while x < 3: x = x + 1; x", 3),

        # Studio 3: Functions
        ("Function definition/call", "def add(a, b): return a + b; add(2, 3)", 5),
        ("Function with local var", "def f(x): y = x * 2; return y; f(4)", 8),

        # Studio 4: Parameter passing, mutability
        ("Array mutation in function", "arr = [1,2,3]; def set0(a): a[0] = 99; set0(arr); arr", [99,2,3]),

        # Studio 5: Arrays, strings, indexing, len()
        ("Array literal and indexing", "a = [10, 20, 30]; a[1]", 20),
        ("Index assignment", "a = [10, 20, 30]; a[2] = 99; a", [10, 20, 99]),
        ("String literal and indexing", 's = "cat"; s[1]', "a"),
        ("len(array)", "a = [1,2,3]; len(a)", 3),
        ("len(string)", 's = "cat"; len(s)', 3),
        ("Nested array indexing", "b = [[1,2],[3,4]]; b[1][0]", 3),
        ("Empty array", "a = []; len(a)", 0),
        ("Index must be integer", "a = [1,2,3]; a[1.5] = 7", "Index must be integer"),
        ("Cannot assign to string index", 's = "cat"; s[0] = "x"', "object does not support item assignment"),
        ("len() expects array or string", "len(42)", "object of type 'int' has no len()"),
    ]

    for description, code, expected in test_cases:
        if run_test_case(description, code, expected):
            passed += 1
        total += 1

    print(f"\nTest Results: {passed}/{total} tests passed")
    if passed == total:
        print("All tests PASSED! 🎉")
    else:
        print(f"{total - passed} tests FAILED")

if __name__ == "__main__":
    run_all_tests()