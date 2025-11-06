class LexicalError(Exception):
    def __init__(self, token, message):
        self.message = message
        self.line = token.line
        self.column = token.column

    def __str__(self):
        return f"LexicalError at line {self.line}, column {self.column}: {self.message}"
