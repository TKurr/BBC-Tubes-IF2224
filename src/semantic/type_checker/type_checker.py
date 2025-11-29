from ..symbol.constants import TypeKind, ObjKind
from ..errors import (
    TypeMismatchError, InvalidOperationError, InvalidArrayIndexError,
    NotAnArrayError, ArgumentTypeError
)

class TypeChecker:
    """Menangani pemeriksaan tipe untuk ekspresi, pernyataan (statements), dan deklarasi"""
    
    def __init__(self):
        self.type_names = {
            TypeKind.INTEGER: "integer",
            TypeKind.REAL: "real",
            TypeKind.BOOLEAN: "boolean",
            TypeKind.CHAR: "char",
            TypeKind.ARRAY: "array",
            TypeKind.RECORD: "record",
            TypeKind.NOTYPE: "notype"
        }
    
    def get_type_name(self, type_kind):
        """Ubah TypeKind menjadi string yang mudah dibaca"""
        return self.type_names.get(type_kind, f"unknown({type_kind})")
    
    def is_numeric_type(self, type_kind):
        """Periksa apakah tipe bersifat numerik (integer atau real)"""
        return type_kind in [TypeKind.INTEGER, TypeKind.REAL]
    
    def is_ordinal_type(self, type_kind):
        """Periksa apakah tipe bersifat ordinal (integer, boolean, char)"""
        return type_kind in [TypeKind.INTEGER, TypeKind.BOOLEAN, TypeKind.CHAR]
    
    def is_compatible(self, type1, type2):
        """Periksa apakah dua tipe kompatibel untuk penugasan (assignment)"""
        # Tipe yang sama selalu kompatibel
        if type1 == type2:
            return True
        
        # Integer dapat ditugaskan ke real
        if type1 == TypeKind.REAL and type2 == TypeKind.INTEGER:
            return True
        
        return False
    
    def check_arithmetic_operation(self, op, left_type, right_type, line=None, column=None):
        """Periksa apakah operasi aritmetika valid untuk tipe yang diberikan. Mengembalikan tipe hasil operasi."""
        # Kedua operand harus numerik
        if not self.is_numeric_type(left_type):
            raise InvalidOperationError(
                op, self.get_type_name(left_type), 
                self.get_type_name(right_type), line, column
            )
        
        if not self.is_numeric_type(right_type):
            raise InvalidOperationError(
                op, self.get_type_name(left_type), 
                self.get_type_name(right_type), line, column
            )
        
        # Operasi bagi (div) dan mod pada integer menghasilkan integer
        if op in ['bagi', 'mod']:
            if left_type != TypeKind.INTEGER or right_type != TypeKind.INTEGER:
                raise TypeMismatchError(
                    "integer", 
                    f"{self.get_type_name(left_type)} and {self.get_type_name(right_type)}",
                    op, line, column
                )
            return TypeKind.INTEGER
        
        # Jika salah satu operand real, hasil adalah real
        if left_type == TypeKind.REAL or right_type == TypeKind.REAL:
            return TypeKind.REAL
        
        # Keduanya integer, hasil integer (kecuali pembagian '/')
        if op == '/':
            return TypeKind.REAL  # Division always returns real in Pascal
        
        return TypeKind.INTEGER
    
    def check_relational_operation(self, op, left_type, right_type, line=None, column=None):
        """Periksa apakah operasi relasional valid untuk tipe yang diberikan. Mengembalikan tipe boolean."""
        # Operator equality bekerja pada tipe apa pun (asal sama)
        if op in ['=', '<>']:
            if left_type != right_type:
                raise TypeMismatchError(
                    self.get_type_name(left_type),
                    self.get_type_name(right_type),
                    f"comparison '{op}'", line, column
                )
            return TypeKind.BOOLEAN
        
        # Operator perbandingan urutan memerlukan tipe ordinal
        if op in ['<', '<=', '>', '>=']:
            if not (self.is_numeric_type(left_type) or left_type == TypeKind.CHAR):
                raise InvalidOperationError(
                    op, self.get_type_name(left_type),
                    self.get_type_name(right_type), line, column
                )
            
            if not (self.is_numeric_type(right_type) or right_type == TypeKind.CHAR):
                raise InvalidOperationError(
                    op, self.get_type_name(left_type),
                    self.get_type_name(right_type), line, column
                )
            
            # Tipe harus compatible
            if left_type != right_type:
                if not (self.is_numeric_type(left_type) and self.is_numeric_type(right_type)):
                    raise TypeMismatchError(
                        self.get_type_name(left_type),
                        self.get_type_name(right_type),
                        f"comparison '{op}'", line, column
                    )
            
            return TypeKind.BOOLEAN
        
        raise InvalidOperationError(op, self.get_type_name(left_type), 
                                   self.get_type_name(right_type), line, column)
    
    def check_logical_operation(self, op, left_type, right_type=None, line=None, column=None):
        """Periksa apakah operasi logika (logical) valid. Mengembalikan tipe boolean."""
        # Unary not
        if op in ['tidak', 'not'] and right_type is None:
            if left_type != TypeKind.BOOLEAN:
                raise TypeMismatchError(
                    "boolean", self.get_type_name(left_type),
                    f"unary '{op}'", line, column
                )
            return TypeKind.BOOLEAN
        
        # Operator biner and / or
        if op in ['dan', 'and', 'atau', 'or']:
            if left_type != TypeKind.BOOLEAN:
                raise TypeMismatchError(
                    "boolean", self.get_type_name(left_type),
                    f"logical '{op}'", line, column
                )
            if right_type != TypeKind.BOOLEAN:
                raise TypeMismatchError(
                    "boolean", self.get_type_name(right_type),
                    f"logical '{op}'", line, column
                )
            return TypeKind.BOOLEAN
        
        raise InvalidOperationError(op, self.get_type_name(left_type),
                                   self.get_type_name(right_type) if right_type else None,
                                   line, column)
    
    def check_unary_operation(self, op, operand_type, line=None, column=None):
        """Periksa apakah operasi unary valid. Mengembalikan tipe hasil."""
        # Unary + dan -
        if op in ['+', '-']:
            if not self.is_numeric_type(operand_type):
                raise InvalidOperationError(
                    f"unary {op}", self.get_type_name(operand_type),
                    None, line, column
                )
            return operand_type
        
        # Unary not
        if op in ['tidak', 'not']:
            return self.check_logical_operation(op, operand_type, None, line, column)
        
        raise InvalidOperationError(f"unary {op}", self.get_type_name(operand_type),
                                   None, line, column)
    
    def check_assignment(self, target_type, value_type, line=None, column=None):
        """Periksa apakah penugasan (assignment) valid"""
        if not self.is_compatible(target_type, value_type):
            raise TypeMismatchError(
                self.get_type_name(target_type),
                self.get_type_name(value_type),
                "assignment", line, column
            )
    
    def check_array_index(self, index_type, line=None, column=None):
        """Periksa apakah indeks array valid (harus integer)"""
        if index_type != TypeKind.INTEGER:
            raise InvalidArrayIndexError(
                self.get_type_name(index_type), line, column
            )
    
    def check_condition(self, condition_type, context="condition", line=None, column=None):
        """Periksa apakah ekspresi kondisi bertipe boolean"""
        if condition_type != TypeKind.BOOLEAN:
            raise TypeMismatchError(
                "boolean", self.get_type_name(condition_type),
                context, line, column
            )
    
    def check_for_loop_bounds(self, var_type, start_type, end_type, line=None, column=None):
        """Periksa apakah batas for-loop valid"""
        # Variabel loop harus ordinal
        if not self.is_ordinal_type(var_type):
            raise TypeMismatchError(
                "ordinal type (integer, boolean, or char)",
                self.get_type_name(var_type),
                "for loop variable", line, column
            )
        
        # Nilai awal dan akhir harus cocok dengan tipe variabel loop
        if start_type != var_type:
            raise TypeMismatchError(
                self.get_type_name(var_type),
                self.get_type_name(start_type),
                "for loop start value", line, column
            )
        
        if end_type != var_type:
            raise TypeMismatchError(
                self.get_type_name(var_type),
                self.get_type_name(end_type),
                "for loop end value", line, column
            )
    
    def get_result_type(self, op, left_type, right_type, line=None, column=None):
        """Dapatkan tipe hasil dari operasi biner, menggabungkan seluruh pemeriksaan tipe operasi."""
        # Operator aritmetika
        if op in ['+', '-', '*', '/', 'bagi', 'mod']:
            return self.check_arithmetic_operation(op, left_type, right_type, line, column)
        
        # Operator relasional
        if op in ['=', '<>', '<', '<=', '>', '>=']:
            return self.check_relational_operation(op, left_type, right_type, line, column)
        
        # Operator logika
        if op in ['dan', 'and', 'atau', 'or']:
            return self.check_logical_operation(op, left_type, right_type, line, column)
        
        raise InvalidOperationError(op, self.get_type_name(left_type),
                                   self.get_type_name(right_type), line, column)
