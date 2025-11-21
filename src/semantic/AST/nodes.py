from .ast_node import ASTNode

class ProgramNode(ASTNode):
    def __init__(self, name, declarations=None, block=None):
        super().__init__()
        self.name = name
        self.declarations = declarations if declarations else []
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
        return f"VarDecl(name='{self.name}', type='{self.vartype}')"

class AssignNode(ASTNode):
    def __init__(self, target, value):
        super().__init__()
        self.target = target
        self.value = value

    def __repr__(self):
        return f"Assign(target: {self.target}, value: {self.value})"

class VarNode(ASTNode):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __repr__(self):
        return f"Var('{self.name}')"

class NumNode(ASTNode):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __repr__(self):
        return f"Num({self.value})"

class BinOpNode(ASTNode):
    def __init__(self, left, op, right):
        super().__init__()
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f"BinOp(op='{self.op}', left={self.left}, right={self.right})"

class ProcedureCallNode(ASTNode):
    def __init__(self, name, args=None):
        super().__init__()
        self.name = name
        self.args = args if args else []

    def __repr__(self):
        return f"ProcedureCall(name='{self.name}', args={self.args})"

class StringNode(ASTNode):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __repr__(self):
        return f"String({self.value})"
