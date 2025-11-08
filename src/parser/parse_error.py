class ParseError(Exception):
    def __init__(self, message, token):
        self.message = message
        self.line = token.line
        self.column = token.column
        self.value = token.value
        self.type = token.type
        
    def __str__(self):
        if not self.full_source_text:
            return f"SyntaxError at line {self.line}, column {self.column}: {self.message}"
        lines = self.full_source_text.split('\n')
        error_line = lines[self.line - 1] if 0 < self.line <= len(lines) else ""
        error_line = error_line.rstrip()
        
        line_num_str = str(self.line)
        code_prefix = f" {line_num_str} | "
        empty_prefix = f" {' ' * len(line_num_str)} |"
        caret_prefix = f" {' ' * len(line_num_str)} | "
        caret_padding = " " * max(0, self.column - 1)
        
        return (
			f"SyntaxError: {self.message}\n"
			f"  --> (line {self.line}, column {self.column})\n"
			f"{empty_prefix}\n"
			f"{code_prefix}{error_line}\n"
			f"{caret_prefix}{caret_padding}^"
		)