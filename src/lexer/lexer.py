from lexer.token import Token, KEYWORDS, OPERATORS
from lexer.errors import LexicalError
from lexer.dfa_loader import DFALoader
from lexer.dfa_engine import DFAEngine

class Lexer:
    def __init__(self, dfa_path):
        dfa_data = DFALoader(dfa_path).load()
        self.dfa = DFAEngine(
            dfa_data.start_state,
            dfa_data.final_states,
            dfa_data.transitions
        )

    def tokenize(self, text):
        tokens = []
        current = ""
        line, col = 1, 0
        i = 0
        self.dfa.reset()

        while i < len(text):
            char = text[i]
            col += 1

            # newline
            if char == "\n":
                line += 1
                col = 0
                i += 1
                continue

            success = self.dfa.next_state(char)

            if success:
                current += char
                i += 1
            else:
                if current:
                    token = self.create_token(current, line, col)
                    if token:  
                        tokens.append(token)
                    current = ""
                    self.dfa.reset()
                else:
                    token = self.create_token(char, line, col)
                    if token:
                        tokens.append(token)
                    self.dfa.reset()
                    i += 1

        if current:
            tokens.append(self.create_token(current, line, col))

        return tokens

    def create_token(self, value, line, col):
        v = value.lower()
        if value.isspace():
            return None
        elif v in KEYWORDS:
            token_type = "KEYWORD"
        elif v in OPERATORS:
            token_type = OPERATORS[v]
        elif value.replace(".", "", 1).isdigit():
            token_type = "NUMBER"
        elif value == ";":
            token_type = "SEMICOLON"
        elif value == ",":
            token_type = "COMMA"
        elif value == ".":
            token_type = "DOT"
        elif value == "..":
            token_type = "RANGE_OPERATOR"
        elif value == "(":
            token_type = "LPARENTHESIS"
        elif value == ")":
            token_type = "RPARENTHESIS"
        elif value == "[":
            token_type = "LBRACKET"
        elif value == "]":
            token_type = "RBRACKET"
        elif value == ":":
            token_type = "COLON"
        elif value == ":=":
            token_type = "ASSIGN_OPERATOR"
        elif value in {"+", "-", "*", "/"}:
            token_type = "ARITHMETIC_OPERATOR"
        elif value in {"=", "<>", "<", "<=", ">", ">="}:
            token_type = "RELATIONAL_OPERATOR"
        elif value.startswith("'") and value.endswith("'"):
            inner = value[1:-1]
            token_type = "CHAR_LITERAL" if len(inner) == 1 else "STRING_LITERAL"
        elif value.isidentifier():
            token_type = "IDENTIFIER"
        else:
            token_type = "UNKNOWN"

        return Token(token_type, value, line, col)
