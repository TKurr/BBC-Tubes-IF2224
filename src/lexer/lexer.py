from lexer.token import Token, KEYWORDS, OPERATORS, STATE_TOKEN_MAP
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
                    if not self.dfa.is_accepting():
                        tokens.append(Token("UNKNOWN", current, line, col))
                        print(f"[Error] Invalid token '{current}' at line {line}, col {col}")
                        break
                    else:
                        token = self.create_token(current, line, col)
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

        return tokens

    def create_token(self, value, line, col):
        if value.isspace():
            return None

        state = getattr(self.dfa, "last_final_state", None)
        token_type = None

        if state in self.dfa.final_states:
            token_type = state

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
