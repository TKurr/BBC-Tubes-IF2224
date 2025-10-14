from lexer.token import Token, KEYWORDS, OPERATORS
from lexer.errors import LexicalError
from lexer.dfa_loader import DFALoader
from lexer.dfa_engine import DFAEngine

class Lexer:
    def __init__(self, dfa_path):
        dfa_data = DFALoader(dfa_path).load()
        self.dfa = DFAEngine(
            dfa_data.start_state, dfa_data.final_states, dfa_data.transitions
        )

    def tokenize(self, text):
        tokens = []
        current = ""
        line, col = 1, 0
        self.dfa.reset()
        i = 0

        while i < len(text):
            char = text[i]
            col += 1

            # biar pindah baris trus balikin ke kolom 0
            if char == "\n":
                line += 1
                col = 0
                i += 1
                continue

            # sekip spasi
            if char.isspace():
                if current:
                    tokens.append(self.create_token(current, line, col))
                    current = ""
                    self.dfa.reset()
                i += 1
                continue

            # handle literal string
            if char == "'":
                string_val = "'"
                i += 1
                while i < len(text):
                    string_val += text[i]
                    if text[i] == "'":
                        break
                    i += 1
                tokens.append(Token("STRING_LITERAL", string_val, line, col))
                current = ""
                self.dfa.reset()
                i += 1
                continue

            success = self.dfa.next_state(char)
            if success:
                current += char
                i += 1
                continue
            else:
                if current:
                    # operasi :=
                    if current == ":" and char == "=":
                        tokens.append(Token("ASSIGN_OPERATOR", ":=", line, col))
                        current = ""
                        self.dfa.reset()
                        i += 1
                        continue
                    # finalisasi current token
                    tokens.append(self.create_token(current, line, col))
                    current = ""
                    self.dfa.reset()
                    continue
                else:
                    # karakter yang gada transisi di rule
                    token = self.create_token(char, line, col)
                    if token.type == "UNKNOWN":
                        raise LexicalError(f"Unexpected character '{char}'", line, col)
                    tokens.append(token)
                    self.dfa.reset()
                    i += 1

        if current:
            tokens.append(self.create_token(current, line, col))
        return tokens

    def create_token(self, value, line, col):
        v = value.lower()

        if v in KEYWORDS:
            token_type = "KEYWORD"
        elif v in OPERATORS:
            token_type = OPERATORS[v]
        elif v.replace(".", "", 1).isdigit():
            token_type = "NUMBER"
        elif value == ";":
            token_type = "SEMICOLON"
        elif value == ",":
            token_type = "COMMA"
        elif value == ".":
            token_type = "DOT"
        elif value == "(":
            token_type = "LPARENTHESIS"
        elif value == ")":
            token_type = "RPARENTHESIS"
        elif value == ":":
            token_type = "COLON"
        elif value == ":=":
            token_type = "ASSIGN_OPERATOR"
        elif value in {"+", "-", "*", "/"}:
            token_type = "ARITHMETIC_OPERATOR"
        elif value in {"=", "<>", "<", "<=", ">", ">="}:
            token_type = "RELATIONAL_OPERATOR"
        elif value.isidentifier():
            token_type = "IDENTIFIER"
        else:
            token_type = "UNKNOWN"

        return Token(token_type, value, line, col)
