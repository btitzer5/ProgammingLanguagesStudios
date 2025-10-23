import pytest
from interpreter import evaluate
from parser import Parser
from environment import Env

# Helper to run code and get variable value
def run_and_get_var(src, var):
    parser = Parser()
    ast = parser.parse(src)
    env = Env()
    evaluate(ast, env)
    return env.get(var)

def test_by_value():
    src = """
    x = 10;
    def f(y) : y = y + 5;
    f(x);
    """
    result = run_and_get_var(src, 'x')
    print("\n[test_by_value] Input:\n" + src.strip())
    print(f"[test_by_value] Output: x = {result}")
    assert result == 10  # x should not change

def test_by_reference():
    src = """
    x = 10;
    def f(ref y) : y = y + 5;
    f(x);
    """
    result = run_and_get_var(src, 'x')
    print("\n[test_by_reference] Input:\n" + src.strip())
    print(f"[test_by_reference] Output: x = {result}")
    assert result == 15  # x should be updated

def test_ref_must_be_var():
    src = """
    def f(ref y) : y = y + 1;
    f(42);
    """
    parser = Parser()
    ast = parser.parse(src)
    env = Env()
    print("\n[test_ref_must_be_var] Input:\n" + src.strip())
    with pytest.raises(RuntimeError) as excinfo:
        evaluate(ast, env)
    print(f"[test_ref_must_be_var] Output: {excinfo.value}")

def test_wrong_arg_count():
    src = """
    def f(x, y) : return x + y;
    f(1);
    """
    parser = Parser()
    ast = parser.parse(src)
    env = Env()
    print("\n[test_wrong_arg_count] Input:\n" + src.strip())
    with pytest.raises(RuntimeError) as excinfo:
        evaluate(ast, env)
    print(f"[test_wrong_arg_count] Output: {excinfo.value}")
