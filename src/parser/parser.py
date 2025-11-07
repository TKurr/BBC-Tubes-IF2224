from .parse_error import ParseError
from .parse_node import ParseNode

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0]

    # ========== Utility ==========
    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    # ========= Parse rules =========
    def expect(self, expected_type, expected_value=None):
        token = self.current_token
        if token is None:
            raise ParseError(f"Unexpected end of input, expected {expected_type}", self.tokens[-1])

        if token.type != expected_type:
            raise ParseError(f"Unexpected token {token.type}({token.value}), expected {expected_type}", token)

        if expected_value and token.value.lower() != expected_value.lower():
            raise ParseError(f"Unexpected value '{token.value}', expected '{expected_value}'", token)

        self.advance()
        return token
    
    # Main Func
    def parse(self):
        node = self.parse_program()
        if self.current_token is not None:
            raise ParseError(f"Unexpected token {self.current_token.type}({self.current_token.value})", self.current_token)
        return node

    # Root
    def parse_program(self):
        node = ParseNode("<program>")
        node.add_child(self.parse_program_header())
        node.add_child(self.parse_declaration_part())
        node.add_child(self.parse_compound_statement())
        node.add(self.expect("DOT"))
        return node


    # Kerjain disini
    def parse_program_header(self):
        node = ParseNode("<program-header>")
        node.add_child(self.expect("KEYWORD"))
        node.add_child(self.expect("IDENTIFIER"))
        node.add_child(self.expect("SEMICOLON"))
        return node

    # Declaration rules
    def parse_declaration_part(self):
        node = ParseNode("<declaration-part>")
        return node

    def parse_const_declaration(self): pass
    def parse_type_declaration(self): pass
    def parse_var_declaration(self): pass
    def parse_subprogram_declaration(self): pass

    # Type / Identifier helpers
    def parse_identifier_list(self): pass
    def parse_type(self): pass
    def parse_array_type(self): pass
    def parse_range(self): pass

    # Compound & Statements
    def parse_compound_statement(self):
        node = ParseNode("<compound-statement>")
        # node.add_child(self.expect("KEYWORD", "mulai"))
        # node.add_child(self.parse_statement_list())
        # node.add_child(self.expect("KEYWORD", "selesai"))
        return node

    def parse_statement_list(self): pass
    def parse_statement(self): pass

    # Specific statement types
    def parse_assignment_statement(self): pass
    def parse_if_statement(self): pass
    def parse_while_statement(self): pass
    def parse_for_statement(self): pass
    def parse_procedure_function_call(self): pass

    # Parameters
    def parse_formal_parameter_list(self): pass
    def parse_parameter_list(self): pass

    # Expressions
    def parse_expression(self): pass
    def parse_simple_expression(self): pass
    def parse_term(self): pass
    def parse_factor(self): pass
    def parse_function_call(self): pass

    # Operators
    def parse_relational_operator(self): pass
    def parse_additive_operator(self): pass
    def parse_multiplicative_operator(self): pass