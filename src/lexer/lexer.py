from .token import Token
from .lexical_error import LexicalError
from .lexer_config import LexerConfig
from src.dfa.dfa_engine import DFAEngine
from typing import List

class Lexer:
    def __init__(self, dfa_engine: DFAEngine, config: LexerConfig):
        self.dfa = dfa_engine
        self.config = config
        self.line = 1
        self.column = 1
        self.text = ""
        self.index = 0

    def _reset_state(self):
        self.line = 1
        self.column = 1
        self.index = 0
        self.text = ""

    def tokenize(self, text: str) -> List[Token]:
        self._reset_state()
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

            self.dfa.reset() 
            current_value = ""
            last_valid_token = (None, None, -1, -1) 
            start_col = self.column
            start_line = self.line
            
            temp_index = self.index
            while temp_index < len(self.text):
                char_to_check = self.text[temp_index]
                if not self.dfa.next_state(char_to_check):
                    break
                
                current_value += char_to_check
                
                if self.dfa.last_final_state:
                    last_valid_token = (current_value, self.dfa.last_final_state, start_line,start_col)
                    
                temp_index += 1

            value, final_state, line, col = last_valid_token
            if value is None:
                raise LexicalError(Token("UNKNOWN", self.text[self.index], self.line, self.column),f"Invalid character or token sequence")
            
            token = self._create_token(value, final_state, line, col)
            tokens.append(token)
            self.index += len(value)
            self.column += len(value)
            
        return tokens


    def _create_token(self, value: str, final_state: str, line: int, col: int) -> Token:
        token_type = self.config.state_token_map.get(final_state)
        value_lower = value.lower()

        if token_type == "IDENTIFIER":
            if value_lower in self.config.keywords:
                token_type = "KEYWORD"
            elif value_lower in self.config.operators_map:
                token_type = self.config.operators_map[value_lower]

        return Token(token_type, value, line, col)