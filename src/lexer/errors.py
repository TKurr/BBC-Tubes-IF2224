class LexicalError(Exception):
    def __init__(self, message, line, column):
        self.message = message
        self.line = line
        self.column = column

    def __str__(self):
        return f"[LexicalError] {self.message} at line {self.line}, column {self.column}"
