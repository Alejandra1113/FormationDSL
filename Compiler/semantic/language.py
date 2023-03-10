class Node:
    pass


class ProgramNode(Node):
    def __init__(self, definitions, begin_with):
        self.definitions = definitions
        self.begin_with = begin_with


class DefinitionsNode(Node):
    def __init__(self, functions):
        self.functions = functions


class BeginWithNode(Node):
    def __init__(self, num, step):
        self.num = num
        self.step = step


class DeclarationNode(Node):
    pass


class StatementNode(Node):
    pass


class ExpressionNode(Node):
    pass


class FuncDeclarationNode(DeclarationNode):
    def __init__(self, idx, params, body):
        self.id = idx
        self.params = params
        self.body = body


class StepNode(DeclarationNode):
    def __init__(self, instructions):
        self.instructions = instructions


class VarDeclarationNode(DeclarationNode):
    def __init__(self, idx, type, expr):
        self.id = idx
        self.type = type
        self.expr = expr


class ArrayDeclarationNode(DeclarationNode):
    def __init__(self, type, id, expr):
        self.type = type
        self.id = id
        self.expr = expr


class TypeNode(DeclarationNode):
    def __init__(self, name):
        self.name = name


class ParamNode(DeclarationNode):
    def __init__(self, idx, type):
        self.idx = idx
        self.type = type


class ParamArrayNode(DeclarationNode):
    def __init__(self, idx, type):
        self.idx = idx
        self.type = type


class GroupVarDeclarationNode(DeclarationNode):
    def __init__(self, type, idx, collec, init, len):
        self.type = type
        self.id = idx
        self.collec = collec
        self.init = init
        self.len = len


class LoopNode(StatementNode):
    def __init__(self, expr, body):
        self.expr = expr
        self.body = body


class ArrayNode(StatementNode):
    def __init__(self, elements, return_type = None):
        self.elements = elements
        self.return_type = return_type


class IterNode(StatementNode):
    def __init__(self, collec, expr, dir):
        self.collec = collec
        self.expr = expr
        self.dir = dir


class BorrowNode(StatementNode):
    def __init__(self, from_collec, to_collec, init, len):
        self.from_collec = from_collec
        self.to_collec = to_collec
        self.init = init
        self.len = len


class ConditionNode(StatementNode):
    def __init__(self, expr, body):
        self.expr = expr
        self.body = body


class AssignNode(ExpressionNode):
    def __init__(self, idx, expr):
        self.id = idx
        self.expr = expr


class SetIndexNode(ExpressionNode):
    def __init__(self, idx, index, expr):
        self.id = idx
        self.index = index
        self.expr = expr


class AtomicNode(ExpressionNode):
    def __init__(self, lex, return_type = None):
        self.lex = lex
        self.return_type = return_type


class UnaryNode(ExpressionNode):
    def __init__(self, expr, return_type = None):
        self.expr = expr
        self.return_type = return_type


class BinaryNode(ExpressionNode):
    def __init__(self, left, right, return_type = None):
        self.left = left
        self.right = right
        self.return_type = return_type


class TernaryNode(ExpressionNode):
    def __init__(self, left, right, expr):
        self.left = left
        self.right = right
        self.expr = expr


class ConstantNode(AtomicNode):
    def __init__(self, lex, type, return_type=None):
        self.type = type
        AtomicNode.__init__(self, lex, return_type)

class VariableNode(AtomicNode):
    pass

class InstantiateNode(AtomicNode):
    pass

class SpecialNode(AtomicNode):
    pass

class DynamicCallNode(AtomicNode):
    def __init__(self, idx, head, args, return_type = None):
        AtomicNode.__init__(self, idx, return_type)
        self.head = head
        self.args = args


class CallNode(AtomicNode):
    def __init__(self, idx, args, return_type = None):
        AtomicNode.__init__(self, idx, return_type)
        self.args = args


class BeginCallNode(AtomicNode):
    def __init__(self, idx, poss, rot, args):
        AtomicNode.__init__(self, idx)
        self.args = args
        self.poss = poss
        self.rot = rot


class NotNode(UnaryNode):
    pass


class PlusNode(BinaryNode):
    pass


class MinusNode(BinaryNode):
    pass


class StarNode(BinaryNode):
    pass


class DivNode(BinaryNode):
    pass


class ModNode(BinaryNode):
    pass


class VectNode(BinaryNode):
    pass


class BinaryLogicNode(BinaryNode):
    pass


class AndNode(BinaryLogicNode):
    pass


class OrNode(BinaryLogicNode):
    pass


class EqNode(BinaryNode):
    pass


class NonEqNode(BinaryNode):
    pass


class EqlNode(NonEqNode):
    pass


class EqgNode(NonEqNode):
    pass


class GtNode(NonEqNode):
    pass


class LtNode(NonEqNode):
    pass


class GetIndexNode(BinaryNode):
    pass


class SliceNode(BinaryNode):
    pass


class LinkNode(TernaryNode):
    pass
