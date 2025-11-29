from .symbol.symbol_table import SymbolTable
from .symbol.constants import TypeKind, ObjKind
from .type_checker import TypeChecker
from .errors import (
    SemanticError, UndeclaredIdentifierError, RedeclaredIdentifierError,
    TypeMismatchError, InvalidOperationError, NotAnArrayError,
    NotAFunctionError, NotAProcedureError, ArgumentCountError,
    ArgumentTypeError, InvalidAssignmentError, MissingReturnError
)
from .AST.nodes import *

class SemanticAnalyzer:
    
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.type_checker = TypeChecker()
        self.errors = []
        self.current_function = None  # Lacak fungsi saat ini untuk pemeriksaan tipe kembalian
        
        # Prosedur dan fungsi bawaan (built-in)
        self.builtins = {
            'writeln', 'write', 'readln', 'read',
            'tulis', 'baca',  # Indonesian equivalents
        }
    
    def analyze(self, ast_root):
        try:
            self.visit(ast_root)
            if self.errors:
                return False, self.errors
            return True, []
        except SemanticError as e:
            self.errors.append(e)
            return False, self.errors
    
    def report_error(self, error):
        self.errors.append(error)
    
    def visit(self, node):
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node):
        for child in getattr(node, 'children', []):
            if child:
                self.visit(child)
    
    # ========== Struktur Program ==========
    
    def visit_ProgramNode(self, node):
        # Nama program tidak disimpan di tabel simbol pada implementasi ini
        # Hanya proses deklarasi dan blok utama
        
        # Kunjungi bagian deklarasi
        if node.declarations:
            for decl in node.declarations:
                self.visit(decl)
        
        # Kunjungi blok utama
        if node.block:
            self.visit(node.block)
    
    def visit_BlockNode(self, node):
        """Kunjungi blok (compound statement)"""
        for statement in node.statements:
            if statement:
                self.visit(statement)
    
    def visit_DeclarationsNode(self, node):
        """Kunjungi node deklarasi"""
        for decl in node.declarations:
            if decl:
                self.visit(decl)
    
    # ========== Deklarasi ==========
    
    def visit_ConstDeclNode(self, node):
        """Kunjungi deklarasi konstanta"""
        # Periksa apakah sudah dideklarasikan di scope saat ini
        existing = self.symbol_table.lookup_current_scope(node.name)
        if existing:
            self.report_error(RedeclaredIdentifierError(node.name))
            return
        
        # Tentukan tipe dari ekspresi nilai konstanta
        type_kind = TypeKind.NOTYPE
        if node.consttype:
            # Kunjungi ekspresi untuk memperoleh tipenya
            type_kind = self.visit(node.consttype)
        
        # Tambahkan ke tabel simbol
        self.symbol_table.add_constant(node.name, type_kind, None)
    
    def visit_VarDeclNode(self, node):
        """Kunjungi deklarasi variabel"""
        # Periksa apakah sudah dideklarasikan di scope saat ini
        existing = self.symbol_table.lookup_current_scope(node.name)
        if existing:
            self.report_error(RedeclaredIdentifierError(node.name))
            return
        
        # Tentukan tipe
        if hasattr(node.vartype, '__class__') and node.vartype.__class__.__name__ == 'ArrayTypeNode':
            # Tangani tipe array - simpan tipe elemen untuk diambil nanti
            base_type = self._get_type_kind(node.vartype.base_type)
            var_idx = self.symbol_table.add_variable(node.name, TypeKind.ARRAY)
            # Simpan info array di ATAB
            if hasattr(node.vartype, 'bounds') and len(node.vartype.bounds) >= 2:
                low = node.vartype.bounds[0].value if hasattr(node.vartype.bounds[0], 'value') else 1
                high = node.vartype.bounds[1].value if hasattr(node.vartype.bounds[1], 'value') else 10
                self.symbol_table.add_array_info(
                    xtyp=TypeKind.ARRAY,
                    etyp=base_type,
                    low=low,
                    high=high,
                    elsz=1
                )
                # Simpan referensi ke tabel array di TAB
                if var_idx >= 0 and var_idx < len(self.symbol_table.tab):
                    self.symbol_table.tab[var_idx]['ref'] = len(self.symbol_table.atab) - 1
        else:
            type_kind = self._get_type_kind(node.vartype)
            self.symbol_table.add_variable(node.name, type_kind)
    
    def visit_TypeDeclarationNode(self, node):
        """Kunjungi deklarasi tipe"""
        # Periksa apakah sudah dideklarasikan di scope saat ini
        existing = self.symbol_table.lookup_current_scope(node.name)
        if existing:
            self.report_error(RedeclaredIdentifierError(node.name))
            return
        
        # Ambil jenis tipe dari node tipe
        type_kind = self._resolve_type_node(node.type_node)
        
        # Tambahkan ke tabel simbol
        self.symbol_table.add_type(node.name, type_kind)
    
    def visit_ProcedureDeclNode(self, node):
        """Kunjungi deklarasi prosedur"""
        # Periksa apakah sudah dideklarasikan di scope saat ini
        existing = self.symbol_table.lookup_current_scope(node.name)
        if existing:
            self.report_error(RedeclaredIdentifierError(node.name))
            return
        
        # Tambahkan prosedur ke tabel simbol
        proc_idx = self.symbol_table.add_procedure(node.name, ObjKind.PROCEDURE)
        
        # Masuk ke scope prosedur
        block_idx = self.symbol_table.enter_scope()
        
        # Kaitkan entri prosedur ke bloknya
        if proc_idx >= 0 and proc_idx < len(self.symbol_table.tab):
            self.symbol_table.tab[proc_idx]['ref'] = block_idx
        
        # Tambahkan parameter
        if node.params:
            for param in node.params:
                self.visit(param)
        
        # Kunjungi badan prosedur
        if node.block:
            self.visit(node.block)
        
        # Keluar dari scope prosedur
        self.symbol_table.exit_scope()
    
    def visit_FunctionDeclNode(self, node):
        """Kunjungi deklarasi fungsi"""
        # Periksa apakah sudah dideklarasikan di scope saat ini
        existing = self.symbol_table.lookup_current_scope(node.name)
        if existing:
            self.report_error(RedeclaredIdentifierError(node.name))
            return
        
        # Ambil tipe kembalian
        return_type = self._get_type_kind(node.return_type)
        
        # Tambahkan fungsi ke tabel simbol
        func_idx = self.symbol_table.add_procedure(node.name, ObjKind.FUNCTION)
        
        # Perbarui entri fungsi dengan tipe kembalian
        self.symbol_table.tab[func_idx]['type'] = return_type
        
        # Lacak fungsi saat ini untuk pemeriksaan return
        prev_function = self.current_function
        self.current_function = (node.name, return_type)
        
        # Masuk ke scope fungsi
        block_idx = self.symbol_table.enter_scope()
        
        # Kaitkan entri fungsi ke bloknya
        if func_idx >= 0 and func_idx < len(self.symbol_table.tab):
            self.symbol_table.tab[func_idx]['ref'] = block_idx
        
        # Tambahkan parameter
        if node.params:
            for param in node.params:
                self.visit(param)
        
        # Kunjungi badan fungsi
        if node.block:
            self.visit(node.block)
        
        # Keluar dari scope fungsi
        self.symbol_table.exit_scope()
        
        # Kembalikan fungsi sebelumnya
        self.current_function = prev_function
    
    def visit_ParamNode(self, node):
        """Kunjungi node parameter"""
        type_kind = self._get_type_kind(node.type_node)
        
        for name in node.names:
            self.symbol_table.add_parameter(name, type_kind)
    
    # ========== Pernyataan (Statements) ==========
    
    def visit_AssignNode(self, node):
        """Kunjungi pernyataan assignment"""
        # Periksa target ada dan dapat di-assign
        if isinstance(node.target, VarNode):
            symbol = self.symbol_table.lookup(node.target.name)
            if not symbol:
                self.report_error(UndeclaredIdentifierError(node.target.name))
                return
            
            # Tidak dapat melakukan assignment ke konstanta
            if symbol['obj'] == ObjKind.CONSTANT:
                self.report_error(InvalidAssignmentError(
                    node.target.name, "cannot assign to constant"
                ))
                return
            
            target_type = symbol['type']
        else:
            # Tangani tipe target lain (akses array, dsb.)
            target_type = self.visit(node.target)
        
        # Ambil tipe nilai
        value_type = self.visit(node.value)
        
        # Periksa kompatibilitas tipe
        try:
            self.type_checker.check_assignment(target_type, value_type)
        except SemanticError as e:
            self.report_error(e)
    
    def visit_IfNode(self, node):
        """Kunjungi pernyataan if"""
        # Periksa kondisi bertipe boolean
        condition_type = self.visit(node.condition)
        try:
            self.type_checker.check_condition(condition_type, "if statement")
        except SemanticError as e:
            self.report_error(e)
        
        # Kunjungi blok then
        if node.then_block:
            self.visit(node.then_block)
        
        # Kunjungi blok else jika ada
        if node.else_block:
            self.visit(node.else_block)
    
    def visit_WhileNode(self, node):
        """Kunjungi pernyataan while"""
        # Periksa kondisi bertipe boolean
        condition_type = self.visit(node.condition)
        try:
            self.type_checker.check_condition(condition_type, "while statement")
        except SemanticError as e:
            self.report_error(e)
        
        # Kunjungi badan
        if node.body:
            self.visit(node.body)
    
    def visit_RepeatNode(self, node):
        """Kunjungi pernyataan repeat-until"""
        # Kunjungi badan terlebih dahulu
        if node.body:
            self.visit(node.body)
        
        # Periksa kondisi bertipe boolean
        condition_type = self.visit(node.condition)
        try:
            self.type_checker.check_condition(condition_type, "repeat-until statement")
        except SemanticError as e:
            self.report_error(e)
    
    def visit_ForNode(self, node):
        """Kunjungi pernyataan for"""
        # Ambil tipe variabel loop
        var_symbol = self.symbol_table.lookup(node.var_node.name)
        if not var_symbol:
            self.report_error(UndeclaredIdentifierError(node.var_node.name))
            return
        
        var_type = var_symbol['type']
        
        # Ambil tipe ekspresi awal dan akhir
        start_type = self.visit(node.start_expr)
        end_type = self.visit(node.end_expr)
        
        # Periksa batas kompatibel
        try:
            self.type_checker.check_for_loop_bounds(var_type, start_type, end_type)
        except SemanticError as e:
            self.report_error(e)
        
        # Kunjungi badan
        if node.body:
            self.visit(node.body)
    
    def visit_ProcedureFunctionCallNode(self, node):
        """Kunjungi pemanggilan prosedur/fungsi"""
        # Periksa apakah ini built-in
        call_name = node.name.lower() if isinstance(node.name, str) else str(node.name).lower()
        
        if call_name in self.builtins:
            # Built-in menerima argumen apa pun, lewati pemeriksaan rinci
            if node.args:
                for arg in node.args:
                    self.visit(arg)
            return TypeKind.NOTYPE
        
        # Cari entri prosedur/fungsi
        symbol = self.symbol_table.lookup(node.name)
        if not symbol:
            self.report_error(UndeclaredIdentifierError(node.name))
            return TypeKind.NOTYPE
        
        # Periksa bahwa simbol dapat dipanggil
        if symbol['obj'] not in [ObjKind.PROCEDURE, ObjKind.FUNCTION]:
            self.report_error(NotAProcedureError(node.name))
            return TypeKind.NOTYPE
        
        # Ambil parameter yang diharapkan
        expected_params = self.symbol_table.get_parameters(symbol)
        
        # Periksa jumlah argumen
        actual_count = len(node.args) if node.args else 0
        expected_count = len(expected_params)
        
        if actual_count != expected_count:
            self.report_error(ArgumentCountError(expected_count, actual_count, node.name))
        
        # Periksa tipe argumen
        if node.args:
            for i, (arg, expected_param) in enumerate(zip(node.args, expected_params)):
                arg_type = self.visit(arg)
                expected_type = expected_param['type']
                
                if not self.type_checker.is_compatible(expected_type, arg_type):
                    self.report_error(ArgumentTypeError(
                        f"argument {i+1}",
                        self.type_checker.get_type_name(expected_type),
                        self.type_checker.get_type_name(arg_type)
                    ))
        
        # Kembalikan tipe untuk fungsi
        if symbol['obj'] == ObjKind.FUNCTION:
            return symbol['type']
        
        return TypeKind.NOTYPE
    
    # ========== Ekspresi ==========
    
    def visit_BinOpNode(self, node):
        """Kunjungi operasi biner"""
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        
        try:
            result_type = self.type_checker.get_result_type(
                node.op, left_type, right_type
            )
            return result_type
        except SemanticError as e:
            self.report_error(e)
            return TypeKind.NOTYPE
    
    def visit_UnaryOpNode(self, node):
        """Kunjungi operasi unary"""
        operand_type = self.visit(node.operand)
        
        try:
            result_type = self.type_checker.check_unary_operation(node.op, operand_type)
            return result_type
        except SemanticError as e:
            self.report_error(e)
            return TypeKind.NOTYPE
    
    def visit_VarNode(self, node):
        """Kunjungi referensi variabel"""
        symbol = self.symbol_table.lookup(node.name)
        if not symbol:
            self.report_error(UndeclaredIdentifierError(node.name))
            return TypeKind.NOTYPE
        
        return symbol['type']
    
    def visit_ArrayAccessNode(self, node):
        """Kunjungi akses array (misal: arr[i])"""
        # Ambil variabel array
        if hasattr(node.array, 'name'):
            array_name = node.array.name
            symbol = self.symbol_table.lookup(array_name)
            
            if not symbol:
                self.report_error(UndeclaredIdentifierError(array_name))
                return TypeKind.NOTYPE
            
            # Periksa apakah memang bertipe array
            if symbol['type'] != TypeKind.ARRAY:
                self.report_error(SemanticError(f"'{array_name}' is not an array"))
                return TypeKind.NOTYPE
            
            # Periksa tipe indeks
            index_type = self.visit(node.index)
            if index_type != TypeKind.INTEGER:
                try:
                    self.type_checker.check_array_index(index_type)
                except SemanticError as e:
                    self.report_error(e)
            
            # Ambil tipe elemen dari ATAB
            ref = symbol.get('ref', -1)
            if ref >= 0 and ref < len(self.symbol_table.atab):
                array_info = self.symbol_table.atab[ref]
                return array_info['etyp']
            
            # Fallback: kembalikan INTEGER jika info array tidak ditemukan
            return TypeKind.INTEGER
        
        return TypeKind.NOTYPE

    
    def visit_NumNode(self, node):
        """Kunjungi literal angka"""
        # Periksa apakah integer atau real
        if isinstance(node.value, int) or '.' not in str(node.value):
            return TypeKind.INTEGER
        return TypeKind.REAL
    
    def visit_StringNode(self, node):
        """Kunjungi literal string"""
        # String satu karakter bertipe char
        if len(node.value) == 1:
            return TypeKind.CHAR
        # String diperlakukan sebagai array char (disederhanakan)
        return TypeKind.CHAR
    
    def visit_BooleanNode(self, node):
        """Kunjungi literal boolean"""
        return TypeKind.BOOLEAN
    
    # ========== Metode Bantu ==========
    
    def _get_type_kind(self, type_str):
        """Konversikan string tipe menjadi konstanta TypeKind"""
        type_map = {
            'integer': TypeKind.INTEGER,
            'real': TypeKind.REAL,
            'boolean': TypeKind.BOOLEAN,
            'char': TypeKind.CHAR,
            'array': TypeKind.ARRAY,
            'larik': TypeKind.ARRAY,
            'record': TypeKind.RECORD,
            'rekaman': TypeKind.RECORD
        }
        
        if isinstance(type_str, str):
            return type_map.get(type_str.lower(), TypeKind.NOTYPE)
        
        return TypeKind.NOTYPE
    
    def _resolve_type_node(self, type_node):
        """Resolusi node tipe menjadi TypeKind"""
        # Handle berbagai representasi node tipe
        if isinstance(type_node, str):
            return self._get_type_kind(type_node)
        
        # Handle tipe array, tipe record, dll.
        # Dapat di-expand sesuai struktur AST
        
        return TypeKind.NOTYPE
