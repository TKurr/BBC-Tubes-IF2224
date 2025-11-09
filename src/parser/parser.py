from .parse_error import ParseError
from .parse_node import ParseNode

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos]

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

    def parse_const_declaration(self):
        node = ParseNode("<const-declaration>")
        node.add_child(self.expect("KEYWORD", "konstanta"))
        
        while True:
            node.add_child(self.expect("IDENTIFIER"))
            
            if self.check("RELATIONAL_OPERATOR") and self.current_token.value == "=":
                node.add_child(self.expect("RELATIONAL_OPERATOR"))
            else:
                raise ParseError(f"Expected '=' in constant declaration", self.current_token)
            
            node.add_child(self.parse_expression())
            node.add_child(self.expect("SEMICOLON"))
            
            if not self.check("IDENTIFIER"):
                break
        return node
    
    def parse_type_declaration(self):
        node = ParseNode("<type-declaration>")
        node.add_child(self.expect("KEYWORD", "tipe"))
        
        while True:
            node.add_child(self.expect("IDENTIFIER"))
            
            if self.check("RELATIONAL_OPERATOR") and self.current_token.value == "=":
                node.add_child(self.expect("RELATIONAL_OPERATOR"))
            else:
                raise ParseError(f"Expected '=' in type declaration", self.current_token)
            node.add_child(self.parse_type())
            node.add_child(self.expect("SEMICOLON"))
            
            if not self.check("IDENTIFIER"):
                break
        return node
    
    def parse_var_declaration(self):
        node = ParseNode("<var-declaration>")
        node.add_child(self.expect("KEYWORD", "variabel"))
        
        while True:
            node.add_child(self.parse_identifier_list())
            node.add_child(self.expect("COLON"))
            node.add_child(self.parse_type())
            node.add_child(self.expect("SEMICOLON"))
            
            if not self.check("IDENTIFIER"):
                break
        return node
    
    def parse_subprogram_declaration(self):
        if self.check("KEYWORD", "prosedur"):
            return self.parse_procedure_declaration()
        elif self.check("KEYWORD", "fungsi"):
            return self.parse_function_declaration()
        else:
            raise ParseError(f"Expected 'prosedur' or 'fungsi'", self.current_token)

    def parse_procedure_declaration(self):
        node = ParseNode("<procedure-declaration>")
        node.add_child(self.expect("KEYWORD", "prosedur"))
        node.add_child(self.expect("IDENTIFIER"))
        #parse parameter list
        if self.check("LPARENTHESIS"):
            node.add_child(self.parse_formal_parameter_list())
        node.add_child(self.expect("SEMICOLON"))
        #parse block
        node.add_child(self.parse_block())
        node.add_child(self.expect("SEMICOLON"))
        return node
    
    def parse_function_declaration(self):
        node = ParseNode("<function-declaration>")
        node.add_child(self.expect("KEYWORD", "fungsi"))
        node.add_child(self.expect("IDENTIFIER"))
        #parse parameter list
        if self.check("LPARENTHESIS"):
            node.add_child(self.parse_formal_parameter_list())
        #parse return type
        node.add_child(self.expect("COLON"))
        node.add_child(self.parse_type())
        node.add_child(self.expect("SEMICOLON"))
        #parse block
        node.add_child(self.parse_block())
        node.add_child(self.expect("SEMICOLON"))
        return node
    
    def parse_block(self):
        node = ParseNode("<block>")
        node.add_child(self.parse_declaration_part())
        node.add_child(self.parse_compound_statement())
        return node
    
    def parse_formal_parameter_list(self):
        node = ParseNode("<formal-parameter-list>")
        node.add_child(self.expect("LPARENTHESIS"))
        
        node.add_child(self.parse_parameter_group())
        
        while self.check("SEMICOLON"):
            node.add_child(self.expect("SEMICOLON"))
            node.add_child(self.parse_parameter_group())
        node.add_child(self.expect("RPARENTHESIS"))
        return node

    def parse_parameter_group(self):
        '''Helper function for formal-parameter-list'''
        node = ParseNode("<parameter-group>")
        node.add_child(self.parse_identifier_list())
        node.add_child(self.expect("COLON"))
        node.add_child(self.parse_type())
        return node
    
    # Type / Identifier
    def parse_identifier_list(self):
        '''Identifier, Identifier, Identifier'''
        node = ParseNode("<identifier-list>")
        node.add_child(self.expect("IDENTIFIER"))
        
        while self.check("COMMA"):
            node.add_child(self.expect("COMMA"))
            node.add_child(self.expect("IDENTIFIER"))
        return node
    
    def parse_type(self):
        '''parse variable type'''
        node = ParseNode("<type>")
        
        #array type
        if self.check("KEYWORD", "larik"):
            node.add_child(self.parse_array_type())
            return node
        
        #builtin type
        elif self.check("KEYWORD", "integer") or self.check("KEYWORD", "real") or \
             self.check("KEYWORD", "boolean") or self.check("KEYWORD", "char"):
            node.add_child(self.expect("KEYWORD"))
            return node
        
        #cusom type (identifier)
        if self.check("IDENTIFIER"):
            node.add_child(self.expect("IDENTIFIER"))
            return node
        
        raise ParseError(f"Expected type", self.current_token)
    
    def parse_array_type(self):
        node = ParseNode("<array-type>")
        node.add_child(self.expect("KEYWORD", "larik"))
        node.add_child(self.expect("LBRACKET"))
        node.add_child(self.parse_range())
        node.add_child(self.expect("RBRACKET"))
        node.add_child(self.expect("KEYWORD", "dari"))
        node.add_child(self.parse_type())
        return node
    
    def parse_range(self):
        node = ParseNode("<range>")
        node.add_child(self.parse_expression())
        
        if self.check("RANGE_OPERATOR"):
            node.add_child(self.expect("RANGE_OPERATOR"))
        else:
            raise ParseError("Expected '..' for range", self.current_token)
        
        node.add_child(self.parse_expression())
        return node
    
    # Compound & Statements
    def parse_compound_statement(self):
        node = ParseNode("<compound-statement>")
        node.add_child(self.expect("KEYWORD", "mulai"))
        node.add_child(self.parse_statement_list())
        node.add_child(self.expect("KEYWORD", "selesai"))
        return node

    def parse_kasus_statement(self):
        node = ParseNode("<kasus-statement>")
        node.add_child(self.expect("KEYWORD", "kasus"))
        node.add_child(self.parse_expression())
        node.add_child(self.expect("KEYWORD", "dari"))

        kasus_list = ParseNode("<kasus-list>")

        while True:
            if (self.check("NUMBER") or self.check("CHAR_LITERAL") or self.check("STRING_LITERAL") or \
                self.check("KEYWORD", "true") or self.check("KEYWORD", "false")):
                kasus_list.add_child(self.expect(self.current_token.type))
            else:
                raise ParseError("Expected constant in 'kasus' statement", self.current_token)

            if self.check("COMMA"):
                self.expect("COMMA")
            else:
                kasus_list.add_child(self.expect("COLON"))
                kasus_list.add_child(self.parse_statement())

                if self.check("SEMICOLON"):
                    kasus_list.add_child(self.expect("SEMICOLON"))
                    if not (self.check("NUMBER") or self.check("CHAR_LITERAL") or self.check("STRING_LITERAL") or \
                            self.check("KEYWORD", "true") or self.check("KEYWORD", "false")):
                        break
                else:
                    break

        node.add_child(kasus_list)
        return node

    def parse_statement_list(self):
        '''List of statements parser'''
        node = ParseNode("<statement-list>")
        node.add_child(self.parse_statement())
        
        while self.check("SEMICOLON"):
            node.add_child(self.expect("SEMICOLON"))
            if self.check("KEYWORD", "selesai"):
                break
            node.add_child(self.parse_statement())
        return node

    def parse_statement(self):
        '''Indivdual statement parser'''
        # Statement kosong
        if self.check("SEMICOLON") or self.check("KEYWORD", "selesai"):
            return ParseNode("<empty-statement>")
        # If statement
        if self.check("KEYWORD", "jika"):
            return self.parse_if_statement()
        # While statement
        if self.check("KEYWORD", "selama"):
            return self.parse_while_statement()
        # For statement
        if self.check("KEYWORD", "untuk"):
            return self.parse_for_statement()
        # Repeat statement
        if self.check("KEYWORD", "ulangi"):
            return self.parse_repeat_statement()
        # Compound statement
        if self.check("KEYWORD", "mulai"):
            return self.parse_compound_statement()
        # Kasus statement
        if self.check("KEYWORD", "kasus"):
            return self.parse_kasus_statement()
        # Caller / Assignment statement
        if self.check("IDENTIFIER"):
            next_token = self.peek()
            if next_token and next_token.type == "ASSIGN_OPERATOR":
                return self.parse_assignment_statement()
            else:
                return self.parse_procedure_function_call()
        # Built-in procedure/function
        if self.check("KEYWORD"):
            return self.parse_procedure_function_call()
        
        raise ParseError(f"Unexpected token in statement", self.current_token)

    # Specific statement 
    def parse_assignment_statement(self):
        node = ParseNode("<assignment-statement>")
        node.add_child(self.expect("IDENTIFIER"))
        node.add_child(self.expect("ASSIGN_OPERATOR"))
        node.add_child(self.parse_expression())
        return node

    def parse_if_statement(self):
        node = ParseNode("<if-statement>")
        node.add_child(self.expect("KEYWORD", "jika"))
        node.add_child(self.parse_expression())
        node.add_child(self.expect("KEYWORD", "maka"))
        node.add_child(self.parse_statement())
        
		# parse else
        if self.check("KEYWORD", "selain_itu") or self.check("KEYWORD", "selain-itu"):
            node.add_child(self.expect("KEYWORD"))
            node.add_child(self.parse_statement())
        return node

    def parse_while_statement(self):
        node = ParseNode("<while-statement>")
        node.add_child(self.expect("KEYWORD", "selama"))
        node.add_child(self.parse_expression())
        node.add_child(self.expect("KEYWORD", "lakukan"))
        node.add_child(self.parse_statement())
        return node
    
    def parse_for_statement(self):
        node = ParseNode("<for-statement>")
        node.add_child(self.expect("KEYWORD", "untuk"))
        node.add_child(self.expect("IDENTIFIER"))
        node.add_child(self.expect("ASSIGN_OPERATOR"))
        node.add_child(self.parse_expression())
        
        if self.check("KEYWORD", "ke"):
            node.add_child(self.expect("KEYWORD", "ke"))
        elif self.check("KEYWORD", "turun_ke"):
            node.add_child(self.expect("KEYWORD", "turun_ke"))
        else:
            raise ParseError("Expected 'ke' or 'turun_ke' in for-statement", self.current_token)
       
        node.add_child(self.parse_expression())
        node.add_child(self.expect("KEYWORD", "lakukan"))
        node.add_child(self.parse_statement())
        return node
    
    def parse_repeat_statement(self):
        node = ParseNode("<repeat-statement>")
        node.add_child(self.expect("KEYWORD", "ulangi"))
        stmt_list_node = ParseNode("<statement-list>")
        stmt_list_node.add_child(self.parse_statement())
        
        while self.check("SEMICOLON"):
            stmt_list_node.add_child(self.expect("SEMICOLON"))
            if self.check("KEYWORD", "sampai"):
                break
            stmt_list_node.add_child(self.parse_statement())
        
        node.add_child(stmt_list_node)
        node.add_child(self.expect("KEYWORD", "sampai"))
        node.add_child(self.parse_expression()) 
        return node

    def parse_procedure_function_call(self):
        node = ParseNode("<procedure/function-call>")
        
        if self.check("IDENTIFIER"):
            node.add_child(self.expect("IDENTIFIER"))
        elif self.check("KEYWORD"):
            node.add_child(self.expect("KEYWORD"))
        else:
            raise ParseError(f"Expected procedure/function name", self.current_token)
        
        # Parse parameter list (kalo ada args)
        if self.check("LPARENTHESIS"):
            node.add_child(self.expect("LPARENTHESIS"))
            if not self.check("RPARENTHESIS"):
                node.add_child(self.parse_parameter_list())
            node.add_child(self.expect("RPARENTHESIS"))
            
        return node

    # Parameters
    def parse_parameter_list(self):
        node = ParseNode("<parameter-list>")
        node.add_child(self.parse_expression())
        
        while self.check("COMMA"):
            node.add_child(self.expect("COMMA"))
            node.add_child(self.parse_expression())
        return node

    # Expressions
    def parse_expression(self):
        node = ParseNode("<expression>")
        node.add_child(self.parse_simple_expression())
        
        if self.is_relational_operator():
            node.add_child(self.parse_relational_operator())
            node.add_child(self.parse_simple_expression())
        return node

    def parse_simple_expression(self):
        node = ParseNode("<simple-expression>")
        
        if self.check("ARITHMETIC_OPERATOR") and (self.current_token.value == "+" or self.current_token.value == "-"):
            node.add_child(self.expect("ARITHMETIC_OPERATOR"))
        
        node.add_child(self.parse_term())
        
        while self.is_additive_operator():
            node.add_child(self.parse_additive_operator())
            node.add_child(self.parse_term())
        
        return node

    def parse_term(self):
        '''Multiplicatio operations'''
        node = ParseNode("<term>")
        node.add_child(self.parse_factor())
        
        while self.is_multiplicative_operator():
            node.add_child(self.parse_multiplicative_operator())
            node.add_child(self.parse_factor())
        return node

    def parse_factor(self):
        node = ParseNode("<factor>")
        
        # Number literal
        if self.check("NUMBER"):
            node.add_child(self.expect("NUMBER"))
        
        # String literal
        elif self.check("STRING_LITERAL"):
            node.add_child(self.expect("STRING_LITERAL"))
        
        # Character literal
        elif self.check("CHAR_LITERAL"):
            node.add_child(self.expect("CHAR_LITERAL"))
        
        # Boolean literal (true/false)
        elif self.check("KEYWORD", "true") or self.check("KEYWORD", "false"):
            node.add_child(self.expect("KEYWORD"))
        
        # NOT operator
        elif self.check("LOGICAL_OPERATOR", "tidak") or self.check("KEYWORD", "tidak"):
            if self.check("LOGICAL_OPERATOR"):
                node.add_child(self.expect("LOGICAL_OPERATOR"))
            else:
                node.add_child(self.expect("KEYWORD"))
            node.add_child(self.parse_factor())
        
        # Ekspresi dalam tanda kurung
        elif self.check("LPARENTHESIS"):
            node.add_child(self.expect("LPARENTHESIS"))
            node.add_child(self.parse_expression())
            node.add_child(self.expect("RPARENTHESIS"))
        
        # Identifier (variable atau function/procedure call)
        elif self.check("IDENTIFIER"):
            next_token = self.peek()
            
            if next_token and next_token.type == "LPARENTHESIS":
                node.add_child(self.parse_procedure_function_call())
            else:
                node.add_child(self.expect("IDENTIFIER"))    
        else:
            raise ParseError(f"Unexpected token in factor", self.current_token)
        
        return node
        

    # Operators
    def parse_relational_operator(self):
        if self.check("RELATIONAL_OPERATOR"):
            return self.expect("RELATIONAL_OPERATOR")
        else:
            raise ParseError(f"Expected relational operator", self.current_token)

    def parse_additive_operator(self):
        if self.check("ARITHMETIC_OPERATOR"):
            return self.expect("ARITHMETIC_OPERATOR")
        elif self.check("LOGICAL_OPERATOR", "atau"):
            return self.expect("LOGICAL_OPERATOR")
        else:
            raise ParseError(f"Expected additive operator", self.current_token)
        
    def parse_multiplicative_operator(self):
        if self.check("ARITHMETIC_OPERATOR"):
            return self.expect("ARITHMETIC_OPERATOR")
        elif self.check("LOGICAL_OPERATOR","dan"):
            return self.expect("LOGICAL_OPERATOR","dan")
        else:
            raise ParseError(f"Expected multiplicative operator", self.current_token)
        
    # Helper function 
    
    def is_relational_operator(self):
        if self.current_token is None:
            return False
        return self.check("RELATIONAL_OPERATOR") and self.current_token.value in ["<", ">", "<=", ">=", "=", "<>"]
    
    def is_additive_operator(self):
        if self.current_token is None:
            return False
        return (self.check("ARITHMETIC_OPERATOR") and self.current_token.value in ["+", "-"]) or self.check("LOGICAL_OPERATOR", "atau")
    
    def is_multiplicative_operator(self):
        if self.current_token is None:
            return False
        return (self.check("ARITHMETIC_OPERATOR") and self.current_token.value in ["*", "/","bagi","mod"]) or \
            self.check("LOGICAL_OPERATOR","dan")