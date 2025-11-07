class ParseError(Exception):
    def __init__(self, message, token):
        self.message = message
        self.line = token.line
        self.column = token.column
        self.value = token.value
        self.type = token.type

    def __str__(self):
        return f"Syntax error at line {self.line}, column {self.column}: {self.message}"
