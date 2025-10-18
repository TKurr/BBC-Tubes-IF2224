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
            
            if char == "{":
                i += 1
                while i < len(text) and text[i] != "}":
                    if text[i] == "\n":
                        line += 1
                        col = 0
                    i += 1
                i += 1
                continue
            
            if char == "(" and (i + 1) < len(text) and text[i + 1] == "*":
                i += 2
                while i < len(text) - 1:
                    if text[i] == "*" and text[i + 1] == ")":
                        i += 2
                        break
                    if text[i] == "\n":
                        line += 1
                        col = 0
                    i += 1
                continue

            # flush token
            if char == "'" and current:
                tokens.append(self.create_token(current, line, col))
                current = ""
                self.dfa.reset()
                continue

            # handle literal string
            if char == "'":
                literal_val = "'"
                i += 1
                inner = ""
                while i < len(text):
                    literal_val += text[i]
                    if text[i] == "'":
                        break
                    inner += text[i]
                    i += 1
                literal_val += "'"

                if len(inner) == 1:
                    token_type = "CHAR_LITERAL"
                else:
                    token_type = "STRING_LITERAL"

                tokens.append(Token(token_type, inner, line, col))
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
                    # operasi range
                    if current == '.' and char == '.':
                        tokens.append(Token("RANGE_OPERATOR", "..", line, col))
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
        elif value.isidentifier():
            token_type = "IDENTIFIER"
        else:
            token_type = "UNKNOWN"

        return Token(token_type, value, line, col)
