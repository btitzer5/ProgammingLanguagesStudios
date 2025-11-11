# Gambl/lexer.py
# Tokenization and Lexical Analysis

import re

# Token specification
SPEC = [
    ("NUM", r"\d+(\.\d+)?"),
    ("STRING", r"\"([^\"\\]|\\.)*\""),
    ("EQ", r"=="),
    ("LE", r"<="),
    ("GE", r">="),
    ("LT", r"<"),
    ("GT", r">"),
    ("AND", r"and\b"),
    ("OR", r"or\b"),
    ("NOT", r"not\b"),
    ("REF", r"ref\b"),
    ("IF", r"if\b"),
    ("THEN", r"then\b"),
    ("ELSE", r"else\b"),
    ("WHILE", r"while\b"),
    ("DEF", r"def\b"),
    ("RETURN", r"return\b"),
    ("ID",  r"[A-Za-z_]\w*"),
    ("ASSIGN", r"="),
    ("PLUS", r"\+"),
    ("MINUS", r"-"),
    ("MUL", r"\*"),
    ("DIV", r"/"),
    ("MOD", r"%"),
    ("POW", r"\^"),
    ("LBRACK", r"\["),
    ("RBRACK", r"\]"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("COMMA", r","),
    ("COLON", r":"),
    ("SEMICOLON", r";"),
    ("WS",  r"[ \t\r\n]+"),
    ("COMMENT", r"#.*"),
    ("MISMATCH", r"."),
]

# Compile the master regex pattern
MASTER = re.compile("|".join(f"(?P<{name}>{pat})" for name, pat in SPEC))

def lex(src):
    """
    Tokenize source code into a sequence of (token_type, token_value) tuples.
    
    Args:
        src (str): Source code to tokenize
        
    Yields:
        tuple: (token_type, token_value) pairs
        
    Raises:
        ValueError: If an unexpected character is encountered
    """
    for m in MASTER.finditer(src):
        kind = m.lastgroup
        text = m.group()
        
        # Skip whitespace and comments
        if kind == "WS" or kind == "COMMENT":
            continue
            
        # Report unexpected characters
        if kind == "MISMATCH":
            raise ValueError(f"Unexpected character: {text!r} at index {m.start()}")
            
        yield (kind, text)

def tokenize(src):
    """
    Convenience function that returns a list of all tokens.
    
    Args:
        src (str): Source code to tokenize
        
    Returns:
        list: List of (token_type, token_value) tuples
    """
    return list(lex(src))

if __name__ == "__main__":
    # Test the lexer
    test_code = "def add(x, y) : return x + y; add(2, 3)"
    tokens = tokenize(test_code)
    for token in tokens:
        print(token)