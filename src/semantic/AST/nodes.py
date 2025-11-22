from .ast_node import ASTNode

class ProgramNode(ASTNode):
    def __init__(self, name, declarations=None, block=None):
        super().__init__()
        self.name = name
        self.declarations = declarations or []
        self.block = block

        if self.declarations:
            self.children.extend(self.declarations)
        if self.block:
            self.children.append(self.block)

    def __repr__(self):
        return f"ProgramNode(name='{self.name}')"

class BlockNode(ASTNode):
    def __init__(self, statements=None):
        super().__init__()
        self.statements = statements or []
        self.children.extend(self.statements)

    def __repr__(self):
        return "BlockNode"

class DeclarationsNode(ASTNode):
    def __init__(self, declarations=None):
        super().__init__()
        self.declarations = declarations or []
        self.children.extend(self.declarations)

    def __repr__(self):
        return "DeclarationsNode"

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
        self.children.extend([target, value])

    def __repr__(self):
        return f"AssignNode(target={self.target}, value={self.value})"

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

class StringNode(ASTNode):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __repr__(self):
        return f"StringNode({self.value})"

class UnaryOpNode(ASTNode):
    def __init__(self, op, operand):
        super().__init__()
        self.op = op
        self.operand = operand
        self.children.append(operand)

    def __repr__(self):
        return f"UnaryOpNode(op='{self.op}', operand={self.operand})"

class BinOpNode(ASTNode):
    def __init__(self, left, op, right):
        super().__init__()
        self.left = left
        self.op = op
        self.right = right
        self.children.extend([left, right])

    def __repr__(self):
        return f"BinOpNode(op='{self.op}', left={self.left}, right={self.right})"

class ProcedureCallNode(ASTNode):
    def __init__(self, name, args=None):
        super().__init__()
        self.name = name
        self.args = args or []
        self.children.extend(self.args)

    def __repr__(self):
        return f"ProcedureCallNode(name='{self.name}', args={self.args})"

class IfNode(ASTNode):
    def __init__(self, condition, then_block, else_block=None):
        super().__init__()
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block
        self.children.extend([condition, then_block])
        if else_block:
            self.children.append(else_block)

    def __repr__(self):
        return f"IfNode(condition={self.condition}, then={self.then_block}, else={self.else_block})"

class WhileNode(ASTNode):
    def __init__(self, condition, body):
        super().__init__()
        self.condition = condition
        self.body = body
        self.children.extend([condition, body])

    def __repr__(self):
        return f"WhileNode(condition={self.condition}, body={self.body})"

class RepeatNode(ASTNode):
    def __init__(self, body, condition):
        super().__init__()
        self.body = body
        self.condition = condition
        self.children.extend([body, condition])

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
        self.children.extend([var_node, start_expr, end_expr, body])

    def __repr__(self):
        return f"ForNode({self.var_node} := {self.start_expr} {self.direction} {self.end_expr}, body={self.body})"

class CaseBranchNode(ASTNode):
    def __init__(self, constants, statement):
        super().__init__()
        self.constants = constants
        self.statement = statement
        self.children.extend(constants + [statement])

    def __repr__(self):
        consts = ", ".join(str(c) for c in self.constants)
        return f"CaseBranchNode([{consts}] => {self.statement})"

class CaseNode(ASTNode):
    def __init__(self, expr_node, branches):
        super().__init__()
        self.expr_node = expr_node
        self.branches = branches
        self.children.append(expr_node)
        self.children.extend(branches)

    def __repr__(self):
        return f"CaseNode(expr={self.expr_node}, branches={self.branches})"

class ArrayTypeNode(ASTNode):
    def __init__(self, base_type, bounds):
        super().__init__()
        self.base_type = base_type 
        self.bounds = bounds      
    def __repr__(self):
        return f"ArrayTypeNode(base_type={self.base_type}, bounds={self.bounds})"

class ArrayAccessNode(ASTNode):
    def __init__(self, array, index):
        self.array = array    
        self.index = index    

    def __repr__(self):
        return f"ArrayAccessNode(array={self.array}, index={self.index})"
