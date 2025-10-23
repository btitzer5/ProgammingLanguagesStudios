# Gambl/new_interpreter.py
# Evaluation and Interpretation Logic

from ast_nodes import Number, Variable, BinOp, UnaryOp, Assignment, If, While, FunctionDef, Call, FunctionValue, ReturnValue, Block
from environment import Env

def evaluate(node, env):
    """
    Evaluate an AST node in the given environment.
    
    Args:
        node: AST node to evaluate
        env: Environment for variable/function lookup
        
    Returns:
        The result of evaluating the node
    """
    if isinstance(node, Number):
        return node.value
    
    elif isinstance(node, Variable):
        val = env.get(node.name)
    # If it's a Reference, get the value
        if hasattr(val, 'get') and callable(val.get):
            return val.get()
        return val
    
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
        elif node.op == "<=":
            return left <= right
        elif node.op == ">=":
            return left >= right
        elif node.op == "and":
            return left and right
        elif node.op == "or":
            return left or right
        else:
            raise RuntimeError(f"Unknown operator: {node.op}")

    elif isinstance(node, While):
        result = None
        while True:
            condition = evaluate(node.condition, env)  # Check condition again
            if not condition:
                break
            result = evaluate(node.body, env)  # Just run the body
        return result  # Last result

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
        elif node.op == "-":
            return -operand
        else:
            raise RuntimeError(f"Unknown unary operator: {node.op}")
        
    elif isinstance(node, Assignment):
        value = evaluate(node.value, env)
        # Set through Reference if needed
        var = None
        try:
            var = env.get(node.name)
        except Exception:
            pass
        if hasattr(var, 'set') and callable(var.set):
            var.set(value)
        else:
            env.set(node.name, value)
        return None  # Assignments return no value
    
    elif isinstance(node, FunctionDef):
        # Store the function in the environment
        func_value = FunctionValue(node.params, node.statements, env)
        env.set(node.name, func_value)
        return None  # Defining a function returns nothing
    
    elif isinstance(node, Call):
        # Look up the function
        func = env.get(node.name)
        if not isinstance(func, FunctionValue):
            raise RuntimeError(f"{node.name} is not a function")
        # Check argument count
        if len(node.args) != len(func.params):
            raise RuntimeError(f"Function {node.name} expects {len(func.params)} arguments, got {len(node.args)}")
        # Evaluate args and handle ref/value
        arg_values = []
        for arg, (is_ref, pname) in zip(node.args, func.params):
            if is_ref:
                # For ref, wrap as Reference
                if isinstance(arg, Variable):
                    arg_values.append(__import__('environment').Reference(env, arg.name))
                else:
                    raise RuntimeError("ref parameter needs a variable")
            else:
                val = evaluate(arg, env)
                if hasattr(val, 'get') and callable(val.get):
                    arg_values.append(val.get())
                else:
                    arg_values.append(val)
        # New environment for the call
        func_env = Env()
        func_env.variables = func.env.variables.copy()  # Copy closure
        # Bind params
        for (is_ref, pname), arg_val in zip(func.params, arg_values):
            func_env.define(pname, arg_val)
        # Run function body
        result = None
        for stmt in func.body:
            if isinstance(stmt, ReturnValue):
                return evaluate(stmt.value, func_env)
            else:
                result = evaluate(stmt, func_env)
        return result  # Last result if no return
    
    elif isinstance(node, ReturnValue):
        return evaluate(node.value, env)
    
    elif isinstance(node, Block):
        result = None
        for stmt in node.statements:
            result = evaluate(stmt, env)
        return result  # Last statement result
    
    else:
        raise RuntimeError(f"Unknown AST node: {type(node)}")

def repl():
    """Interactive loop."""
    from parser import parse
    
    env = Env()
    print("Welcome to the Gambl interpreter. Type 'quit' to exit.")
    
    while True:
        try:
            line = input(">>> ").strip()
            if line.lower() in ("quit", "exit"):
                break
            if not line:
                continue

            # Split on semicolons
            statements = line.split(";")
            result = None
            for stmt in statements:
                stmt = stmt.strip()
                if stmt:
                    ast = parse(stmt)
                    result = evaluate(ast, env)
            
            if result is not None:
                print(result)
        
        except Exception as e:
            print(f"Error: {e}")

