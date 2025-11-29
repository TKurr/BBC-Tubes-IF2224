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
        return f"ProgramNode(name: '{self.name}')"

class BlockNode(ASTNode):
    def __init__(self, statements=None):
        super().__init__()
        self.statements = statements or []
        self.children.extend(self.statements)

    def __repr__(self):
        return f"Block"

class DeclarationsNode(ASTNode):
    def __init__(self, declarations=None):
        super().__init__()
        self.declarations = declarations or []
        self.children.extend(self.declarations)

    def __repr__(self):
        return "Declarations"

class ConstDeclNode(ASTNode):
    def __init__(self, name, consttype):
        super().__init__()
        self.name = name
        self.consttype = consttype

    def __repr__(self):
        return f"ConstDecl(name='{self.name}', type='{self.consttype}')"

class VarDeclNode(ASTNode):
    def __init__(self, name, vartype):
        super().__init__()
        self.name = name
        self.vartype = vartype

    def __repr__(self):
        return f"VarDecl('{self.name}')"

class TypeDeclarationNode(ASTNode):
    def __init__(self, name, type_node):
        super().__init__()
        self.name = name
        self.type_node = type_node
        self.children.append(type_node)

    def __repr__(self):
        return f"TypeDecl(name='{self.name}')"

class AssignNode(ASTNode):
    def __init__(self, target, value):
        super().__init__()
        self.target = target
        self.value = value
        self.children.extend([target, value])

    def __repr__(self):
        # buat VarNode (ambil nama)
        t_str = self.target.name if hasattr(self.target, 'name') else "target"

        # buat NumNode (ambil value)
        v_str = self.value.value if hasattr(self.value, 'value') else "expr"

        return f"Assign('{t_str}' := {v_str})"

class VarNode(ASTNode):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __repr__(self):
        return f"target '{self.name}'"

class NumNode(ASTNode):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __repr__(self):
        return f"value {self.value}"

class StringNode(ASTNode):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __repr__(self):
        return f"String ({self.value})"

class BooleanNode:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Boolean ({self.value})"

class UnaryOpNode(ASTNode):
    def __init__(self, op, operand):
        super().__init__()
        self.op = op
        self.operand = operand
        self.children.append(operand)

    def __repr__(self):
        return f"UnaryOp(op='{self.op}')"

class BinOpNode(ASTNode):
    def __init__(self, left, op, right):
        super().__init__()
        self.left = left
        self.op = op
        self.right = right
        self.children.extend([left, right])

    def __repr__(self):
        return f"BinOp '{self.op}'"

class ProcedureDeclNode(ASTNode):
    def __init__(self, name, params, block):
        self.name = name
        self.params = params
        self.block = block

    def __repr__(self):
        return f"ProcedureDecl(params='{self.params}', block='{self.block}')"

class FunctionDeclNode(ASTNode):
    def __init__(self, name, params, return_type, block):
        self.name = name
        self.params = params
        self.return_type = return_type
        self.block = block

    def __repr__(self):
        return f"FunctonDecl(params='{self.params}', block='{self.block}', return_type='{self.return_type}')"

class ParamNode(ASTNode):
    def __init__(self, names, type_node, is_var=False):
        super().__init__()
        self.names = names
        self.type_node = type_node
        self.is_var = is_var

    def __repr__(self):
        return f"Param(names='{self.names}', type='{self.type_node}', is_var={self.is_var})"

class ProcedureFunctionCallNode(ASTNode):
    def __init__(self, name, args=None):
        super().__init__()
        self.name = name
        self.args = args or []
        self.children.extend(self.args)

    def __repr__(self):
        return f"ProcedureFunctionCall('{self.name}')"

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
        return f"If(condition={self.condition}, then={self.then_block}, else={self.else_block})"

class WhileNode(ASTNode):
    def __init__(self, condition, body):
        super().__init__()
        self.condition = condition
        self.body = body
        self.children.extend([condition, body])

    def __repr__(self):
        return f"While(condition={self.condition}, body={self.body})"

class RepeatNode(ASTNode):
    def __init__(self, body, condition):
        super().__init__()
        self.body = body
        self.condition = condition
        self.children.extend([body, condition])

    def __repr__(self):
        return f"Repeat(body={self.body}, until={self.condition})"

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
        return f"For({self.var_node} := {self.start_expr} {self.direction} {self.end_expr}, body={self.body})"

class CaseBranchNode(ASTNode):
    def __init__(self, constants, statement):
        super().__init__()
        self.constants = constants
        self.statement = statement
        self.children.extend(constants + [statement])

    def __repr__(self):
        consts = ", ".join(str(c) for c in self.constants)
        return f"CaseBranch([{consts}] => {self.statement})"

class CaseNode(ASTNode):
    def __init__(self, expr_node, branches):
        super().__init__()
        self.expr_node = expr_node
        self.branches = branches
        self.children.append(expr_node)
        self.children.extend(branches)

    def __repr__(self):
        return f"Case(expr={self.expr_node}, branches={self.branches})"

class ArrayTypeNode(ASTNode):
    def __init__(self, base_type, bounds):
        super().__init__()
        self.base_type = base_type
        self.bounds = bounds
    def __repr__(self):
        return f"ArrayType(base_type={self.base_type}, bounds={self.bounds})"

class ArrayAccessNode(ASTNode):
    def __init__(self, array, index):
        self.array = array
        self.index = index

    def __repr__(self):
        return f"ArrayAccess(array={self.array}, index={self.index})"

class RecordFieldNode(ASTNode):
    def __init__(self, name, type_):
        super().__init__()
        self.name = name
        self.type_ = type_

    def __repr__(self):
        return f"RecordField('{self.name}')"

class RecordTypeNode(ASTNode):
    def __init__(self, fields=None):
        super().__init__()
        self.fields = fields or []
        self.children.extend(self.fields)

    def __repr__(self):
        return f"RecordType(fields={self.fields})"

class RangeTypeNode(ASTNode):
    def __init__(self, lower, upper):
        super().__init__()
        self.lower = lower
        self.upper = upper

    def __repr__(self):
        return f"RangeType({self.lower}-{self.upper})"
