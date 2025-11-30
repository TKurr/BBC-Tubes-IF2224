from .symbol.constants import TypeKind
from .errors import (
    SemanticError, TypeMismatchError, InvalidOperationError
)


class StringOperationError(SemanticError):
    def __init__(self, operation, message, line=None, column=None):
        full_message = f"Invalid string operation '{operation}': {message}"
        super().__init__(full_message, line, column)


class StringHandler:
    VALID_STRING_OPERATORS = {
        '+',
        '=',
        '<>',
        '<', '<=', '>', '>='
    }
    
    STRING_BUILTINS = {
        'length', 'panjang',
        'concat', 'gabung',
        'copy', 'salin',
        'pos', 'posisi',
        'upcase', 'huruf_besar',
        'lowcase', 'huruf_kecil',
        'chr', 'karakter',
        'ord', 'urutan',
    }
    
    def __init__(self):
        self.type_names = {
            TypeKind.STRING: "string",
            TypeKind.CHAR: "char",
            TypeKind.INTEGER: "integer"
        }
    
    def get_type_name(self, type_kind):
        return self.type_names.get(type_kind, f"unknown({type_kind})")
    
    def is_string_type(self, type_kind):
        return type_kind in [TypeKind.STRING, TypeKind.CHAR]
    
    def is_string_compatible(self, type1, type2):
        if type1 == TypeKind.STRING and type2 == TypeKind.STRING:
            return True
        if type1 == TypeKind.CHAR and type2 == TypeKind.CHAR:
            return True
        if self.is_string_type(type1) and self.is_string_type(type2):
            return True
        return False
    
    def check_string_operation(self, op, left_type, right_type, line=None, column=None):
        if op not in self.VALID_STRING_OPERATORS:
            raise StringOperationError(
                op, f"operator '{op}' tidak didukung untuk tipe string",
                line, column
            )
        
        # Konkatenasi dengan +
        if op == '+':
            return self._check_concatenation(left_type, right_type, line, column)
        
        # Operasi perbandingan
        if op in ['=', '<>', '<', '<=', '>', '>=']:
            return self._check_string_comparison(op, left_type, right_type, line, column)
        
        raise StringOperationError(
            op, "operasi tidak dikenali", line, column
        )
    
    def _check_concatenation(self, left_type, right_type, line=None, column=None):
        if not self.is_string_type(left_type):
            raise TypeMismatchError(
                "string atau char", self.get_type_name(left_type),
                "konkatenasi string", line, column
            )
        
        if not self.is_string_type(right_type):
            raise TypeMismatchError(
                "string atau char", self.get_type_name(right_type),
                "konkatenasi string", line, column
            )
        
        # Hasil konkatenasi selalu string
        return TypeKind.STRING
    
    def _check_string_comparison(self, op, left_type, right_type, line=None, column=None):
        if not self.is_string_type(left_type):
            raise TypeMismatchError(
                "string atau char", self.get_type_name(left_type),
                f"perbandingan string '{op}'", line, column
            )
        
        if not self.is_string_type(right_type):
            raise TypeMismatchError(
                "string atau char", self.get_type_name(right_type),
                f"perbandingan string '{op}'", line, column
            )
        
        # Hasil perbandingan adalah boolean
        return TypeKind.BOOLEAN
    
    def check_string_assignment(self, target_type, value_type, line=None, column=None):
        if target_type == TypeKind.STRING:
            if value_type in [TypeKind.STRING, TypeKind.CHAR]:
                return True
            raise TypeMismatchError(
                "string atau char", self.get_type_name(value_type),
                "assignment string", line, column
            )
        
        if target_type == TypeKind.CHAR:
            if value_type == TypeKind.CHAR:
                return True
            # Char hanya bisa diassign dari char
            raise TypeMismatchError(
                "char", self.get_type_name(value_type),
                "assignment char", line, column
            )
        
        return False
    
    def check_string_index(self, index_type, line=None, column=None):
        if index_type != TypeKind.INTEGER:
            raise TypeMismatchError(
                "integer", self.get_type_name(index_type),
                "indeks string", line, column
            )
        return TypeKind.CHAR
    
    def get_builtin_return_type(self, func_name, arg_types):
        func_name_lower = func_name.lower()
        
        if func_name_lower in ['length', 'panjang']:
            if len(arg_types) == 1 and self.is_string_type(arg_types[0]):
                return TypeKind.INTEGER
            return None
        
        if func_name_lower in ['concat', 'gabung']:
            if all(self.is_string_type(t) for t in arg_types):
                return TypeKind.STRING
            return None
        
        if func_name_lower in ['copy', 'salin']:
            if len(arg_types) == 3:
                if (self.is_string_type(arg_types[0]) and 
                    arg_types[1] == TypeKind.INTEGER and 
                    arg_types[2] == TypeKind.INTEGER):
                    return TypeKind.STRING
            return None
        
        if func_name_lower in ['pos', 'posisi']:
            if len(arg_types) == 2:
                if self.is_string_type(arg_types[0]) and self.is_string_type(arg_types[1]):
                    return TypeKind.INTEGER
            return None
        
        if func_name_lower in ['upcase', 'huruf_besar', 'lowcase', 'huruf_kecil']:
            if len(arg_types) == 1 and self.is_string_type(arg_types[0]):
                return arg_types[0]  # Return same type
            return None
        
        if func_name_lower in ['chr', 'karakter']:
            if len(arg_types) == 1 and arg_types[0] == TypeKind.INTEGER:
                return TypeKind.CHAR
            return None
        
        if func_name_lower in ['ord', 'urutan']:
            if len(arg_types) == 1 and arg_types[0] == TypeKind.CHAR:
                return TypeKind.INTEGER
            return None
        
        return None
    
    def is_string_builtin(self, func_name):
        return func_name.lower() in self.STRING_BUILTINS
