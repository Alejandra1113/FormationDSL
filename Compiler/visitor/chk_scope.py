import Compiler.utils as util
from Compiler.semantic import *
from .visitor import *
from ._def import *

__all__ = ['ScopeCheckerVisitor']


class ScopeCheckerVisitor(object):
    @on('node')
    def visit(self, node, context: Context, index):
        pass

    @when(ProgramNode)
    def visit(self, node: ProgramNode, context: ProgramContext = None, index: int = 0):
        context = context or ProgramContext()
        def_error = self.visit(node.definitions, context, index)
        # begin_error = self.visit(node.begin_with, context, index)
        return def_error  # + begin_error

    @when(DefinitionsNode)
    def visit(self, node: DefinitionsNode, context: ProgramContext, index: int = 0):
        errors = []
        for i, child in enumerate(node.functions):
            child_err = self.visit(child, context, i)
            util.update_errs(errors, child_err)
        return errors

    # @when(BeginWithNode)
    #    pass

    @when(FuncDeclarationNode)
    def visit(self, node: FuncDeclarationNode, context: ProgramContext, index: int = 0):
        errors = []
        if context.is_func_defined(node.idx, node.params):
            errors.append(f"funcion {node.idx} está ya definida")
        else:
            context.define_function(node.idx, node.params)
        new_context = context.create_child_context(index)
        for i, child in enumerate(node.body):
            child_err = self.visit(child, new_context, i)
            util.update_errs(errors, child_err)
        return errors

    @when(VarDeclarationNode)
    def visit(self, node: VarDeclarationNode, context: OtherContext, index: int = 0):
        return None

    @when(GroupVarDeclarationNode)
    def visit(self, node: GroupVarDeclarationNode, context: OtherContext, index: int = 0):
        return None

    @when(LoopNode)
    def visit(self, node: LoopNode, context: OtherContext, index: int = 0):
        errors = []
        new_context = context.create_child_context(index)
        for i, child in enumerate(node.body):
            child_err = self.visit(child, new_context, i)
            util.update_errs(errors, child_err)
        return errors

    @when(IterNode)
    def visit(self, node: IterNode, context: OtherContext, index: int = 0):
        return None

    @when(BorrowNode)
    def visit(self, node: BorrowNode, context: OtherContext, index: int = 0):
        return None

    @when(ConditionNode)
    def visit(self, node: ConditionNode, context: OtherContext, index: int = 0):
        errors = []
        new_context = context.create_child_context(index)
        for i, child in enumerate(node.body):
            child_err = self.visit(child, new_context, i)
            util.update_errs(errors, child_err)
        return errors

    @when(ConstantNode)
    def visit(self, node: ConstantNode, context: OtherContext, index: int = 0):
        return None

    @when(VariableNode)
    def visit(self, node: VariableNode, context: OtherContext, index: int = 0):
        return None

    @when(CallNode)
    def visit(self, node: CallNode, context: OtherContext, index: int = 0):
        return None

    @when(BeginCallNode)
    def visit(self, node: BeginCallNode, context: OtherContext, index: int = 0):
        return None

    @when(UnaryNode)
    def visit(self, node: UnaryNode, context: OtherContext, index: int = 0):
        return None

    @when(BinaryNode)
    def visit(self, node: BinaryNode, context: OtherContext, index: int = 0):
        return None

    @when(TernaryNode)
    def visit(self, node: TernaryNode, context: OtherContext, index: int = 0):
        return None
