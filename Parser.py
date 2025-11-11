# Gambl/Parser.py
# Parsing Logic - Converts tokens to Abstract Syntax Tree
from ast_nodes import Number, Variable, BinOp, UnaryOp, Assignment, If, While, FunctionDef, Call, FunctionValue, ReturnValue, Block, ArrayLiteral, Index, AssignIndex, String
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
    
    def check(self, kind):
        """Return True if the current token is of the given kind."""
        return self.peek_kind() == kind

    def expect(self, kind):
        """Consume a token of the given kind, or raise an error."""
        return self.eat_kind(kind)

    def match(self, kind):
        """If the current token is of the given kind, consume it and return True; else False."""
        if self.check(kind):
            self.eat_kind(kind)
            return True
        return False

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
        # Number literal
        if self.peek_kind() == "NUM":
            return Number(self.eat_kind("NUM")[1])
        # String literal
        if self.peek_kind() == "STRING":
            return String(self.eat_kind("STRING")[1][1:-1])
        # Array literal
        if self.peek_kind() == "LBRACK":
            self.eat_kind("LBRACK")
            items = []
            if self.peek_kind() != "RBRACK":
                items.append(self.parse_expr())
                while self.peek_kind() == "COMMA":
                    self.eat_kind("COMMA")
                    items.append(self.parse_expr())
            self.eat_kind("RBRACK")
            return ArrayLiteral(items)
        # Function call or variable
        if self.peek_kind() == "ID":
            if (not self.at_eof() and
                self.i + 1 < len(self.tokens) and
                self.tokens[self.i + 1][0] == "LPAREN"):
                name = self.eat_kind("ID")[1]
                self.eat_kind("LPAREN")
                args = []
                if self.peek_kind() != "RPAREN":
                    args.append(self.parse_expr())
                    while self.peek_kind() == "COMMA":
                        self.eat_kind("COMMA")
                        args.append(self.parse_expr())
                self.eat_kind("RPAREN")
                return Call(name, args)
            return Variable(self.eat_kind("ID")[1])
        # Parentheses for grouping
        if self.peek_kind() == "LPAREN":
            self.eat_kind("LPAREN")
            expr = self.parse_expr()
            self.eat_kind("RPAREN")
            return expr
        raise SyntaxError(f"Unexpected token: {self.current()}")

    def parse_power(self):
        node = self.parse_factor()
        while self.peek_kind() == "LBRACK":
            self.eat_kind("LBRACK")
            index = self.parse_expr()
            self.eat_kind("RBRACK")
            node = Index(node, index)
        if self.peek_val() == "^":
            op = self.eat_val("^")[1]
            right = self.parse_power()
            return BinOp(node, op, right)
        return node

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

    def parse_array(self):
        items = []
        self.expect('LBRACK')
        if not self.check('RBRACK'):
            items.append(self.parse_expr())
            while self.match('COMMA'):
                items.append(self.parse_expr())
        self.expect('RBRACK')
        return ArrayLiteral(items)
    
    def parse_index(self, base):
        self.expect('LBRACK')
        index = self.parse_expr()
        self.expect('RBRACK')
        return Index(base, index)

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
            right = self.parse_expr()  # ✅ FIXED
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
        # Assignment: a = value or a[expr] = value
        if (self.peek_kind() == "ID" and
            not self.at_eof() and
            self.i + 1 < len(self.tokens) and
            self.tokens[self.i + 1][0] == "ASSIGN"):
            name = self.eat_kind("ID")[1]
            self.eat_kind("ASSIGN")
            value = self.parse_while()
            return Assignment(name, value)
        # Index assignment: a[expr][expr]... = value
        elif (self.peek_kind() == "ID" and
            not self.at_eof() and
            self.i + 1 < len(self.tokens) and
            self.tokens[self.i + 1][0] == "LBRACK"):
            # Parse the full left-hand side as an expression (with all chained indexing)
            lhs = self.parse_expr()
            if self.peek_kind() == "ASSIGN":
                self.eat_kind("ASSIGN")
                expr = self.parse_while()
                # Unpack the left-hand side to get the base and all indices
                # Only support AssignIndex for a single index for now
                if isinstance(lhs, Index):
                    return AssignIndex(lhs.base, lhs.index, expr)
                else:
                    raise SyntaxError("Invalid assignment target")
            else:
                return lhs
        else:
            return self.parse_if()

    def parse_while(self):
        """Parse while loops."""
        if self.peek_kind() == "WHILE":
            self.eat_kind("WHILE")
            condition = self.parse_comparison()
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
