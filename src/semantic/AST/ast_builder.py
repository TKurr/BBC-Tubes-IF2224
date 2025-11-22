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
                "<var-declaration>": self.build_var_decl_node,
                "<compound-statement>": self.build_block_node,
                "<assignment-statement>": self.build_assign_node,
                "<expression>": self.build_expression_node,
                "<simple-expression>": self.build_simple_expression_node,
                "<term>": self.build_term_node,
                "<factor>": self.build_factor_node,
                "<procedure/function-call>": self.build_procedure_call_node,
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
        token = next((t for t in node.child if isinstance(t, Token)), None)
        return VarNode(token.value) if token else None

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
                decls_attr = decl_node.children if decl_node else []
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

    def build_var_decl_node(self, node):
        declarations = []
        identifiers_nodes = [c for c in node.child if c.type == "<identifier-list>"]
        type_nodes = [c for c in node.child if c.type == "<type>"]

        for id_node, type_node in zip(identifiers_nodes, type_nodes):
            vartype = None
            type_token = next((t for t in type_node.child if hasattr(t, "value")), None)
            if type_token:
                vartype = type_token.value

            for item in id_node.child:
                if item.type == "IDENTIFIER":
                    declarations.append(VarDeclNode(item.value, vartype))
        return declarations

    def build_block_node(self, node):
        stmts_nodes = [c for c in node.child if c.type not in ("KEYWORD",)]
        stmts = []
        for stmt in stmts_nodes:
            stmt_node = self.build_node(stmt)
            if isinstance(stmt_node, BlockNode):
                stmts.extend(stmt_node.children)
            elif stmt_node:
                stmts.append(stmt_node)
        return BlockNode(stmts)

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
        ops = [c for c in node.child if isinstance(c, Token) and c.type == "ARITHMETIC_OPERATOR"]
        if len(simple_exprs) == 2 and ops:
            return BinOpNode(simple_exprs[0], ops[0].value, simple_exprs[1])
        return simple_exprs[0] if simple_exprs else None

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
    # Procedure call
    # ---------------------------
    def build_procedure_call_node(self, node):
        name_token = next((t for t in node.child if isinstance(t, Token) and t.type == "IDENTIFIER"), None)
        if not name_token:
            raise ASTError("Procedure call missing name", node)
        args = [self.build_node(c) for c in node.child if c.type == "<expression>"]
        return ProcedureCallNode(name_token.value, args)

    # ---------------------------
    # Conditional Node
    # ---------------------------
    def build_if_node(self, node):
        condition = next((self.build_node(c) for c in node.child if c.type == "<expression>"), None)
        then_block = next((self.build_node(c) for c in node.child if c.type == "<compound-statement>"), None)
        else_block = next((self.build_node(c) for c in node.child if getattr(c, "value", "").lower() in ("selain_itu", "selain-itu")), None)
        return IfNode(condition, then_block, else_block)

    def build_case_node(self, node):
        expr_node = next((self.build_node(c) for c in node.child if c.type == "<expression>"), None)
        case_list_node = next((c for c in node.child if c.type == "<case-list>"), None)
        branches = []
        if case_list_node:
            for case in case_list_node.child:
                constants = [self.build_node(c) for c in case.child if c.type != "COLON"]
                stmt_node = next((self.build_node(c) for c in case.child if c.type != "COLON"), None)
                branches.append(CaseBranchNode(constants, stmt_node))
        return CaseNode(expr_node, branches)

    # ---------------------------
    # Loop Node
    # ---------------------------
    def build_while_node(self, node):
        condition = next((self.build_node(c) for c in node.child if c.type in ("<expression>", "<factor>")), None)
        body = next((self.build_node(c) for c in node.child if c.type == "<compound-statement>"), None)
        if not condition or not body:
            raise ASTError("While statement incomplete", node)
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
        end_expr = next((self.build_node(c) for c in reversed(node.child) if c.type == "<expression>"), None)
        body_node = next((self.build_node(c) for c in node.child if c.type == "<compound-statement>"), None)
        direction_token = next((c for c in node.child if getattr(c, "value", "").lower() in ("ke", "sampai")), None)
        direction = getattr(direction_token, "value", "ke").lower() if direction_token else "ke"
        return ForNode(var_node, start_expr, end_expr, direction, body_node)
