class Token:
    def __init__(self, type_, value, line, column):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        if self.type in {"STRING_LITERAL", "CHAR_LITERAL"} and not self.value.startswith("'"):
            return f"{self.type}('{self.value}')"
        return f"{self.type}({self.value})"

KEYWORDS = {
    "program", "var", "begin", "end", "if", "then", "else", "while", "do", "for",
    "to", "downto", "integer", "real", "boolean", "char", "array", "of",
    "procedure", "function", "const", "type"
}

OPERATORS = {
    "+": "ARITHMETIC_OPERATOR",
    "-": "ARITHMETIC_OPERATOR",
    "*": "ARITHMETIC_OPERATOR",
    "/": "ARITHMETIC_OPERATOR",
    "div": "ARITHMETIC_OPERATOR",
    "mod": "ARITHMETIC_OPERATOR",
    ":=": "ASSIGN_OPERATOR",
    "=": "RELATIONAL_OPERATOR",
    "<": "RELATIONAL_OPERATOR",
    ">": "RELATIONAL_OPERATOR",
    "<=": "RELATIONAL_OPERATOR",
    ">=": "RELATIONAL_OPERATOR",
    "<>": "RELATIONAL_OPERATOR",
    "and": "LOGICAL_OPERATOR",
    "or": "LOGICAL_OPERATOR",
    "not": "LOGICAL_OPERATOR",
}

STATE_TOKEN_MAP = {
    "ID": "IDENTIFIER",
    "NUM": "NUMBER",
    "NUM_REAL": "NUMBER",
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
    "RELATIONAL_OPERATOR": "RELATIONAL_OPERATOR",
    "LESS_THAN": "RELATIONAL_OPERATOR",
    "GREATER_THAN": "RELATIONAL_OPERATOR",
}