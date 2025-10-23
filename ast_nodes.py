# Gambl/ast_nodes.py
# AST node classes for the interpreter. These are just simple containers.

class Number:
    def __init__(self, value):
        self.value = int(value)
    def __repr__(self):
        return f"Number({self.value})"

class Variable:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return f"Variable({self.name!r})"

class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    def __repr__(self):
        return f"BinOp({self.left}, {self.op!r}, {self.right})"

class UnaryOp:
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand
    def __repr__(self):
        return f"UnaryOp({self.op!r}, {self.operand})"

class Assignment:
    def __init__(self, name, value):
        self.name = name
        self.value = value
    def __repr__(self):
        return f"Assignment({self.name!r}, {self.value})"

class If:
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch
    def __repr__(self):
        return f"If({self.condition}, {self.then_branch}, {self.else_branch})"

class While:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    def __repr__(self):
        return f"While({self.condition}, {self.body})"

class FunctionDef:
    def __init__(self, name, params, statements):
        self.name = name
        self.params = params  # List of (is_ref, name) tuples
        self.statements = statements
    def __repr__(self):
        return f"FunctionDef({self.name!r}, {self.params}, {self.statements})"
    
class Call:
    def __init__(self, name, args):
        self.name = name
        self.args = args
    def __repr__(self):
        return f"Call({self.name!r}, {self.args})"

class FunctionValue:
    def __init__(self, params, statements, env):
        self.params = params  # List of (is_ref, name) tuples
        self.body = statements
        self.env = env
    def __repr__(self):
        return f"FunctionValue({self.params}, {self.body}, env)"
    
class ReturnValue:
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"ReturnValue({self.value})"

class Block:
    def __init__(self, statements):
        self.statements = statements
    def __repr__(self):
        return f"Block({self.statements})"