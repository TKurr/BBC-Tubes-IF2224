from .nodes import *
from src.lexer.token import Token
from src.parser.parse_node import ParseNode

class ASTError(Exception):
    def __init__(self, message, node=None):
        self.node = node
        super().__init__(message)

class ASTBuilder:
    def __init__(self, parse_root):
        self.parse_root = parse_root

    def build(self):
        return self.build_node(self.parse_root)

    # ---------------------------
    # Controller SDT
    # ---------------------------
    def build_node(self, node):
        if isinstance(node, Token):
            return self.build_token(node)
        elif isinstance(node, ParseNode):
            controller_map = {
                "<program>": self.build_program_node,
                "<program-header>": lambda n: None,
                "<declaration-part>": self.build_declarations_node,
                "<const-declaration>": self.build_const_decl_node,
                "<var-declaration>": self.build_var_decl_node,
                "<type-declaration>": self.build_type_declaration_node,
                "<record-type>": self.build_record_type_node,
                "<compound-statement>": self.build_block_node,
                "<assignment-statement>": self.build_assign_node,
                "<expression>": self.build_expression_node,
                "<simple-expression>": self.build_simple_expression_node,
                "<term>": self.build_term_node,
                "<factor>": self.build_factor_node,
                "<procedure-declaration>": self.build_procedure_decl_node,
                "<function-declaration>": self.build_function_decl_node,
                "<procedure/function-call>": self.build_procedure_function_call_node,
                "<variable>": self.build_variable_node,
                "<number>": self.build_number_node,
                "<string-literal>": self.build_string_node,
                "<if-statement>": self.build_if_node,
                "<while-statement>": self.build_while_node,
                "<for-statement>": self.build_for_node,
                "<repeat-statement>": self.build_repeat_node,
                "<case-statement>": self.build_case_node
            }
            builder = controller_map.get(node.type)
            if builder:
                return builder(node)
            # fallback SDT: ambil atribut dari child
            children_nodes = [self.build_node(c) for c in node.child if self.build_node(c)]
            if len(children_nodes) == 1:
                return children_nodes[0]
            return BlockNode(children_nodes)
        return None

    # ---------------------------
    # Terminal nodes
    # ---------------------------
    def build_token(self, token):
        if token.type == "NUMBER":
            return NumNode(token.value)
        elif token.type in ["STRING_LITERAL", "CHAR_LITERAL"]:
            return StringNode(token.value)
        elif token.type == "IDENTIFIER":
            return VarNode(token.value)
        return None

    def build_number_node(self, node):
        token = next((t for t in node.child if isinstance(t, Token)), None)
        return NumNode(token.value) if token else None

    def build_string_node(self, node):
        token = next((t for t in node.child if isinstance(t, Token)), None)
        return StringNode(token.value) if token else None

    def build_variable_node(self, node):
        base_token = next((t for t in node.child if isinstance(t, Token) and t.type == "IDENTIFIER"), None)
        if not base_token:
            return None

        current_node = VarNode(base_token.value)

        # Traversal child untuk field atau array index
        i = 0
        while i < len(node.child):
            c = node.child[i]

            # Skip identifier pertama yang sudah diambil
            if isinstance(c, Token) and c.value == base_token.value and i == 0:
                 pass

            # DOT -> akses field
            elif isinstance(c, Token) and c.type == "DOT":
                next_child = node.child[i] if i < len(node.child) else None
                if next_child and isinstance(next_child, Token) and next_child.type == "IDENTIFIER":
                    current_node = RecordFieldNode(next_child.value, current_node)
                    i += 1


            # <variable-index> -> akses array
            elif getattr(c, "type", None) == "<variable-index>":
                expr_node = next((self.build_node(x) for x in c.child if getattr(x, "type", None) == "<expression>"), None)
                if expr_node:
                    current_node = ArrayAccessNode(current_node, expr_node)

            i += 1

        return current_node

    # ---------------------------
    # Helper for building lists
    # ---------------------------

    def build_statement_list(self, nodes):
        statements = []
        for n in nodes:
            node = self.build_node(n)
            if node:
                if isinstance(node, BlockNode):
                    statements.extend(node.children)
                else:
                    statements.append(node)
        return BlockNode(statements) if len(statements) > 1 else (statements[0] if statements else None)

    # ---------------------------
    # Program / Declarations / Block
    # ---------------------------
    def build_program_node(self, node):
        prog_name = None
        decls_attr = []
        block_attr = None

        for c in node.child:
            if c.type == "<program-header>":
                token = next((t for t in c.child if isinstance(t, Token) and t.type == "IDENTIFIER"), None)
                if token:
                    prog_name = token.value
            elif c.type == "<declaration-part>":
                decl_node = self.build_node(c)
                decls_attr = [decl_node] if decl_node else []
            elif c.type == "<compound-statement>":
                block_attr = self.build_node(c)

        return ProgramNode(prog_name, decls_attr, block_attr)

    def build_declarations_node(self, node):
        decls = []
        for c in node.child:
            child_decl = self.build_node(c)
            if child_decl:
                if isinstance(child_decl, list):
                    decls.extend(child_decl)
                else:
                    decls.append(child_decl)
        return DeclarationsNode(decls)

    def build_const_decl_node(self, node):
        consts = []
        i = 0
        children = node.child

        while i < len(children):
            c = children[i]
            if isinstance(c, Token) and c.type == "IDENTIFIER":
                name = c.value
                j = i + 1
                while j < len(children) and children[j].type != "<expression>":
                    j += 1
                expr_node = None
                if j < len(children) and children[j].type == "<expression>":
                    expr_node = self.build_node(children[j])
                else:
                    expr_node = None

                const_node = ConstDeclNode(name, expr_node)
                consts.append(const_node)

                k = j + 1
                while k < len(children) and not (isinstance(children[k], Token) and children[k].type == "SEMICOLON"):
                    k += 1
                i = k + 1
                continue

            i += 1

        return consts

    def build_var_decl_node(self, node):
        declarations = []
        identifiers_nodes = [c for c in node.child if c.type == "<identifier-list>"]
        type_nodes = [c for c in node.child if c.type == "<type>"]

        for id_node, type_node in zip(identifiers_nodes, type_nodes):
            vartype = self.build_type_definition_node(type_node)

            for item in id_node.child:
                if item.type == "IDENTIFIER":
                    declarations.append(VarDeclNode(item.value, vartype))
        return declarations

    def build_type_definition_node(self, node):
        if node is None:
            return None

        # Token langsung
        if isinstance(node, Token):
            if node.type in ("IDENTIFIER", "KEYWORD"):
                return node.value
            return None

        # Tangani range: <expression> RANGE_OPERATOR(..) <expression>
        expr_nodes = [c for c in getattr(node, "child", []) if getattr(c, "type", None) == "<expression>"]
        range_op = next((c for c in getattr(node, "child", []) if isinstance(c, Token) and c.type == "RANGE_OPERATOR"), None)
        if len(expr_nodes) == 2 and range_op:
            lower = self.build_node(expr_nodes[0])
            upper = self.build_node(expr_nodes[1])
            return RangeTypeNode(lower, upper)

        # Tangani record / array / primitive seperti sebelumnya
        for c in getattr(node, "child", []):
            if getattr(c, "type", None) == "<record-type>":
                return self.build_record_type_node(c)
            if getattr(c, "type", None) == "<array-type>":
                # sama seperti sebelumnya
                bounds = []
                range_node = next((x for x in c.child if getattr(x,"type",None)=="<range>"), None)
                if range_node:
                    lower = self.build_node(range_node.child[0])
                    upper = self.build_node(range_node.child[2])

                    bounds.append((lower, upper))
                base_type_node = next((x for x in c.child if getattr(x,"type",None)=="<type>"), None)
                base_type = self.build_type_definition_node(base_type_node) if base_type_node else None
                return ArrayTypeNode(base_type, bounds)
            if isinstance(c, Token) and c.type in ("IDENTIFIER","KEYWORD"):
                return c.value
            # rekursif
            res = self.build_type_definition_node(c)
            if res:
                return res

        return None

    def build_type_declaration_node(self, node):
        type_decls = []
        if not hasattr(self, "type_table"):
            self.type_table = {}
        i = 0
        while i < len(node.child):
            if node.child[i].type == "IDENTIFIER" and i+2 < len(node.child):
                identifier = node.child[i].value
                if node.child[i+1].type == "RELATIONAL_OPERATOR" and node.child[i+1].value == "=":
                    type_def_node = node.child[i+2]
                    type_def = self.build_type_definition_node(type_def_node)
                    type_decl = TypeDeclarationNode(identifier, type_def)
                    type_decls.append(type_decl)
                    self.type_table[identifier] = type_def  # simpan di type table
                    i += 3
                    if i < len(node.child) and node.child[i].type == "SEMICOLON":
                        i += 1
                    continue
            i += 1
        return type_decls

    def build_record_type_node(self, node):
        fields = []
        for group in node.child:
            if group.type == "<parameter-group>":
                id_list_node = next((c for c in group.child if c.type == "<identifier-list>"), None)
                ids = [t.value for t in getattr(id_list_node, "child", []) if isinstance(t, Token) and t.type == "IDENTIFIER"] if id_list_node else []

                type_node = next((c for c in group.child if c.type == "<type>"), None)
                field_type = self.build_type_definition_node(type_node) if type_node else None

                for name in ids:
                    fields.append(RecordFieldNode(name, field_type))

        return RecordTypeNode(fields)

    def build_block_node(self, node):
        statements_nodes = [c for c in node.child if c.type not in ("KEYWORD",)]
        statements = []
        for statement in statements_nodes:
            statement_node = self.build_node(statement)
            if isinstance(statement_node, BlockNode):
                statements.extend(statement_node.children)
            elif statement_node:
                statements.append(statement_node)
        return BlockNode(statements)

    def build_variable_access(self, node):
        base_token = next((t for t in node.child if isinstance(t, Token) and t.type == "IDENTIFIER"), None)
        if not base_token:
            return None
        current_node = VarNode(base_token.value)

        i = 0
        while i < len(node.child):
            c = node.child[i]
            if c.type == "<variable-index>":
                expr_node = next((self.build_node(x) for x in c.child if x.type == "<expression>"), None)
                current_node = ArrayAccessNode(current_node, expr_node)
            elif isinstance(c, Token) and c.type == "DOT":
                i += 1
                field_token = node.child[i] if i < len(node.child) else None
                if field_token and isinstance(field_token, Token) and field_token.type == "IDENTIFIER":
                    current_node = RecordFieldNode(field_token.value, current_node)
            i += 1

        return current_node

    # ---------------------------
    # Assignment
    # ---------------------------
    def build_assign_node(self, node):
        target_node = next((self.build_node(c) for c in node.child if c.type == "<variable>"), None)
        value_node = next((self.build_node(c) for c in node.child if c.type == "<expression>"), None)
        if not target_node or not value_node:
            raise ASTError("Assignment statement incomplete", node)
        return AssignNode(target_node, value_node)

    # ---------------------------
    # Expressions (SDT)
    # ---------------------------
    def build_expression_node(self, node):
        simple_exprs = [self.build_simple_expression_node(c) for c in node.child if c.type == "<simple-expression>"]
        ops = [c for c in node.child if isinstance(c, Token) and c.type in ("ARITHMETIC_OPERATOR", "RELATIONAL_OPERATOR")]

        if len(simple_exprs) == 2 and ops:
            return BinOpNode(simple_exprs[0], ops[0].value, simple_exprs[1])
        elif simple_exprs:
            return simple_exprs[0]
        return None

    def build_simple_expression_node(self, node):
        # 1. Ambil semua term dan operator
        terms = [self.build_term_node(c) for c in node.child if c.type == "<term>"]
        ops = [c for c in node.child if isinstance(c, Token) and c.type == "ARITHMETIC_OPERATOR"]

        if not terms:
            return None

        # 2. Cek apakah operasi pertama adalah Unary (misal: -3 atau +10)
        # Indikator: Anak pertama node -> TOKEN OPERATOR
        first_child = node.child[0]
        is_unary_start = isinstance(first_child, Token) and first_child.type == "ARITHMETIC_OPERATOR"

        current = None
        term_idx = 0
        op_idx = 0

        # SPLIT UNARY VS BINARY
        if is_unary_start:
            # Unary (-3): Ambil operator ke-0 dan term ke-0
            op_val = ops[0].value
            term_val = terms[0]
            current = UnaryOpNode(op_val, term_val) # Pake Node Unary

            term_idx = 1
            op_idx = 1
        else:
            # Kasus Biasa (3+5): Term ke-0 jadi base kiri
            current = terms[0]
            term_idx = 1
            op_idx = 0

        # Sisanya lanjut as Binary Operation (looping manual)
        while op_idx < len(ops):
            # check pastiin ada term kanan
            if term_idx >= len(terms):
                 break

            op_val = ops[op_idx].value
            right_val = terms[term_idx]
            current = BinOpNode(current, op_val, right_val)

            op_idx += 1
            term_idx += 1

        return current

    def build_term_node(self, node):
        factors = [self.build_factor_node(c) for c in node.child if c.type == "<factor>"]
        ops = [c for c in node.child if isinstance(c, Token) and c.type == "ARITHMETIC_OPERATOR"]
        if not ops:
            return factors[0] if factors else None
        current = factors[0]
        for i, op in enumerate(ops):
            current = BinOpNode(current, op.value, factors[i+1])
        return current

    def build_factor_node(self, node):
        # Unary tidak
        if any(getattr(c, "value", "").lower() == "tidak" for c in node.child):
            factor = next((self.build_factor_node(c) for c in node.child if getattr(c, "value", "").lower() != "tidak"), None)
            return UnaryOpNode("tidak", factor)

        # Boolean literal
        token = next((t for t in node.child if isinstance(t, Token) and t.type == "KEYWORD" and t.value.lower() in ("true","false")), None)
        if token:
            return BooleanNode(token.value.lower() == "true")

        # Jika ada logical operator (dan/or)
        logical_ops = [t for t in node.child if isinstance(t, Token) and t.type == "LOGICAL_OPERATOR"]
        if logical_ops:
            left = self.build_factor_node(node.child[0])
            for i, op in enumerate(logical_ops):
                right = self.build_factor_node(node.child[i+1])
                left = BinOpNode(left, op.value.lower(), right)
            return left

        # Parentheses
        if any(c.type == "LPARENTHESIS" for c in node.child):
            expr = next((self.build_expression_node(c) for c in node.child if getattr(c,"type",None)=="<expression>"), None)
            return expr

        # Default fallback
        return self.build_node(node.child[0])

    # ---------------------------
    # Function / Procedure
    # ---------------------------
    def build_param_list(self, node):
        params = []

        if node is None:
            return params

        for child in node.child:
            if child.type == "<parameter-group>":
                is_var = False

                #
                for grandchild in child.child:
                    if isinstance(grandchild, Token) and grandchild.value.lower() == "variabel":
                        is_var = True
                        break


                # Ambil identifier list
                id_list_node = next((c for c in child.child if c.type == "<identifier-list>"), None)
                ids = [t.value for t in id_list_node.child if isinstance(t, Token) and t.type == "IDENTIFIER"] if id_list_node else []

                # Ambil tipe
                type_node = next((c for c in child.child if c.type == "<type>"), None)
                vartype = None
                if type_node:
                    t = next((tk for tk in type_node.child if hasattr(tk, "value")), None)
                    vartype = t.value if t else None

                for name in ids:
                    params.append(ParamNode(name, vartype, is_var))

        return params

    def build_procedure_decl_node(self, node):
        # Nama prosedur
        name_token = next((t for t in node.child if isinstance(t, Token) and t.type == "IDENTIFIER"), None)
        name = name_token.value

        # Parameter list
        param_list_node = next((c for c in node.child if c.type == "<formal-parameter-list>"), None)
        params = self.build_param_list(param_list_node)

        # Block (isi prosedur)
        block_node = next((c for c in node.child if c.type in ("<block>", "<compound-statement>")), None)
        block = self.build_node(block_node)

        return ProcedureDeclNode(name, params, block)


    def build_function_decl_node(self, node):
        # Nama function
        name_token = next((t for t in node.child if isinstance(t, Token) and t.type == "IDENTIFIER"), None)
        name = name_token.value

        # Parameter list
        param_list_node = next((c for c in node.child if c.type == "<formal-parameter-list>"), None)
        params = self.build_param_list(param_list_node)

        # Return type
        type_node = next((c for c in node.child if c.type == "<type>"), None)
        return_type = None
        if type_node:
            t = next((tk for tk in type_node.child if hasattr(tk, "value")), None)
            return_type = t.value if t else None

        # Function body (block)
        block_node = next((c for c in node.child if c.type in ("<block>", "<compound-statement>")), None)
        block = self.build_node(block_node)

        return FunctionDeclNode(name, params, return_type, block)

    def build_procedure_function_call_node(self, node):
        name_token = next((t for t in node.child if isinstance(t, Token) and t.type == "IDENTIFIER"), None)
        if not name_token:
            raise ASTError("Procedure call missing name", node)

        param_list_node = next((c for c in node.child if c.type == "<parameter-list>"), None)
        args = []
        if param_list_node:
            for expr_node in param_list_node.child:
                built_expr = self.build_node(expr_node)
                if built_expr:
                    args.append(built_expr)

        return ProcedureFunctionCallNode(name_token.value, args)


    # ---------------------------
    # Conditional Node
    # ---------------------------
    def build_if_node(self, node):
        idx_jika = next(i for i, c in enumerate(node.child) if c.type == 'KEYWORD' and c.value.lower() == 'jika')
        idx_maka = next(i for i, c in enumerate(node.child) if c.type == 'KEYWORD' and c.value.lower() == 'maka')
        idx_selain_itu = next((i for i, c in enumerate(node.child) if c.type == 'KEYWORD' and c.value.lower() == 'selain_itu'), None)

        expr_node = next(c for c in node.child[idx_jika + 1: idx_maka] if c.type == "<expression>")
        condition = self.build_node(expr_node)

        if idx_selain_itu:
            then_nodes = node.child[idx_maka + 1: idx_selain_itu]
            else_nodes = node.child[idx_selain_itu + 1:]
        else:
            then_nodes = node.child[idx_maka + 1:]
            else_nodes = []

        then_body = self.build_statement_list(then_nodes)
        else_body = self.build_statement_list(else_nodes) if else_nodes else None

        return IfNode(condition=condition, then_block=then_body, else_block=else_body)

    def build_case_node(self, node):
        expr_node = next((self.build_node(c) for c in node.child if getattr(c,"type",None)=="<expression>"), None)

        case_list_node = next((c for c in node.child if getattr(c,"type",None)=="<case-list>"), None)
        branches = []

        if case_list_node:
            i = 0
            children = case_list_node.child
            while i < len(children):
                # ambil value case
                value_token = children[i]
                value_node = self.build_node(value_token) if hasattr(value_token, "type") else None
                i += 1

                # skip COLON
                if i < len(children) and isinstance(children[i], Token) and children[i].type == "COLON":
                    i += 1

                # ambil statement setelah colon
                stmt_nodes = []
                while i < len(children) and not (isinstance(children[i], Token) and children[i].type in ("NUMBER", "IDENTIFIER")):
                    stmt_nodes.append(children[i])
                    i += 1

                stmt_node = self.build_statement_list(stmt_nodes)
                branches.append(CaseBranchNode([value_node], stmt_node))

        return CaseNode(expr_node, branches)

    # ---------------------------
    # Loop Node
    # ---------------------------
    def build_while_node(self, node):
        expr_node = next((c for c in node.child if c.type == "<expression>"), None)
        if not expr_node:
            raise ASTError("While statement missing condition", node)
        condition = self.build_node(expr_node)

        body_candidates = [c for c in node.child if c.type not in ("KEYWORD", "<expression>")]
        if not body_candidates:
            raise ASTError("While statement missing body", node)
        body = self.build_statement_list(body_candidates)

        return WhileNode(condition, body)

    def build_repeat_node(self, node):
        body = next((self.build_node(c) for c in node.child if c.type == "<statement-list>"), None)
        condition = next((self.build_node(c) for c in node.child if c.type in ("<expression>", "<factor>")), None)
        if not body or not condition:
            raise ASTError("Repeat statement incomplete", node)
        return RepeatNode(body, condition)

    def build_for_node(self, node):
        var_node = next((self.build_node(c) for c in node.child if c.type == "IDENTIFIER"), None)
        start_expr = next((self.build_node(c) for c in node.child if c.type == "<expression>"), None)
        direction_token = next((c for c in node.child if getattr(c, "value", "").lower() in ("ke", "turun_ke")), None)
        end_expr = None
        if direction_token:
            idx = node.child.index(direction_token)
            for c in node.child[idx+1:]:
                if c.type == "<expression>":
                    end_expr = self.build_node(c)
                    break

        lakukan_idx = next((i for i, c in enumerate(node.child) if getattr(c, "value", "").lower() == "lakukan"), None)
        body_nodes = node.child[lakukan_idx+1:] if lakukan_idx is not None else []
        body_node = self.build_statement_list(body_nodes)

        direction = getattr(direction_token, "value", "ke").lower() if direction_token else "ke"

        return ForNode(var_node, start_expr, end_expr, direction, body_node)
