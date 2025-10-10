class Token:
    def __init__(self, type_, value, line, column):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
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
