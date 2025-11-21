from .ast_node import ASTNode

class ProgramNode(ASTNode):
    def __init__(self, name, declarations=None, block=None):
        super().__init__()
        self.name = name
        self.declarations = declarations
        self.block = block
        if self.declarations:
            self.add_child(DeclarationsNode(self.declarations))
        if self.block:
            self.add_child(self.block)

    def __repr__(self):
        return f"ProgramNode(name='{self.name}')"

class BlockNode(ASTNode):
    def __init__(self, statements=None):
        super().__init__()
        self.statements = statements if statements else []
        for stmt in self.statements:
            self.add_child(stmt)

    def __repr__(self):
        return "Block"

class DeclarationsNode(ASTNode):
    def __init__(self, declarations=None):
        super().__init__()
        self.declarations = declarations if declarations else []
        for d in self.declarations:
            self.add_child(d)

    def __repr__(self):
        return "Declarations"

class VarDeclNode(ASTNode):
    def __init__(self, name, vartype):
        super().__init__()
        self.name = name
        self.vartype = vartype

    def __repr__(self):
        return f"VarDeclNode(name='{self.name}', type='{self.vartype}')"

class AssignNode(ASTNode):
    def __init__(self, target, value):
        super().__init__()
        self.target = target
        self.value = value
        self.add_child(self.target)
        self.add_child(self.value)

    def __repr__(self):
        return f"AssignNode(target: {self.target}, value: {self.value})"

class VarNode(ASTNode):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __repr__(self):
        return f"VarNode('{self.name}')"

class NumNode(ASTNode):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __repr__(self):
        return f"NumNode({self.value})"

class UnaryOpNode(ASTNode):
    def __init__(self, op, operand):
        super().__init__()
        self.op = op
        self.operand = operand
        self.add_child(operand)

    def __repr__(self):
        return f"UnaryOpNode(op='{self.op}', operand={self.operand})"

class BinOpNode(ASTNode):
    def __init__(self, left, op, right):
        super().__init__()
        self.left = left
        self.op = op
        self.right = right

        self.add_child(left)
        self.add_child(right)

    def __repr__(self):
        return f"BinOpNode(op='{self.op}', left={self.left}, right={self.right})"

class ProcedureCallNode(ASTNode):
    def __init__(self, name, args=None):
        super().__init__()
        self.name = name
        self.args = args if args else []
        for a in self.args:
            self.add_child(a)

    def __repr__(self):
        return f"ProcedureCallNode(name='{self.name}', args={self.args})"

class StringNode(ASTNode):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __repr__(self):
        return f"StringNode({self.value})"

class IfNode(ASTNode):
    def __init__(self, condition, then_block, else_block=None):
        super().__init__()
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block
        self.add_child(condition)
        self.add_child(then_block)
        if else_block:
            self.add_child(else_block)

    def __repr__(self):
        return f"IfNode(condition={self.condition}, then={self.then_block}, else={self.else_block})"

class WhileNode(ASTNode):
    def __init__(self, condition, body):
        super().__init__()
        self.condition = condition
        self.body = body
        self.add_child(condition)
        self.add_child(body)

    def __repr__(self):
        return f"WhileNode(condition={self.condition}, body={self.body})"

class RepeatNode(ASTNode):
    def __init__(self, body, condition):
        super().__init__()
        self.body = body
        self.condition = condition
        self.add_child(body)
        self.add_child(condition)

    def __repr__(self):
        return f"RepeatNode(body={self.body}, until={self.condition})"

class ForNode(ASTNode):
    def __init__(self, var_node, start_expr, end_expr, direction, body):
        super().__init__()
        self.var_node = var_node
        self.start_expr = start_expr
        self.end_expr = end_expr
        self.direction = direction
        self.body = body

        self.add_child(var_node)
        self.add_child(start_expr)
        self.add_child(end_expr)
        self.add_child(body)

    def __repr__(self):
        return f"ForNode({self.var_node} := {self.start_expr} {self.direction} {self.end_expr}, body={self.body})"

class CaseNode(ASTNode):
    def __init__(self, expr_node, branches):
        super().__init__()
        self.expr_node = expr_node
        self.branches = branches

        self.add_child(expr_node)
        for branch in branches:
            self.add_child(branch)

    def __repr__(self):
        repr_branches = []
        for branch in self.branches:  # <-- langsung objek
            repr_constants = ", ".join([str(c) for c in branch.constants])
            repr_branches.append(f"[{repr_constants}] => {branch.statement}")
        return f"CaseNode(expr={self.expr_node}, branches={{ {', '.join(repr_branches)} }})"

class CaseBranchNode(ASTNode):
    def __init__(self, constants, statement):
        super().__init__()
        self.constants = constants
        self.statement = statement

        for c in constants:
            self.add_child(c)
        self.add_child(statement)

    def __repr__(self):
        consts = ", ".join([str(c) for c in self.constants])
        return f"CaseBranchNode([{consts}] => {self.statement})"
