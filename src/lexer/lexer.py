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
                        if token.type == "UNKNOWN":
                            tokens.append(token)
                            print(f"[Error] Unknown token '{token.value}' at line {line}, col {col}")
                            break
                        tokens.append(token)
                    current = ""
                    self.dfa.reset()
                else:
                    token = self.create_token(char, line, col)
                    if token:
                        if token.type == "UNKNOWN":
                            tokens.append(token)
                            print(f"[Error] Unknown token '{token.value}' at line {line}, col {col}")
                            break
                        tokens.append(token)
                    self.dfa.reset()
                    i += 1

        if current:
            tokens.append(self.create_token(current, line, col))

        return tokens

    def create_token(self, value, line, col):
        if value.isspace():
            return None

        state = getattr(self.dfa, "last_final_state", None)
        token_type = None

        if state in self.dfa.final_states:
            token_type = state

        STATE_TOKEN_MAP = {
            "ID": "IDENTIFIER",
            "NUM": "NUMBER",
            "ASSIGN": "ASSIGN_OPERATOR",
            "ARITHMETIC_OPERATOR": "ARITHMETIC_OPERATOR",
            "STRING_LITERAL": "STRING_LITERAL",
            "CHAR_LITERAL": "CHAR_LITERAL",
            "SEMICOLON": "SEMICOLON",
            "COMMA": "COMMA",
            "DOT": "DOT",
            "RANGE_OPERATOR": "RANGE_OPERATOR",
            "COLON": "COLON",
            "LPARENTHESIS": "LPARENTHESIS",
            "RPARENTHESIS": "RPARENTHESIS",
            "LBRACKET": "LBRACKET",
            "RBRACKET": "RBRACKET",
            "EQUAL": "RELATIONAL_OPERATOR",
            "LESS_THAN": "RELATIONAL_OPERATOR",
            "GREATER_THAN": "RELATIONAL_OPERATOR",
            "LESS_EQUAL": "RELATIONAL_OPERATOR",
            "GREATER_EQUAL": "RELATIONAL_OPERATOR",
            "NOT_EQUAL": "RELATIONAL_OPERATOR"
        }

        if token_type in STATE_TOKEN_MAP:
            token_type = STATE_TOKEN_MAP[token_type]

        v = value.lower()

        if v in OPERATORS:
            token_type = OPERATORS[v]

        elif v in KEYWORDS:
            token_type = "KEYWORD"

        elif token_type is None and v.isidentifier():
            token_type = "IDENTIFIER"

        if token_type is None:
            token_type = "UNKNOWN"

        return Token(token_type, value, line, col)
