from .parse_error import ParseError
from .parse_node import ParseNode

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0]

    # ========== Utility ==========
    def advance(self):
        '''Advance 1 offset dari tokens list'''
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None
            
    def peek(self, offset=1):
        '''Melihat token selanjutnya tanpa consume'''
        peek_pos = self.pos + offset
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return None
    
    def expect(self, expected_type, expected_value=None):
        '''Expected token untuk suatu aturan produksi'''
        token = self.current_token
        if token is None:
            raise ParseError(f"Unexpected end of input, expected {expected_type}", self.tokens[-1])

        if token.type != expected_type:
            raise ParseError(f"Unexpected token {token.type}({token.value}), expected {expected_type}", token)

        if expected_value and token.value.lower() != expected_value.lower():
            raise ParseError(f"Unexpected value '{token.value}', expected '{expected_value}'", token)

        self.advance()
        return token
    
    def check(self, expected_type, expected_value=None):
        '''Compare current token with type and/or value'''
        if self.current_token is None:
            return False
        if self.current_token.type != expected_type:
            return False
        if expected_value and self.current_token.value.lower() != expected_value.lower():
            return False
        return True
    
     # ========= Parse rules =========
    def parse(self):
        '''Main function caller'''
        node = self.parse_program()
        if self.current_token is not None:
            raise ParseError(f"Unexpected token {self.current_token.type}({self.current_token.value})", self.current_token)
        return node
    
	# Root
    def parse_program(self):
        '''Root node parse'''
        node = ParseNode("<program>")
        node.add_child(self.parse_program_header())
        node.add_child(self.parse_declaration_part())
        node.add_child(self.parse_compound_statement())
        node.add_child(self.expect("DOT"))
        return node

	# Header
    def parse_program_header(self):
        '''Header node parse'''
        node = ParseNode("<program-header>")
        node.add_child(self.expect("KEYWORD","program"))
        node.add_child(self.expect("IDENTIFIER"))
        node.add_child(self.expect("SEMICOLON"))
        return node

	# Declaration rules
    def parse_declaration_part(self):
        '''Strict urutan initialization dari pascal-s'''
        node = ParseNode("<declaration-part>")
        while self.check("KEYWORD", "konstanta"):
            node.add_child(self.parse_const_declaration())
        while self.check("KEYWORD", "tipe"):
            node.add_child(self.parse_type_declaration())
        while self.check("KEYWORD", "variabel"):
            node.add_child(self.parse_var_declaration())
        while self.check("KEYWORD", "prosedur") or self.check("KEYWORD", "fungsi"):
            node.add_child(self.parse_subprogram_declaration())
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
        node.add_child(self.parse_statement_list())
        return node

    def parse_statement_list(self): 
        node = ParseNode("<statement-list>")
        node.add_child(self.parse_statement())
    
        while self.current_token.type == "SEMICOLON":
            self.advance()
            node.add_child(self.parse_statement())
        return node

    def parse_statement(self):
        t = self.current_token

        if t.value.lower() == "jika":
            return self.parse_if_statement()
        elif t.value.lower() == "selama":
            return self.parse_while_statement()
        elif t.value.lower() == "untuk":
            return self.parse_for_statement()
        elif t.value.lower() == "mulai":
            return self.parse_compound_statement()
        elif t.type == "IDENTIFIER":
            return self.parse_assignment_or_procedure_call()
        else:
            raise ParseError(f"Unexpected token {t.type}({t.value}) in statement", t)

    # Specific statement types
    def parse_assignment_statement(self):
        token = self.expect("IDENTIFIER")

        if self.current_token and self.current_token.type == "ASSIGN":
            node = ParseNode("<assignment-statement>")
            node.add_child(self.parse_expression())
            node.add_child(self.expect("SEMICOLON"))
        elif self.current_token and self.current_token.type == "LPARENTHESIS":
            node.add_child(token)
            node.add_child(self.expect("LPARENTHESIS"))
            if self.current_token and self.current_token.type == "RPARENTHESIS":
                node.add_child(self.parse_parameter_list())
            node.add_child(self.expect("RPARENTHESIS"))
        return node

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