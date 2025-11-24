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
        token = next((t for t in node.child if isinstance(t, Token) and t.type == "IDENTIFIER"), None)
        if not token:
            return None

        var_node = VarNode(token.value)

        index_node = next((c for c in node.child if c.type == "<variable-index>"), None)
        if index_node:
            expr_node = next((self.build_node(c) for c in index_node.child if c.type == "<expression>"), None)
            return ArrayAccessNode(var_node, expr_node)

        return var_node

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
            vartype = None

            array_node = next((c for c in type_node.child if c.type == "<array-type>"), None)
            if array_node:
                bounds = []
                range_node = next((c for c in array_node.child if c.type == "<range>"), None)
                if range_node:
                    expr_nodes = [c for c in range_node.child if c.type == "<expression>"]
                    if len(expr_nodes) == 2:
                        lower = self.build_node(expr_nodes[0])
                        upper = self.build_node(expr_nodes[1])
                        bounds.append((lower, upper))

                base_type_node = next((c for c in array_node.child if c.type == "<type>"), None)
                base_type = None
                if base_type_node:
                    type_token = next((t for t in base_type_node.child if isinstance(t, Token) and t.type == "KEYWORD"), None)
                    base_type = type_token.value if type_token else None

                vartype = ArrayTypeNode(base_type, bounds)
            else:
                type_token = next((t for t in type_node.child if hasattr(t, "value")), None)
                if type_token:
                    vartype = type_token.value

            for item in id_node.child:
                if item.type == "IDENTIFIER":
                    declarations.append(VarDeclNode(item.value, vartype))
        return declarations

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

    # ---------------------------
    # Assignment
    # ---------------------------
    def build_assign_node(self, node):
        target_node = next((self.build_node(c) for c in node.child if c.type == "<variable>"), None)
        value_node = next((self.build_node(c) for c in node.child if c.type == "<expression>"), None)
        # if not target_node or not value_node:
        #     raise ASTError("Assignment statement incomplete", node)
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
        terms = [self.build_term_node(c) for c in node.child if c.type == "<term>"]
        ops = [c for c in node.child if isinstance(c, Token) and c.type == "ARITHMETIC_OPERATOR"]
        if not ops:
            return terms[0] if terms else None
        current = terms[0]
        for i, op in enumerate(ops):
            current = BinOpNode(current, op.value, terms[i+1])
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
        # unary, parentheses, terminal
        if len(node.child) == 1:
            t = node.child[0]
            if isinstance(t, Token):
                return self.build_token(t)
            else:
                return self.build_node(t)
        elif any(getattr(c, "value", "").lower() == "tidak" for c in node.child):
            factor = next((self.build_factor_node(c) for c in node.child if getattr(c, "value", "").lower() != "tidak"), None)
            return UnaryOpNode("tidak", factor)
        elif any(c.type == "LPARENTHESIS" for c in node.child):
            expr = next((self.build_expression_node(c) for c in node.child if c.type == "<expression>"), None)
            return expr
        else:
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
                    params.append(ParamNode(name, vartype))

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
        expr_node = next((self.build_node(c) for c in node.child if c.type == "<expression>"), None)
        case_list_node = next((c for c in node.child if c.type == "<case-list>"), None)
        branches = []
        if case_list_node:
            for case in case_list_node.child:
                constants = [self.build_node(c) for c in case.child if c.type != "COLON"]
                statement_node = next((self.build_node(c) for c in case.child if c.type != "COLON"), None)
                branches.append(CaseBranchNode(constants, statement_node))
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
