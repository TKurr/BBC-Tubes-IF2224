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
        return self._build_node(self.parse_root)

    # ---------------------------
    # Controller SDT
    # ---------------------------
    def _build_node(self, node):
        if isinstance(node, Token):
            return self._build_token(node)
        elif isinstance(node, ParseNode):
            controller_map = {
                "<program>": self._build_program_node,
                "<program-header>": lambda n: None,
                "<declaration-part>": self._build_declarations_node,
                "<var-declaration>": self._build_var_decl_node,
                "<compound-statement>": self._build_block_node,
                "<assignment-statement>": self._build_assign_node,
                "<expression>": self._build_expression_node,
                "<simple-expression>": self._build_simple_expression_node,
                "<term>": self._build_term_node,
                "<factor>": self._build_factor_node,
                "<procedure/function-call>": self._build_procedure_call_node,
                "<variable>": self._build_variable_node,
                "<number>": self._build_number_node,
                "<string-literal>": self._build_string_node,
                "<if-statement>": self._build_if_node,
                "<while-statement>": self._build_while_node,
                "<for-statement>": self._build_for_node,
                "<repeat-statement>": self._build_repeat_node,
                "<case-statement>": self._build_case_node
            }
            builder = controller_map.get(node.type)
            if builder:
                return builder(node)
            # fallback SDT: ambil atribut dari child
            children_nodes = [self._build_node(c) for c in node.child if self._build_node(c)]
            if len(children_nodes) == 1:
                return children_nodes[0]
            return BlockNode(children_nodes)
        return None

    # ---------------------------
    # Terminal nodes
    # ---------------------------
    def _build_token(self, token):
        if token.type == "NUMBER":
            return NumNode(token.value)
        elif token.type in ["STRING_LITERAL", "CHAR_LITERAL"]:
            return StringNode(token.value)
        elif token.type == "IDENTIFIER":
            return VarNode(token.value)
        return None

    def _build_number_node(self, node):
        token = next((t for t in node.child if isinstance(t, Token)), None)
        return NumNode(token.value) if token else None

    def _build_string_node(self, node):
        token = next((t for t in node.child if isinstance(t, Token)), None)
        return StringNode(token.value) if token else None

    def _build_variable_node(self, node):
        token = next((t for t in node.child if isinstance(t, Token)), None)
        return VarNode(token.value) if token else None

    # ---------------------------
    # Program / Declarations / Block
    # ---------------------------
    def _build_program_node(self, node):
        prog_name = None
        decls_attr = []
        block_attr = None

        for c in node.child:
            if c.type == "<program-header>":
                token = next((t for t in c.child if isinstance(t, Token) and t.type == "IDENTIFIER"), None)
                if token:
                    prog_name = token.value
            elif c.type == "<declaration-part>":
                decl_node = self._build_node(c)
                decls_attr = decl_node.children if decl_node else []
            elif c.type == "<compound-statement>":
                block_attr = self._build_node(c)

        return ProgramNode(prog_name, decls_attr, block_attr)

    def _build_declarations_node(self, node):
        decls = []
        for c in node.child:
            child_decl = self._build_node(c)  
            if child_decl:
                decls.extend(child_decl)      
        return DeclarationsNode(decls)

    def _build_var_decl_node(self, node):
        declarations = []

        children = node.child
        i = 0
        n = len(children)

        while i < n:
            c = children[i]

            if c.type == "<identifier-list>":
                identifiers = []
                for item in c.child:
                    if item.type == "IDENTIFIER":
                        identifiers.append(item.value)

                i += 1  

                if i < n and children[i].type == "COLON":
                    i += 1

                type_node = children[i]
                vartype = None
                for t in type_node.child:
                    if hasattr(t, "value"):
                        vartype = t.value
                        break

                i += 1 
                if i < n and children[i].type == "SEMICOLON":
                    i += 1

                for ident in identifiers:
                    declarations.append(VarDeclNode(ident, vartype))

                continue

            i += 1

        return declarations


    def _build_block_node(self, node):
        stmts = []
        for c in node.child:
            stmt = self._build_node(c)
            if isinstance(stmt, BlockNode):
                stmts.extend(stmt.children)
            elif stmt:
                stmts.append(stmt)
        return BlockNode(stmts)

    # ---------------------------
    # Assignment
    # ---------------------------
    def _build_assign_node(self, node):
        if len(node.child) < 3:
            raise ASTError("Assignment statement incomplete", node)
        target_node = self._build_node(node.child[0])
        value_node = self._build_node(node.child[2])
        return AssignNode(target_node, value_node)

    # ---------------------------
    # Expressions (SDT)
    # ---------------------------
    def _build_expression_node(self, node):
        left = self._build_simple_expression_node(node.child[0])
        if len(node.child) == 3:
            op_token = node.child[1]
            right = self._build_simple_expression_node(node.child[2])
            return BinOpNode(left, op_token.value, right)
        return left

    def _build_simple_expression_node(self, node):
        current = self._build_term_node(node.child[0])
        i = 1
        while i < len(node.child):
            op_token = node.child[i]
            next_term = self._build_term_node(node.child[i+1])
            current = BinOpNode(current, op_token.value, next_term)
            i += 2
        return current

    def _build_term_node(self, node):
        current = self._build_factor_node(node.child[0])
        i = 1
        while i < len(node.child):
            op_token = node.child[i]
            next_factor = self._build_factor_node(node.child[i+1])
            current = BinOpNode(current, op_token.value, next_factor)
            i += 2
        return current

    def _build_factor_node(self, node):
        if len(node.child) == 1:
            t = node.child[0]
            if isinstance(t, Token):
                if t.type == "NUMBER":
                    return NumNode(t.value)
                elif t.type in ["STRING_LITERAL", "CHAR_LITERAL"]:
                    return StringNode(t.value)
                elif t.type == "IDENTIFIER":
                    return VarNode(t.value)
            else:
                return self._build_node(t)
        elif len(node.child) == 2 and getattr(node.child[0], "type", "").lower() == "tidak":
            factor = self._build_factor_node(node.child[1])
            return UnaryOpNode("tidak", factor)
        elif len(node.child) == 3 and getattr(node.child[0], "type", "") == "LPARENTHESIS":
            return self._build_expression_node(node.child[1])
        else:
            return self._build_node(node.child[0])

    # ---------------------------
    # Procedure call
    # ---------------------------
    def _build_procedure_call_node(self, node):
        name_token = next((t for t in node.child if isinstance(t, Token) and t.type == "IDENTIFIER"), None)
        if not name_token:
            raise ASTError("Procedure call missing name", node)
        name = name_token.value
        args = []
        for c in node.child[1:]:
            if isinstance(c, Token) and c.type in ["LPARENTHESIS", "RPARENTHESIS"]:
                continue
            arg_node = self._build_node(c)
            if arg_node:
                args.append(arg_node)
        return ProcedureCallNode(name, args)

    # ---------------------------
    # Conditional Node
    # ---------------------------
    def _build_if_node(self, node):
        condition = self._build_node(node.child[1])
        then_block = self._build_node(node.child[3])
        else_block = None
        if len(node.child) > 4:
            token = node.child[4]
            if getattr(token, "value", "").lower() in ("selain_itu", "selain-itu"):
                else_block = self._build_node(node.child[5])
        return IfNode(condition, then_block, else_block)

    def _build_case_node(self, node):
        expr_node = self._build_node(node.child[1])
        case_list_node = node.child[3]
        branches = []
        i = 0
        while i < len(case_list_node.child):
            constants = []
            while not (isinstance(case_list_node.child[i], Token) and case_list_node.child[i].type == "COLON"):
                c = self._build_node(case_list_node.child[i])
                if c:
                    constants.append(c)
                i += 1
            i += 1  # skip COLON
            stmt_node = self._build_node(case_list_node.child[i])
            i += 1
            branches.append(CaseBranchNode(constants, stmt_node))
        return CaseNode(expr_node, branches)

    # ---------------------------
    # Loop Node
    # ---------------------------
    def _build_while_node(self, node):
        condition = next((self._build_node(c) for c in node.child if c.type in ("<expression>", "<factor>")), None)
        body = next((self._build_node(c) for c in node.child if c.type in ("<compound-statement>", "<assignment-statement>")), None)
        if not condition or not body:
            raise ASTError("While statement incomplete", node)
        return WhileNode(condition, body)

    def _build_repeat_node(self, node):
        body = next((self._build_node(c) for c in node.child if c.type == "<statement-list>"), None)
        condition = next((self._build_node(c) for c in node.child if c.type in ("<expression>", "<factor>")), None)
        if not body or not condition:
            raise ASTError("Repeat statement incomplete", node)
        return RepeatNode(body, condition)

    def _build_for_node(self, node):
        var_node = self._build_node(node.child[1])
        start_expr = self._build_node(node.child[3])
        end_expr = self._build_node(node.child[5])
        body_node = self._build_node(node.child[7])
        direction_token = node.child[4]
        direction = getattr(direction_token, "value", "ke").lower()
        return ForNode(var_node, start_expr, end_expr, direction, body_node)
