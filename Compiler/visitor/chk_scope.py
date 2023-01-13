import Compiler.utils as util
from Compiler.semantic.language import *
from .visitor import *
from ._def import *

__all__ = ['ScopeCheckerVisitor']


class ScopeCheckerVisitor(object):
    @on('node')
    def visit(self, node, context, index):
        pass

    @when(ProgramNode)
    def visit(self, node: ProgramNode, context: ProgramContext = None, index: int = 0):
        context = context or ProgramContext()
        def_error = self.visit(node.definitions, context)
        begin_error = self.visit(node.begin_with, context)
        return def_error + begin_error

    @when(DefinitionsNode)
    def visit(self, node: DefinitionsNode, context: ProgramContext, index: int = 0):
        errors = []
        context.set_define_context()
        for i, child in enumerate(node.functions):
            child_err = self.visit(child, context.define_context, i)
            util.update_errs(errors, child_err)
        return errors

    @when(BeginWithNode)
    def visit(self, node: BeginWithNode, context: ProgramContext, index: int = 0):
        errors = []
        context.set_begin_context(node.num)
        for i, child in enumerate(node.step):
            child_err = self.visit(child, context.begin_context, i)
            util.update_errs(errors, child_err)
        return errors

    @when(StepNode)
    def visit(self, node: StepNode, context: BeginContext, index: int = 0):
        _ = context.create_child_context(index)
        return None

    @when(FuncDeclarationNode)
    def visit(self, node: FuncDeclarationNode, context: DefineContext, index: int = 0):
        errors = []
        if context.is_func_defined(node.id, node.params):
            errors.append(f"funcion {node.id} está ya definida")
        else:
            context.define_function(node.id, node.params)
        new_context = context.create_child_context(index)
        new_context.define_variable("G", "group")
        for i, child in enumerate(node.body):
            child_err = self.visit(child, new_context, i)
            util.update_errs(errors, child_err)
        return errors

    @when(VarDeclarationNode)
    def visit(self, node: VarDeclarationNode, context: OtherContext, index: int = 0):
        return None

    @when(ArrayDeclarationNode)
    def visit(self, node: ArrayDeclarationNode, context: OtherContext, index: int = 0):
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

    @when(ExpressionNode)
    def visit(self, node: ExpressionNode, context: OtherContext, index: int = 0):
        return None
