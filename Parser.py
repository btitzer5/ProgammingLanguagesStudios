# Gambl/Parser.py
import re

#AST NOde classes
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
        self.op = op
        self.left = left
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

SPEC = [
    ("NUM", r"\d+"),
    ("EQ", r"=="),
    ("LT", r"<"),
    ("GT", r">"),
    ("AND", r"and\b"),
    ("OR", r"or\b"),
    ("NOT", r"not\b"),
    ("IF", r"if\b"),
    ("THEN", r"then\b"),
    ("ELSE", r"else\b"),
    ("WHILE", r"while\b"),
    ("ID",  r"[A-Za-z_]\w*"),
    ("ASSIGN", r"="),
    ("OP",  r"[+\-*/^()%]"),
    ("COLON", r":"),
    ("SEMICOLON", r";"),
    ("WS",  r"[ \t\r\n]+"),
    ("COMMENT", r"#.*"),
    ("MISMATCH", r"."),
]
MASTER = re.compile("|".join(f"(?P<{name}>{pat})" for name, pat in SPEC))

def lex(src):
    for m in MASTER.finditer(src):
        kind = m.lastgroup
        text = m.group()
        if kind == "WS" or kind == "COMMENT":
            continue
        if kind == "MISMATCH":
            raise ValueError(f"Unexpected character: {text!r} at index {m.start()}")
        yield (kind, text)

# Parse code
# Setup Tokens and cursor
tokens = []
i = 0           # cursor into tokens   

def at_eof():
    return i >= len(tokens)

def current():
    return tokens[i] if not at_eof() else ("EOF", "")

# Helpers peek_kind, peek_val
def peek_kind():
    return current()[0]     # "NUM", "ID", etc.

def peek_val():
    return current()[1]     # "x", "=", etc.

# Testing the peeks
# print(peek_kind(), peek_val())   # ID x

# Consume Helpers eat_kind, eat_val

def advance():
    global i
    if not at_eof(): i += 1

def eat_kind(name):
    if peek_kind() == name:
        token = current(); advance(); return token
    raise SyntaxError(f"expected kind{name!r}, got {current()!r}") # !r: prints literal form 

def eat_val(pat):               
    if peek_val() == pat:
        token = current(); advance(); return token
    raise SyntaxError(f"expected {pat!r}, got {current()!r}")

# Test the eats
# print(eat_kind("ID"))    # consumes ("ID","x")
# print(eat_val("="))      # consumes ("OP","=")

# Factor := "(" Expr ")" | NUM | ID
def parse_factor():
    if peek_val() == "(":
        eat_val("(")
        node = parse_expr()
        eat_val(")")
        return node
    elif peek_kind() == "NUM":
        token = eat_kind("NUM")
        return Number(token[1])
    elif peek_kind() == "ID":
        token = eat_kind("ID")
        return Variable(token[1])
    elif peek_val() == "not":
        eat_val("not")
        operand = parse_factor()
        return UnaryOp("not", operand)
    else:
        raise SyntaxError(f"unexpected {current()!r} in Factor")

# Power := Factor [ "^" Power ]
def parse_power():
    left = parse_factor()
    if peek_val() == "^":
        op = eat_val("^")[1]
        right = parse_power()
        return BinOp(left, op, right)
    return left


# Term := Power { ("*"|"/"|"%") Power }
def parse_term():
    node = parse_power()
    while peek_val() in ("*", "/", "%"):
        op = eat_val(peek_val())[1]
        right = parse_power()
        node = BinOp(node, op, right)
    return node

def parse_comparison():
    node = parse_expr()
    while peek_val() in ("<", ">"):
        op = eat_val(peek_val())[1]
        right = parse_expr()
        node = BinOp(node, op, right)
    return node

def parse_equality():
    node = parse_comparison()
    while peek_kind() == "EQ":
        op = eat_kind("EQ")[1]
        right = parse_comparison()
        node = BinOp(node, op, right)
    return node

def parse_and():
    node = parse_equality()
    while peek_kind() == "AND":
        op = eat_kind("AND")[1]
        right = parse_equality()
        node = BinOp(node, op, right)
    return node

def parse_or():
    node = parse_and()
    while peek_kind() == "OR":
        op = eat_kind("OR")[1]
        right = parse_and()
        node = BinOp(node, op, right)
    return node

def parse_if():
    if peek_kind() == "IF":
        op = eat_kind("IF")[1]
        condition = parse_or()
        then_branch = None
        else_branch = None
        if peek_kind() == "THEN":
            eat_kind("THEN")
            then_branch = parse_statement()
        if peek_kind() == "ELSE":
            eat_kind("ELSE")
            else_branch = parse_statement()
        return If(condition, then_branch, else_branch)
    else:
        return parse_or()
    
def parse_while():
    if peek_kind() == "WHILE":
        eat_kind("WHILE")[1]
        condition = parse_statement()
        eat_kind("COLON")
        body = parse_statement()
        return While(condition, body)
    else:
        return parse_if()

def parse_expr():
    node = parse_term()
    while peek_val() in ("+", "-"):
        op = eat_val(peek_val())[1]
        right = parse_term()
        node = BinOp(node, op, right)
    return node

def parse_assignment():
    if peek_kind() == "ID" and not at_eof() and i+1 < len(tokens) and tokens[i+1][1] == "=":
        name = eat_kind("ID")[1]
        eat_kind("ASSIGN")
        value = parse_while()
        return Assignment(name, value)
    else:
        return parse_while()

def parse_statement():
    return parse_assignment()

def parse(src):
    global tokens, i
    tokens = list(lex(src))    
    i = 0                      
    tree = parse_statement()
    if not at_eof():
        raise SyntaxError(f"extra input after {tree}: {current()!r}")
    return tree


if __name__ == "__main__":
     # Test cases
    print(parse("x = 5"))           # Assignment
    print(parse("2 + 3 * 4"))       # Arithmetic
    print(parse("x == 5 and y < 3")) # Boolean
    print(parse("while x < 10 x = x + 1")) # While loop
    print(parse("while x < 10 x = x + 1; if x == 10 y = 20 else y = 30")) # While loop with if statement
    print(parse("if x == 5 y = 10 else y = 20")) # If statement