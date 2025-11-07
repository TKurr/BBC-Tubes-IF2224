class LexicalError(Exception):
    '''Lexical error output'''
    def __init__(self, token, message, full_source_text):
        self.message = message
        self.line = token.line
        self.column = token.column
        self.full_source_text = full_source_text

    def __str__(self):
        if not self.full_source_text:
            return f"LexicalError at line {self.line}, column {self.column}: {self.message}"

        lines = self.full_source_text.split('\n')
        broken_line = lines[self.line - 1].rstrip()
        line_number_str = str(self.line)
        code_prefix = f" {line_number_str} | "
        empty_line_padding = " " * len(line_number_str)
        empty_line_prefix = f" {empty_line_padding} |"
        caret_prefix_padding = " " * len(line_number_str)
        caret_prefix = f" {caret_prefix_padding} | "
        caret_padding = " " * (self.column - 1)

        return (
            f"LexicalError: {self.message}\n"
            f"  --> (line {self.line}, column {self.column})\n"
            f"{empty_line_prefix}\n"
            f"{code_prefix}{broken_line}\n"
            f"{caret_prefix}{caret_padding}^"
        )