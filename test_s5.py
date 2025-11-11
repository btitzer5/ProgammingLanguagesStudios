from environment import Env
from parser import parse
from interpreter import evaluate
from ast_nodes import String

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
        passed = isinstance(expected_result, str) and expected_result.startswith("ERROR")
        status = "PASS" if passed else "FAIL"
        print(f"Test: {description}")
        print(f"Input: {code}")
        print(f"Expected: {expected_result}")
        print(f"Got: {error_msg}")
        print(f"Status: {status}")
        print("-" * 50)
        return passed


def gambl_len(x):
    if isinstance(x, String):
        x = x.value
    if isinstance(x, (list, str)):
        return len(x)
    raise TypeError("object of type 'int' has no len()")

def run_all_tests():
    print("Studio 5: Data Types, Arrays, Strings, Indexing, len()")
    print("=" * 50)
    passed = 0
    total = 0

    global_env = Env()
    global_env.set("len", gambl_len)


    test_cases = [
        # Array literal and indexing
        ("Array literal and indexing", "a = [10, 20, 30]; a[1]", 20),
        # Index assignment (mutability)
        ("Index assignment", "a = [10, 20, 30]; a[2] = 99; a", [10, 20, 99]),
        # String literal and indexing
        ("String literal and indexing", 's = "cat"; s[1]', "a"),
        # Built-in len() on array
        ("len(array)", "a = [1,2,3]; len(a)", 3),
        # Built-in len() on string
        ("len(string)", 's = "cat"; len(s)', 3),
        # Nested arrays
        ("Nested array indexing", "b = [[1,2],[3,4]]; b[1][0]", 3),
        # Empty array
        ("Empty array", "a = []; len(a)", 0),
        # Error: index must be integer
        ("Index must be integer", "a = [1,2,3]; a[1.5] = 7", "ERROR - Index must be integer"),
        # Error: only arrays are mutable
        ("Cannot assign to string index", 's = "cat"; s[0] = "x"', "ERROR - 'str' object does not support item assignment"),
        # Error: len() expects array or string
        ("len() expects array or string", "len(42)", "ERROR - object of type 'int' has no len()"),
    ]

    for description, code, expected in test_cases:
        if run_test_case(description, code, expected, env=global_env):
            passed += 1
        total += 1

    print(f"\nTest Results: {passed}/{total} tests passed")
    if passed == total:
        print("All tests PASSED! 🎉")
    else:
        print(f"{total - passed} tests FAILED")

if __name__ == "__main__":
    run_all_tests()