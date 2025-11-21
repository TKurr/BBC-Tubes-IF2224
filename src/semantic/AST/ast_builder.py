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

    def _build_node(self, node):

        def token_value(n):
            return n.value if isinstance(n, Token) else None

        # ============================================================
        # TERMINAL TOKENS
        # ============================================================
        if isinstance(node, Token):
            if node.type == "NUMBER":
                return NumNode(node.value)

            elif node.type == "STRING_LITERAL":
                return StringNode(node.value)

            elif node.type == "CHAR_LITERAL":
                return StringNode(node.value)

            elif node.type == "IDENTIFIER":
                return VarNode(node.value)

            else:
                return None   # operator or keyword

        # ============================================================
        # PARSENODE
        # ============================================================
        if isinstance(node, ParseNode):

            # -------------------------------
            # <program>
            # -------------------------------
            if node.type == "<program>":
                prog_name = None
                decl_node = None
                block_node = None

                for c in node.child:
                    if c.type == "<program-header>":
                        tok = next((t for t in c.child
                                    if isinstance(t, Token)
                                    and t.type == "IDENTIFIER"), None)
                        if tok is None:
                            raise ASTError("Program must have an identifier", c)
                        prog_name = tok.value

                    elif c.type == "<declaration-part>":
                        decl_node = self._build_node(c)

                    elif c.type == "<compound-statement>":
                        block_node = self._build_node(c)

                if block_node is None:
                    raise ASTError("Program missing compound statement (mulai ... selesai)", node)

                return ProgramNode(
                    name=prog_name,
                    declarations=decl_node.children if decl_node else [],
                    block=block_node
                )

            # -------------------------------
            # <declaration-part>
            # -------------------------------
            elif node.type == "<declaration-part>":
                decls = []
                for c in node.child:
                    child_decl = self._build_node(c)
                    if child_decl:
                        if isinstance(child_decl, DeclarationsNode):
                            decls.extend(child_decl.children)
                        else:
                            decls.append(child_decl)
                return DeclarationsNode(decls)

            # -------------------------------
            # <var-declaration>
            # -------------------------------
            elif node.type == "<var-declaration>":
                identifiers_node = next((c for c in node.child if c.type == "<identifier-list>"), None)
                type_node        = next((c for c in node.child if c.type == "<type>"), None)

                if not identifiers_node or not type_node:
                    raise ASTError("Variable declaration incomplete", node)

                type_token = next((t for t in type_node.child if isinstance(t, Token)), None)
                if not type_token:
                    raise ASTError("Variable declaration missing type token", type_node)

                vartype = type_token.value
                decls = []

                for ident in identifiers_node.child:
                    if isinstance(ident, Token) and ident.type == "IDENTIFIER":
                        decls.append(VarDeclNode(ident.value, vartype))

                if not decls:
                    raise ASTError("Identifier list in declaration empty", identifiers_node)

                return DeclarationsNode(decls)

            # -------------------------------
            # <compound-statement>
            # -------------------------------
            elif node.type == "<compound-statement>":
                stmts = []
                for c in node.child:
                    if hasattr(c, "type") and c.type not in ["KEYWORD"]:
                        stmt_node = self._build_node(c)
                        if stmt_node:
                            if isinstance(stmt_node, BlockNode):
                                stmts.extend(stmt_node.children)
                            else:
                                stmts.append(stmt_node)
                return BlockNode(stmts)

            # -------------------------------
            # <assignment-statement>
            # -------------------------------
            elif node.type == "<assignment-statement>":

                if len(node.child) < 3:
                    raise ASTError("Assignment statement incomplete", node)

                target_node = self._build_node(node.child[0])
                if target_node is None:
                    raise ASTError("Assignment target invalid", node.child[0])

                value_node = self._build_node(node.child[2])
                if value_node is None:
                    raise ASTError("Assignment value invalid", node.child[2])

                return AssignNode(target_node, value_node)

            # -------------------------------
            # EXPRESSIONS (recursive)
            # -------------------------------
            elif node.type in ["<expression>", "<simple-expression>", "<term>", "<factor>"]:

                # Single child (simple pass-through)
                if len(node.child) == 1:
                    return self._build_node(node.child[0])

                # Binary op: must be 3 children
                if len(node.child) == 3:
                    left = self._build_node(node.child[0])
                    op_token = node.child[1]
                    right = self._build_node(node.child[2])

                    if left is None or right is None:
                        raise ASTError("Binary operator missing operand", node)

                    op = token_value(op_token)
                    if op is None:
                        raise ASTError("Binary operator missing operator token", op_token)

                    return BinOpNode(left, op, right)

                # Other weird cases: reject
                raise ASTError(f"Invalid expression structure: {node.child}", node)

            # -------------------------------
            # PROCEDURE / FUNCTION CALL
            # -------------------------------
            elif node.type == "<procedure/function-call>":
                name_token = next((t for t in node.child
                                   if isinstance(t, Token)
                                   and t.type == "IDENTIFIER"), None)

                if name_token is None:
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

            # -------------------------------
            # <variable>
            # -------------------------------
            elif node.type == "<variable>":
                var_token = next((t for t in node.child if isinstance(t, Token)), None)
                if not var_token:
                    raise ASTError("Variable node missing identifier", node)
                return VarNode(var_token.value)

            # -------------------------------
            # <number> / <string-literal>
            # -------------------------------
            elif node.type == "<number>":
                v = token_value(node)
                if v is None:
                    raise ASTError("Invalid number literal", node)
                return NumNode(v)

            elif node.type == "<string-literal>":
                v = token_value(node)
                if v is None:
                    raise ASTError("Invalid string literal", node)
                return StringNode(v)

            # -------------------------------
            # DEFAULT: flatten children
            # -------------------------------
            children_ast = []
            for c in node.child:
                child_ast = self._build_node(c)
                if child_ast:
                    if isinstance(child_ast, BlockNode):
                        children_ast.extend(child_ast.children)
                    else:
                        children_ast.append(child_ast)

            if len(children_ast) == 1:
                return children_ast[0]
            return BlockNode(children_ast)
