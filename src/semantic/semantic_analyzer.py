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
            'tulis', 'baca',
        }
        
        self._string_handler = None

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
        # Tambahkan nama program ke symbol table
        if node.name:
            prog_idx = self.symbol_table.add_program_name(node.name)
            # Dekorasi node
            node.attr['tab_index'] = prog_idx
            node.attr['type'] = TypeKind.NOTYPE
            node.attr['lev'] = 0

        # Kunjungi bagian deklarasi
        if node.declarations:
            for decl in node.declarations:
                self.visit(decl)

        # Kunjungi blok utama - enter scope untuk compound statement
        if node.block:
            block_idx = self.symbol_table.enter_scope()
            # Dekorasi block node
            node.block.attr['block_index'] = block_idx
            node.block.attr['lev'] = self.symbol_table.current_level

            self.visit(node.block)
            self.symbol_table.exit_scope()

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
        existing = self.symbol_table.lookup_current_scope(node.name)
        if existing:
            self.report_error(RedeclaredIdentifierError(node.name))
            return

        # Handle variable of a user-defined RECORD type
        if isinstance(node.vartype, RecordTypeNode):
            # cek tipe record di symbol table jika ada type_name
            type_name = getattr(node.vartype, 'name', None)
            type_kind = TypeKind.RECORD

            var_idx = self.symbol_table.add_variable(node.name, type_kind)
            node.attr['tab_index'] = var_idx
            node.attr['type'] = type_kind
            node.attr['lev'] = self.symbol_table.current_level

            # isi fields
            fields = {}
            if hasattr(node.vartype, 'fields'):
                for f in node.vartype.fields:
                    # gunakan _get_type_kind tapi jika f.type_ adalah user-defined record, ambil fields
                    ft = self._get_type_kind(f.type_)
                    # Jika user-defined record, ambil fields dari symbol table
                    if ft == TypeKind.RECORD and isinstance(f.type_, str):
                        rec_symbol = self.symbol_table.lookup(f.type_)
                        if rec_symbol and 'fields' in rec_symbol:
                            fields[f.name] = rec_symbol['fields']
                        else:
                            fields[f.name] = TypeKind.NOTYPE
                    else:
                        fields[f.name] = ft
            node.attr['fields'] = fields
            self.symbol_table.tab[var_idx]['fields'] = fields
            return

        # Handle array
        if getattr(node.vartype, '__class__', None).__name__ == 'ArrayTypeNode':
            base_type = self._get_type_kind(node.vartype.base_type)
            low, high = 1, 10
            if hasattr(node.vartype, 'bounds') and node.vartype.bounds:
                b = node.vartype.bounds[0]
                if isinstance(b, tuple) and len(b) == 2:
                    low = int(getattr(b[0], 'value', 1))
                    high = int(getattr(b[1], 'value', 10))

            var_idx = self.symbol_table.add_variable(node.name, TypeKind.ARRAY)
            atab_idx = self.symbol_table.add_array_info(
                xtyp=TypeKind.ARRAY, etyp=base_type, low=low, high=high, elsz=1
            )
            self.symbol_table.tab[var_idx]['ref'] = atab_idx
            node.attr['tab_index'] = var_idx
            node.attr['type'] = TypeKind.ARRAY
            node.attr['lev'] = self.symbol_table.current_level
            return

        # Tipe sederhana
        type_kind = self._get_type_kind(node.vartype)
        var_idx = self.symbol_table.add_variable(node.name, type_kind)
        node.attr['tab_index'] = var_idx
        node.attr['type'] = type_kind
        node.attr['lev'] = self.symbol_table.current_level

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
        type_idx = self.symbol_table.add_type(node.name, type_kind)

        # Jika ini RecordTypeNode, simpan field info ke symbol table entry
        if isinstance(node.type_node, RecordTypeNode):
            # _resolve_type_node sudah mengisi node.type_node.attr['fields']
            field_info = node.type_node.attr.get('fields', {})
            if type_idx is not None and 0 <= type_idx < len(self.symbol_table.tab):
                self.symbol_table.tab[type_idx]['fields'] = field_info


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
        is_var_flag = getattr(node, 'is_var', False)

        for name in node.names:
            self.symbol_table.add_parameter(name, type_kind, is_var_flag)

    # ========== Pernyataan (Statements) ==========

    def visit_AssignNode(self, node):
        """Kunjungi pernyataan assignment"""
        target_type = self.visit(node.target)
        value_type = self.visit(node.value)

        # cek kesesuaian tipe
        try:
            self.type_checker.check_assignment(target_type, value_type)
        except SemanticError as e:
            self.report_error(e)

        node.attr['type'] = TypeKind.NOTYPE


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

            # Cek apakah builtin sudah ada di symbol table
            symbol = self.symbol_table.lookup(call_name)
            if not symbol:
                # Tambahkan builtin ke symbol table saat pertama kali digunakan
                tab_idx = self.symbol_table.add_builtin_procedure(call_name)
            else:
                # Cari tab_index untuk built-in yang sudah ada
                tab_idx = None
                for idx, entry in enumerate(self.symbol_table.tab):
                    if entry.get('name') == call_name:
                        tab_idx = idx
                        break

            node.attr['tab_index'] = tab_idx
            node.attr['type'] = 'predefined'
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
            # Dekorasi node
            node.attr['type'] = result_type
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
        symbol = self.symbol_table.lookup(node.name)
        if not symbol:
            self.report_error(UndeclaredIdentifierError(node.name))
            return TypeKind.NOTYPE

        # Dekorasi node dengan info dari symbol table
        tab_idx = None
        for idx, entry in enumerate(self.symbol_table.tab):
            if entry.get('name') == node.name:
                tab_idx = idx
                break

        node.attr['tab_index'] = tab_idx
        node.attr['type'] = symbol['type']
        node.attr['lev'] = symbol.get('lev', 0)

        # Copy fields dari symbol table (untuk record)
        if 'fields' in symbol:
            node.attr['fields'] = symbol['fields']  # <<< ini penting

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

    def visit_RecordFieldNode(self, node):
        """Kunjungi field record, mendukung nested record & array"""
        parent_type = self.visit(node.parent)  # tipe dari record parent
        if parent_type == TypeKind.NOTYPE:
            return TypeKind.NOTYPE

        if isinstance(parent_type, dict) and parent_type.get('kind') == TypeKind.RECORD:
            fields = parent_type.get('fields', {})
        else:
            self.report_error(SemanticError(
                f"Cannot access field '{node.name}' of non-record type"
            ))
            return TypeKind.NOTYPE

        # cek apakah field ada
        field_type = fields.get(node.name)
        if field_type is None:
            self.report_error(UndeclaredIdentifierError(node.name))
            return TypeKind.NOTYPE

        # dekorasi node
        node.attr['type'] = field_type
        node.attr['parent_type'] = parent_type
        return field_type


    def visit_ArrayTypeNode(self, node):
        """Resolusi info tipe array untuk VarDecl/TypeDecl"""
        
        base_type_kind = self._get_type_kind(node.base_type)
        
        # Ambil batasan
        low = 1
        high = 10
        if hasattr(node, 'bounds') and node.bounds:
            bound_info = node.bounds[0] 
            if isinstance(bound_info, tuple) and len(bound_info) == 2:
                lower_node, upper_node = bound_info
                low = lower_node.value if hasattr(lower_node, 'value') else 1 
                high = upper_node.value if hasattr(upper_node, 'value') else 10 
            
        return TypeKind.ARRAY, base_type_kind, low, high


    def visit_NumNode(self, node):
        """Kunjungi literal angka"""
        # Periksa apakah integer atau real
        if isinstance(node.value, int) or '.' not in str(node.value):
            node.attr['type'] = TypeKind.INTEGER
            return TypeKind.INTEGER
        node.attr['type'] = TypeKind.REAL
        return TypeKind.REAL

    def visit_StringNode(self, node):
        """Kunjungi literal string"""
        # Cek literal char dari lexer/AST builder
        if getattr(node, 'is_char_literal', False):
            node.attr['type'] = TypeKind.CHAR
            return TypeKind.CHAR

        literal_value = node.value if isinstance(node.value, str) else ''
        stripped_value = literal_value

        if len(literal_value) >= 2 and literal_value[0] == "'" and literal_value[-1] == "'":
            stripped_value = literal_value[1:-1]

        if len(stripped_value) == 1:
            node.attr['type'] = TypeKind.CHAR
            return TypeKind.CHAR

        node.attr['type'] = TypeKind.STRING
        return TypeKind.STRING

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
            'string': TypeKind.STRING,
            'array': TypeKind.ARRAY,
            'larik': TypeKind.ARRAY,
            'record': TypeKind.RECORD,
            'rekaman': TypeKind.RECORD
        }

        if isinstance(type_str, str):
            #Tipe Primitif/Keyword
            mapped_type = type_map.get(type_str.lower())
            if mapped_type is not None:
                return mapped_type
            
            #Tipe Didefinisikan Pengguna (Cari di Symbol Table)
            symbol = self.symbol_table.lookup(type_str)
            if symbol and symbol['obj'] == ObjKind.TYPE:
                type_kind = symbol['type']
                # ambil fields jika record
                if type_kind == TypeKind.RECORD and 'fields' in symbol:
                    return {'kind': TypeKind.RECORD, 'fields': symbol['fields']}
                return type_kind
            
            # Tipe Record/Array (fallback)
            return TypeKind.NOTYPE

        return TypeKind.NOTYPE

    def _resolve_type_node(self, type_node):

        # RangeTypeNode -> integer subrange
        if isinstance(type_node, RangeTypeNode):
            low = type_node.lower.value
            high = type_node.upper.value
            type_node.attr['range'] = (low, high)
            return TypeKind.INTEGER   # Pascal subrange dianggap integer

        # ArrayTypeNode
        if isinstance(type_node, ArrayTypeNode):
            # simpan batasan dan tipe elemen
            base_type = self._get_type_kind(type_node.base_type)
            bound = type_node.bounds[0]
            low = bound[0].value
            high = bound[1].value
            type_node.attr['array_info'] = (base_type, low, high)
            return TypeKind.ARRAY

        # RecordTypeNode
        if isinstance(type_node, RecordTypeNode):
            fields = {}
            for f in type_node.fields:
                fields[f.name] = self._get_type_kind(f.type_)
            type_node.attr['fields'] = fields
            return TypeKind.RECORD

        # primitive / identifier type
        if isinstance(type_node, str):
            return self._get_type_kind(type_node)

        return TypeKind.NOTYPE
