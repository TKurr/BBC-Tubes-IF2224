from .token import Token
from .lexical_error import LexicalError
from .lexer_config import LexerConfig
from src.dfa.dfa_engine import DFAEngine
from typing import List

class Lexer:
    '''Core class buat lexical analyzer'''
    def __init__(self, dfa_engine: DFAEngine, config: LexerConfig):
        self.dfa = dfa_engine
        self.config = config
        self.line = 1
        self.column = 1
        self.text = ""
        self.index = 0

    def tokenize(self, text: str) -> List[Token]:
        self.text = text
        tokens: List[Token] = []

        while self.index < len(self.text):
            char = self.text[self.index]
            if char in ' \t':
                self.column += 1
                self.index += 1
                continue
            elif char == '\n':
                self.line += 1
                self.column = 1
                self.index += 1
                continue

            self.dfa.reset_state() 
            current_value = ""
            temp_token = (None, None, -1, -1) # type, value, line, column
            start_col = self.column
            start_line = self.line
            
            temp_index = self.index
            while temp_index < len(self.text):
                char_to_check = self.text[temp_index]
                if not self.dfa.next_state(char_to_check):
                    break
                
                current_value += char_to_check
                
                if self.dfa.last_final_state:
                    temp_token = (current_value, self.dfa.last_final_state, start_line, start_col)
                    
                temp_index += 1

            value, final_state, line, col = temp_token
            if value is None:
                invalid_char = self.text[self.index]
                message = f"Invalid character: '{invalid_char}'"
                error_token = Token("UNKNOWN", invalid_char, self.line, self.column)
                raise LexicalError(error_token, message, self.text)
            
            token = self._create_token(value, final_state, line, col)
            tokens.append(token)
            self.index += len(value)
            self.column += len(value)
            
        return tokens


    def _create_token(self, value: str, final_state: str, line: int, col: int) -> Token:
        token_type = self.config.state_token_map.get(final_state)
        value_lower = value.lower()

		# keyword & operators case insensitive pake lower value buat comparisson
        if token_type == "IDENTIFIER":
            if value_lower in self.config.keywords:
                token_type = "KEYWORD"
            elif value_lower in self.config.operators_map:
                token_type = self.config.operators_map[value_lower]

        return Token(token_type, value, line, col)