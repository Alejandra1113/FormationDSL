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
    def __init__(self, idx, params, params_types, body):
        self.id = idx
        self.params = params
        self.params_types = params_types
        self.body = body


class StepNode(DeclarationNode):
    def __init__(self, instructions):
        self.instructions = instructions


class VarDeclarationNode(DeclarationNode):
    def __init__(self, idx, type, expr):
        self.id = idx
        self.type = type
        self.expr = expr


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
    def __init__(self, lex):
        self.lex = lex


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


class ConstantNode(AtomicNode):
    pass


class VariableNode(AtomicNode):
    pass


class InstantiateNode(AtomicNode):
    pass


class CallNode(AtomicNode):
    def __init__(self, idx, args):
        AtomicNode.__init__(self, idx)
        self.args = args


class BeginCallNode(AtomicNode):
    def __init__(self, idx, poss, rot, args):
        AtomicNode.__init__(self, idx)
        self.args = args
        self.poss = poss
        self.rot = rot


class GetIndexNode(UnaryNode):
    def __init__(self, idx, index, expr):
        self.id = idx
        self.index = index
        self.expr = expr


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



production_to_node = {
    0: ProgramNode,
    1: DefinitionsNode,
    2: None,
    3: None,
    4: None,
    5: None,
    6: None,
    7: LoopNode,
    8: ConditionNode,
    9: IterNode,
   10: BorrowNode,
   11: LinkNode,
   12: CallNode,
   13: CallNode,
   14: None,
   15: None, 
   16: None,
   17: None,
   18: 
    
}