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
        try:
            return self._build_node(self.parse_root)
        except ASTError:
            raise
        except Exception as e:
            raise ASTError(f"Unexpected AST building error: {e}")

    # ---------------------------
    # Dispatcher
    # ---------------------------
    def _build_node(self, node):
        if isinstance(node, Token):
            return self._build_token(node)
        elif isinstance(node, ParseNode):
            dispatch_map = {
                "<program>": self._build_program_node,
                "<program-header>": lambda n: None,  
                "<declaration-part>": self._build_declarations_node,
                "<var-declaration>": self._build_var_decl_node,
                "<compound-statement>": self._build_block_node,
                "<assignment-statement>": self._build_assign_node,
                "<expression>": self._build_expression_node,
                "<simple-expression>": self._build_expression_node,
                "<term>": self._build_expression_node,
                "<factor>": self._build_expression_node,
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
            builder = dispatch_map.get(node.type)
            if builder:
                return builder(node)
            else:
                children_ast = [c_node for c in node.child if (c_node := self._build_node(c))]
                if len(children_ast) == 1:
                    return children_ast[0]
                return BlockNode(children_ast)
        else:
            return None

    # ---------------------------
    # Terminal builders
    # ---------------------------
    def _build_token(self, token):
        if token.type == "NUMBER":
            return NumNode(token.value)
        elif token.type in ["STRING_LITERAL", "CHAR_LITERAL"]:
            return StringNode(token.value)
        elif token.type == "IDENTIFIER":
            return VarNode(token.value)
        else:
            return None

    def _build_number_node(self, node):
        tok = next((t for t in node.child if isinstance(t, Token)), None)
        return NumNode(tok.value) if tok else None

    def _build_string_node(self, node):
        tok = next((t for t in node.child if isinstance(t, Token)), None)
        return StringNode(tok.value) if tok else None

    def _build_variable_node(self, node):
        tok = next((t for t in node.child if isinstance(t, Token)), None)
        return VarNode(tok.value) if tok else None

    # ---------------------------
    # Program / Declarations / Block
    # ---------------------------
    def _build_program_node(self, node):
        prog_name = None
        decl_node = None
        block_node = None
        for c in node.child:
            if c.type == "<program-header>":
                tok = next((t for t in c.child if isinstance(t, Token) and t.type == "IDENTIFIER"), None)
                if tok:
                    prog_name = tok.value
            elif c.type == "<declaration-part>":
                decl_node = self._build_node(c)
            elif c.type == "<compound-statement>":
                block_node = self._build_node(c)
        if block_node is None:
            raise ASTError("Program missing compound statement", node)
        return ProgramNode(
            name=prog_name,
            declarations=decl_node.children if decl_node else [],
            block=block_node
        )

    def _build_declarations_node(self, node):
        decls = []
        for c in node.child:
            child_decl = self._build_node(c)
            if child_decl:
                if isinstance(child_decl, DeclarationsNode):
                    decls.extend(child_decl.children)
                else:
                    decls.append(child_decl)
        return DeclarationsNode(decls)

    def _build_var_decl_node(self, node):
        identifiers_node = next((c for c in node.child if c.type == "<identifier-list>"), None)
        type_node = next((c for c in node.child if c.type == "<type>"), None)
        if not identifiers_node or not type_node:
            raise ASTError("Variable declaration incomplete", node)

        type_token = next((t for t in type_node.child if isinstance(t, Token)), None)
        vartype = type_token.value if type_token else None

        # Hanya ambil token IDENTIFIER, exclude koma atau token lain
        decls = [VarDeclNode(t.value, vartype) for t in identifiers_node.child if isinstance(t, Token) and t.type == "IDENTIFIER"]
        return DeclarationsNode(decls)

    def _build_block_node(self, node):
        stmts = []
        for c in node.child:
            if hasattr(c, "type") and c.type != "KEYWORD":
                stmt_node = self._build_node(c)
                if stmt_node:
                    if isinstance(stmt_node, BlockNode):
                        stmts.extend(stmt_node.children)
                    else:
                        stmts.append(stmt_node)
        return BlockNode(stmts)

    # ---------------------------
    # Assignment / Expression
    # ---------------------------
    def _build_assign_node(self, node):
        if len(node.child) < 3:
            raise ASTError("Assignment statement incomplete", node)
        target_node = self._build_node(node.child[0])
        value_node = self._build_node(node.child[2])
        return AssignNode(target_node, value_node)

    def _build_expression_node(self, node):
        # <expression> -> <simple-expression> (rel_op <simple-expression>)?
        left = self._build_simple_expression_node(node.child[0])
        if len(node.child) == 3:
            op_token = node.child[1]
            right = self._build_simple_expression_node(node.child[2])
            op = op_token.value if isinstance(op_token, Token) else None
            return BinOpNode(left, op, right)
        return left

    def _build_simple_expression_node(self, node):
        # <simple-expression> -> <term> (add_op <term>)*
        current = self._build_term_node(node.child[0])
        i = 1
        while i < len(node.child):
            op_token = node.child[i]
            next_term = self._build_term_node(node.child[i+1])
            op = op_token.value if isinstance(op_token, Token) else None
            current = BinOpNode(current, op, next_term)
            i += 2
        return current

    def _build_term_node(self, node):
        # <term> -> <factor> (mul_op <factor>)*
        current = self._build_factor_node(node.child[0])
        i = 1
        while i < len(node.child):
            op_token = node.child[i]
            next_factor = self._build_factor_node(node.child[i+1])
            op = op_token.value if isinstance(op_token, Token) else None
            current = BinOpNode(current, op, next_factor)
            i += 2
        return current

    def _build_factor_node(self, node):
        """
        <factor> -> NUMBER | ID | STRING | '(' <expression> ')' | 'tidak' <factor> | procedure_call
        """
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
                # fallback: nested parse node (expression, procedure call, etc.)
                return self._build_node(t)

        elif len(node.child) == 2 and getattr(node.child[0], "type", "").lower() == "tidak":
            # unary 'tidak'
            factor = self._build_factor_node(node.child[1])
            return UnaryOpNode("tidak", factor)

        elif len(node.child) == 3 and getattr(node.child[0], "type", "") == "LPARENTHESIS":
            # '(' <expression> ')'
            return self._build_expression_node(node.child[1])

        else:
            # fallback umum
            return self._build_node(node.child[0])


    # ---------------------------
    # Procedure / Function call
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
                if isinstance(arg_node, BlockNode):
                    args.extend(arg_node.children)
                else:
                    args.append(arg_node)
        return ProcedureCallNode(name, args)

    def _build_if_node(self, node):
        if len(node.child) < 4:
            raise ASTBuilderError("If statement incomplete")

        condition = self._build_node(node.child[1])
        then_stmt = self._build_node(node.child[3])

        else_stmt = None
        if len(node.child) > 4:
            token = node.child[4]
            if token.value.lower() in ("selain_itu", "selain-itu"):
                else_stmt = self._build_node(node.child[5])
            else:
                raise ASTBuilderError("Unexpected token in if-statement: " + token.value)

        return IfNode(condition, then_stmt, else_stmt)

    def _build_while_node(self, node):
        """
        <while-statement> -> 'selama' <expression> 'lakukan' <statement>
        """
        condition = None
        body = None

        # iterasi semua child dari parse node while-statement
        for c in node.child:
            # Ambil expression pertama sebagai kondisi
            if c.type in ("<expression>", "<simple-expression>", "<term>", "<factor>") and condition is None:
                condition = self._build_node(c)
            # Ambil statement (compound atau tunggal) sebagai body
            elif c.type in ("<compound-statement>", "<assignment-statement>", "<if-statement>", "<for-statement>", "<while-statement>", "<repeat-statement>", "<procedure/function-call>") and body is None:
                body = self._build_node(c)

        if condition is None or body is None:
            raise ASTError("While statement incomplete", node)

        return WhileNode(condition, body)

    def _build_repeat_node(self, node):
        """
        <repeat-statement> -> 'ulangi' <statement-list> 'sampai' <expression>
        """
        body = None
        condition = None

        for c in node.child:
            if c.type == "<statement-list>":
                body = self._build_node(c)
            elif c.type in ("<expression>", "<simple-expression>", "<term>", "<factor>"):
                condition = self._build_node(c)

        if body is None or condition is None:
            raise ASTError("Repeat statement incomplete", node)

        return RepeatNode(body, condition)

    def _build_for_node(self, node):
        # Ambil ASTNode yang relevan
        var_node = self._build_node(node.child[1])      # <variable>
        start_expr = self._build_node(node.child[3])    # <expression> awal
        end_expr = self._build_node(node.child[5])      # <expression> akhir
        body_node = self._build_node(node.child[7])     # <statement> atau compound statement

        # Ambil arah: 'ke' atau 'turun_ke'
        direction_token = node.child[4]
        direction = direction_token.value.lower() if direction_token else 'ke'

        return ForNode(var_node, start_expr, end_expr, direction, body_node)

    def _build_case_node(self, node):
        expr_node = self._build_node(node.child[1])
        case_list_node = node.child[3]

        branches = []
        i = 0
        while i < len(case_list_node.child):
            constants = []

            while not (isinstance(case_list_node.child[i], Token) and case_list_node.child[i].type == "COLON"):
                child_node = self._build_node(case_list_node.child[i])
                if child_node is not None: # jujur gatau kenapa ada None
                    constants.append(child_node)
                i += 1

            i += 1  # skip COLON
            stmt_node = self._build_node(case_list_node.child[i])
            i += 1

            branches.append(CaseBranchNode(constants, stmt_node))

        return CaseNode(expr_node, branches)
