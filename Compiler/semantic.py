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
    def __init__(self, num, expressions):
        self.num = num
        self.expressions = expressions


class FuncDeclarationNode(Node):
    def __init__(self, idx, params, body):
        self.id = idx
        self.params = params
        self.body = body


class StatementNode(Node):
    pass


class ExpressionNode(Node):
    pass


class VarDeclarationNode(StatementNode):
    def __init__(self, type, idx, expr):
        self.type = type
        self.id = idx
        self.expr = expr


class GroupVarDeclarationNode(StatementNode):
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
    def __init__(self, expr, body1, body2):
        self.expr = expr
        self.body1 = body1
        self.body2 = body2


class AtomicNode(ExpressionNode):
    def __init__(self, lex):
        self.lex = lex


class TypeNode(AtomicNode):
    def __init__(self, type, lex):
        AtomicNode.__init__(self, lex)
        self.type = type


class UnaryNode(ExpressionNode):
    def __init__(self, expr):
        self.expr = expr


class BinaryNode(ExpressionNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right


class TernaryNode(ExpressionNode):
    def __init__(self, left, right, expr):
        self.left = left
        self.right = right
        self.expr = expr


class VariableNode(AtomicNode):
    pass


class CallNode(AtomicNode):
    def __init__(self, idx, args):
        AtomicNode.__init__(self, idx)
        self.args = args


class BeginCallNode(CallNode):
    def __init__(self, idx, poss, rot, args):
        CallNode.__init__(self, idx, args)
        self.poss = poss
        self.rot = rot


class ConstantNode(TypeNode):
    pass


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


class AndNode(BinaryNode):
    pass


class OrNode(BinaryNode):
    pass


class EqNode(BinaryNode):
    pass


class EqlNode(BinaryNode):
    pass


class EqgNode(BinaryNode):
    pass


class GtNode(BinaryNode):
    pass


class LtNode(BinaryNode):
    pass


class LinkNode(TernaryNode):
    pass
