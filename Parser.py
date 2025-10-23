# Gambl/Parser.py
# Parsing Logic - Converts tokens to Abstract Syntax Tree
from ast_nodes import Number, Variable, BinOp, UnaryOp, Assignment, If, While, FunctionDef, Call, FunctionValue, ReturnValue, Block
from lexer import lex

class Parser:
    """
    Recursive descent parser for the Gambl language.
    Converts a stream of tokens into an Abstract Syntax Tree (AST).
    """
    
    def __init__(self):
        self.tokens = []
        self.i = 0  # cursor into tokens
    
    def at_eof(self):
        """Check if we've reached the end of the token stream."""
        return self.i >= len(self.tokens)

    def current(self):
        """Get the current token without consuming it."""
        return self.tokens[self.i] if not self.at_eof() else ("EOF", "")

    def peek_kind(self):
        """Get the type of the current token."""
        return self.current()[0]

    def peek_val(self):
        """Get the value of the current token."""
        return self.current()[1]

    def advance(self):
        """Move to the next token."""
        if not self.at_eof(): 
            self.i += 1

    def eat_kind(self, name):
        """
        Consume a token of a specific type.
        
        Args:
            name (str): Expected token type
            
        Returns:
            tuple: The consumed token
            
        Raises:
            SyntaxError: If the current token doesn't match the expected type
        """
        if self.peek_kind() == name:
            token = self.current()
            self.advance()
            return token
        raise SyntaxError(f"expected kind {name!r}, got {self.current()!r}")

    def eat_val(self, pat):
        """
        Consume a token with a specific value.
        
        Args:
            pat (str): Expected token value
            
        Returns:
            tuple: The consumed token
            
        Raises:
            SyntaxError: If the current token doesn't match the expected value
        """
        if self.peek_val() == pat:
            token = self.current()
            self.advance()
            return token
        raise SyntaxError(f"expected {pat!r}, got {self.current()!r}")

    def parse_call(self):
        """Parse a function call if the current position looks like one."""
        if self.peek_kind() == "ID":
            # Look ahead to see if this is a function call
            if (not self.at_eof() and 
                self.i + 1 < len(self.tokens) and 
                self.tokens[self.i + 1][1] == "("):
                
                name = self.eat_kind("ID")[1]
                self.eat_val("(")
                args = []
                if self.peek_val() != ")":
                    args.append(self.parse_expr())
                    while self.peek_val() == ",":
                        self.eat_val(",")
                        args.append(self.parse_expr())
                self.eat_val(")")
                return Call(name, args)
        return None

    def parse_factor(self):
        """Parse a factor: function call, parenthesized expression, number, variable, or unary operation."""
        # Try function call first
        call = self.parse_call()
        if call:
            return call
            
        if self.peek_val() == "(":
            self.eat_val("(")
            node = self.parse_expr()
            self.eat_val(")")
            return node
        elif self.peek_kind() == "NUM":
            token = self.eat_kind("NUM")
            return Number(token[1])
        elif self.peek_kind() == "ID":
            token = self.eat_kind("ID")
            return Variable(token[1])
        elif self.peek_val() == "not":
            self.eat_val("not")
            operand = self.parse_factor()
            return UnaryOp("not", operand)
        elif self.peek_val() == "-":
            self.eat_val("-")
            operand = self.parse_factor()
            return UnaryOp("-", operand)
        else:
            raise SyntaxError(f"unexpected {self.current()!r} in Factor")

    def parse_power(self):
        """Parse exponentiation (right-associative)."""
        left = self.parse_factor()
        if self.peek_val() == "^":
            op = self.eat_val("^")[1]
            right = self.parse_power()
            return BinOp(left, op, right)
        return left

    def parse_term(self):
        """Parse multiplication, division, and modulo."""
        node = self.parse_power()
        while self.peek_val() in ("*", "/", "%"):
            op = self.eat_val(self.peek_val())[1]
            right = self.parse_power()
            node = BinOp(node, op, right)
        return node

    def parse_expr(self):
        """Parse addition and subtraction."""
        node = self.parse_term()
        while self.peek_val() in ("+", "-"):
            op = self.eat_val(self.peek_val())[1]
            right = self.parse_term()
            node = BinOp(node, op, right)
        return node

    def parse_comparison(self):
        """Parse comparison operators."""
        node = self.parse_expr()
        while self.peek_kind() in ("LT", "GT", "LE", "GE"):
            if self.peek_kind() == "LT":
                op = self.eat_kind("LT")[1]
            elif self.peek_kind() == "GT":
                op = self.eat_kind("GT")[1]
            elif self.peek_kind() == "LE":
                op = self.eat_kind("LE")[1]
            elif self.peek_kind() == "GE":
                op = self.eat_kind("GE")[1]
            right = self.parse_expr()
            node = BinOp(node, op, right)
        return node

    def parse_equality(self):
        """Parse equality operators."""
        node = self.parse_comparison()
        while self.peek_kind() == "EQ":
            op = self.eat_kind("EQ")[1]
            right = self.parse_comparison()
            node = BinOp(node, op, right)
        return node

    def parse_and(self):
        """Parse logical AND."""
        node = self.parse_equality()
        while self.peek_kind() == "AND":
            op = self.eat_kind("AND")[1]
            right = self.parse_equality()
            node = BinOp(node, op, right)
        return node

    def parse_or(self):
        """Parse logical OR."""
        node = self.parse_and()
        while self.peek_kind() == "OR":
            op = self.eat_kind("OR")[1]
            right = self.parse_and()
            node = BinOp(node, op, right)
        return node

    def parse_if(self):
        """Parse if-then-else statements."""
        if self.peek_kind() == "IF":
            self.eat_kind("IF")
            condition = self.parse_or()
            then_branch = None
            else_branch = None
            if self.peek_kind() == "THEN":
                self.eat_kind("THEN")
                then_branch = self.parse_statement()
            if self.peek_kind() == "ELSE":
                self.eat_kind("ELSE")
                else_branch = self.parse_statement()
            return If(condition, then_branch, else_branch)
        else:
            return self.parse_or()

    def parse_assignment(self):
        """Parse variable assignments."""
        if (self.peek_kind() == "ID" and 
            not self.at_eof() and 
            self.i + 1 < len(self.tokens) and 
            self.tokens[self.i + 1][1] == "="):
            
            name = self.eat_kind("ID")[1]
            self.eat_kind("ASSIGN")
            value = self.parse_while()
            return Assignment(name, value)
        else:
            return self.parse_if()

    def parse_while(self):
        """Parse while loops."""
        if self.peek_kind() == "WHILE":
            self.eat_kind("WHILE")
            condition = self.parse_statement()
            self.eat_kind("COLON")
            body = self.parse_statement()
            return While(condition, body)
        else:
            return self.parse_assignment()

    def parse_return(self):
        """Parse return statements."""
        if self.peek_kind() == "RETURN":
            self.eat_kind("RETURN")
            value = self.parse_or()
            return ReturnValue(value)
        else:
            return self.parse_while()

    def parse_function_def(self):
        # Parse a function definition, supporting 'ref' parameter mode
        if self.peek_kind() == "DEF":
            self.eat_kind("DEF")
            name = self.eat_kind("ID")[1]
            self.eat_val("(")
            params = []
            while self.peek_val() != ")":
                is_ref = False
                if self.peek_kind() == "REF":
                    self.eat_kind("REF")
                    is_ref = True
                param_name = self.eat_kind("ID")[1]
                params.append((is_ref, param_name))
                if self.peek_val() == ",":
                    self.eat_val(",")
                else:
                    break
            self.eat_val(")")
            self.eat_kind("COLON")
            # Parse function body (could be multiple statements)
            statements = []
            if self.peek_kind() == "RETURN":
                statements.append(self.parse_return())
            else:
                statements.append(self.parse_assignment())
            while self.peek_val() == ";":
                next_pos = self.i + 1
                if next_pos < len(self.tokens):
                    next_token = self.tokens[next_pos]
                    if next_token[0] == "DEF":
                        break
                    elif (next_token[0] == "ID" and 
                          next_pos + 1 < len(self.tokens) and 
                          self.tokens[next_pos + 1][1] == "("):
                        break
                    else:
                        self.eat_val(";")
                        if not self.at_eof() and self.peek_kind() != "EOF":
                            if self.peek_kind() == "RETURN":
                                statements.append(self.parse_return())
                            else:
                                statements.append(self.parse_assignment())
                        else:
                            break
                else:
                    break
            return FunctionDef(name, params, statements)
        else:
            return self.parse_return()

    def parse_statement(self):
        """Parse any statement type."""
        if self.peek_kind() == "DEF":
            return self.parse_function_def()
        elif self.peek_kind() == "RETURN":
            return self.parse_return()
        elif self.peek_kind() == "WHILE":
            return self.parse_while()
        else:
            return self.parse_assignment()

    def parse(self, src):
        """
        Parse source code into an AST.
        
        Args:
            src (str): Source code to parse
            
        Returns:
            AST node representing the parsed code
        """
        self.tokens = list(lex(src))
        self.i = 0
        
        statements = []
        while not self.at_eof():
            tree = self.parse_statement()
            statements.append(tree)
            
            # If there's a semicolon, consume it and continue
            if self.peek_val() == ";":
                self.eat_val(";")
            else:
                break
        
        # Return Block if multiple statements, single statement otherwise
        if len(statements) == 1:
            return statements[0]
        else:
            return Block(statements)

# Convenience function for external use
def parse(src):
    """
    Parse source code into an AST using a new parser instance.
    
    Args:
        src (str): Source code to parse
        
    Returns:
        AST node representing the parsed code
    """
    parser = Parser()
    return parser.parse(src)
