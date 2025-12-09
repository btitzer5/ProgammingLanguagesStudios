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

def test_try_catch():
    src = """
    try: x = 10 / 0; catch e: x = 42;
    """
    result = run_and_get_var(src, 'x')
    print("\n[test_try_catch] Input:\n" + src.strip())
    print(f"[test_try_catch] Output: x = {result}")
    assert result == 42  # x should not change

