class SemanticError(Exception):
# Kelas dasar untuk semua error semantik
    def __init__(self, message, line=None, column=None):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self.format_message())
    
    def format_message(self):
        if self.line and self.column:
            return f"Semantic error at line {self.line}, column {self.column}: {self.message}"
        elif self.line:
            return f"Semantic error at line {self.line}: {self.message}"
        return f"Semantic error: {self.message}"

class UndeclaredIdentifierError(SemanticError):
# Dilempar ketika sebuah identifier digunakan tetapi belum dideklarasikan
    def __init__(self, identifier, line=None, column=None):
        message = f"Undeclared identifier '{identifier}'"
        super().__init__(message, line, column)

class RedeclaredIdentifierError(SemanticError):
# Raised when an identifier is declared multiple times in the same scope
    def __init__(self, identifier, line=None, column=None):
        message = f"Identifier '{identifier}' is already declared in this scope"
        super().__init__(message, line, column)

class TypeMismatchError(SemanticError):
# Dilempar ketika tipe tidak cocok dalam operasi atau penugasan
    def __init__(self, expected, actual, operation=None, line=None, column=None):
        if operation:
            message = f"Type mismatch in {operation}: expected {expected}, got {actual}"
        else:
            message = f"Type mismatch: expected {expected}, got {actual}"
        super().__init__(message, line, column)

class InvalidOperationError(SemanticError):
# Dilempar ketika sebuah operasi tidak valid untuk tipe yang diberikan
    def __init__(self, operation, type1, type2=None, line=None, column=None):
        if type2:
            message = f"Invalid operation '{operation}' for types {type1} and {type2}"
        else:
            message = f"Invalid operation '{operation}' for type {type1}"
        super().__init__(message, line, column)

class InvalidArrayIndexError(SemanticError):
# Dilempar ketika indeks array bukan integer
    def __init__(self, actual_type, line=None, column=None):
        message = f"Array index must be integer, got {actual_type}"
        super().__init__(message, line, column)

class NotAnArrayError(SemanticError):
# Dilempar ketika mencoba mengindeks variabel yang bukan array
    def __init__(self, identifier, actual_type, line=None, column=None):
        message = f"'{identifier}' is not an array (type: {actual_type})"
        super().__init__(message, line, column)

class NotAFunctionError(SemanticError):
# Dilempar ketika mencoba memanggil identifier yang bukan fungsi
    def __init__(self, identifier, line=None, column=None):
        message = f"'{identifier}' is not a function"
        super().__init__(message, line, column)

class NotAProcedureError(SemanticError):
# Dilempar ketika mencoba memanggil identifier yang bukan prosedur
    def __init__(self, identifier, line=None, column=None):
        message = f"'{identifier}' is not a procedure"
        super().__init__(message, line, column)

class ArgumentCountError(SemanticError):
# Dilempar ketika pemanggilan fungsi/prosedur memiliki jumlah argumen yang salah
    def __init__(self, expected, actual, name, line=None, column=None):
        message = f"'{name}' expects {expected} arguments, got {actual}"
        super().__init__(message, line, column)

class ArgumentTypeError(SemanticError):
# Dilempar ketika argumen fungsi/prosedur memiliki tipe yang salah
    def __init__(self, param_name, expected, actual, line=None, column=None):
        message = f"Argument '{param_name}' expects type {expected}, got {actual}"
        super().__init__(message, line, column)

class InvalidAssignmentError(SemanticError):
# Dilempar ketika mencoba melakukan assignment ke konstanta atau entitas yang tidak dapat diubah
    def __init__(self, identifier, reason=None, line=None, column=None):
        if reason:
            message = f"Cannot assign to '{identifier}': {reason}"
        else:
            message = f"Cannot assign to '{identifier}'"
        super().__init__(message, line, column)

class ReturnTypeMismatchError(SemanticError):
# Dilempar ketika tipe hasil fungsi tidak cocok dengan deklarasinya
    def __init__(self, function_name, expected, actual, line=None, column=None):
        message = f"Function '{function_name}' expects return type {expected}, got {actual}"
        super().__init__(message, line, column)

class MissingReturnError(SemanticError):
# Dilempar ketika fungsi tidak memiliki penugasan nilai ke namanya (return implisit Pascal)
    def __init__(self, function_name, line=None, column=None):
        message = f"Function '{function_name}' must assign a value to its name"
        super().__init__(message, line, column)
