import Compiler.utils as util
from Compiler.semantic.language import *
from .visitor import *
from ._def import *

__all__ = ['TypeCheckerVisitor']


class TypeCheckerVisitor(object):
    @on('node')
    def visit(self, node):
        pass

    @when(ProgramNode)
    def visit(self, node: ProgramNode, context: ProgramContext, index: int = 0):
        _, def_err = self.visit(node.definitions, context, index)
        _, beg_err = self.visit(node.begin_with, context, index)
        errors = def_err + beg_err
        return None, errors

    @when(DefinitionsNode)
    def visit(self, node: DefinitionsNode, context: ProgramContext, index: int = 0):
        errors = []
        new_context = context.get_context(index)
        for i, child in enumerate(node.functions):
            _, child_err = self.visit(child, new_context, i)
            util.update_errs(errors, child_err)
        return None, errors

    @when(BeginWithNode)
    def visit(self, node: BeginWithNode, context: ProgramContext, index: int = 0):
        errors = []
        new_context = context.get_context(index)
        for i, child in enumerate(node.step):
            _, child_err = self.visit(child, new_context, i)
            util.update_errs(errors, child_err)
        return None, errors

    @when(StepNode)
    def visit(self, node: StepNode, context: ProgramContext, index: int = 0):
        errors = []
        for child in node.instructions:
            _, child_err = self.visit(child, context, index)
            util.update_errs(errors, child_err)
        return None, errors

    @when(FuncDeclarationNode)
    def visit(self, node: FuncDeclarationNode, context: ProgramContext, index: int = 0):
        errors = []
        new_context = context.get_context(index)
        for i, child in enumerate(node.body):
            _, child_err = self.visit(child, new_context, i)
            util.update_errs(errors, child_err)
        return None, errors if len(errors) else None

    @when(VarDeclarationNode)
    def visit(self, node: VarDeclarationNode, context: OtherContext, index: int = 0):
        errors = []
        expr_type, expr_err = self.visit(node.expr, context, index)
        util.update_err_type(errors, node.type, expr_type)
        util.update_errs(errors, expr_err)
        return None, errors if len(errors) else None

    @when(GroupVarDeclarationNode)
    def visit(self, node: GroupVarDeclarationNode, context: OtherContext, index: int = 0):
        errors = []
        collec_type, collec_err = self.visit(node.collec, context, index)
        util.update_err_type(errors, node.type, collec_type)
        util.update_errs(errors, collec_err)

        init_type, init_err = self.visit(node.init, context, index)
        util.update_err_type(errors, "num", init_type)
        util.update_errs(errors, init_err)

        len_type, len_err = self.visit(node.len, context, index)
        util.update_err_type(errors, "num", len_type)
        util.update_errs(errors, len_err)
        return None, errors if len(errors) else None

    @when(LoopNode)
    def visit(self, node: LoopNode, context: OtherContext, index: int = 0):
        errors = []
        expr_type, expr_err = self.visit(node.expr, context.parent)
        util.update_err_type(errors, "boolean", expr_type)
        util.update_errs(errors, expr_err)

        new_context = context.get_context(index)
        for i, child in enumerate(node.body):
            _, child_err = self.visit(child, new_context, i)
            util.update_errs(errors, child_err)
        return None, errors if len(errors) else None

    @when(IterNode)
    def visit(self, node: IterNode, context: OtherContext, index: int = 0):
        errors = []
        expr_type, expr_err = self.visit(node.expr, context, index)
        util.update_err_type(errors, "vector", expr_type)
        util.update_errs(errors, expr_err)
        return None, errors if len(errors) else None

    @when(BorrowNode)
    def visit(self, node: BorrowNode, context: OtherContext, index: int = 0):
        errors = []
        init_type, init_err = self.visit(node.init, context, index)
        util.update_err_type(errors, "num", init_type)
        util.update_errs(errors, init_err)

        len_type, len_err = self.visit(node.len, context, index)
        util.update_err_type(errors, "num", len_type)
        util.update_errs(errors, len_err)
        return None, errors if len(errors) else None

    @when(ConditionNode)
    def visit(self, node: ConditionNode, context: OtherContext, index: int = 0):
        errors = []
        expr_type, expr_err = self.visit(
            node.expr, context, index) if node.expr else ("boolean", None)
        util.update_err_type(errors, "boolean", expr_type)
        util.update_errs(errors, expr_err)

        new_context = context.get_context(index)
        for i, child in enumerate(node.body):
            _, child_err = self.visit(child, new_context, i)
            util.update_errs(errors, child_err)
        return errors if len(errors) else None if len(errors) else None

    @when(ConstantNode)
    def visit(self, node: ConstantNode, context: OtherContext, index: int = 0):
        return node.type, None

    @when(VariableNode)
    def visit(self, node: VariableNode, context: OtherContext, index: int = 0):
        type_var = context.get_variable_info(node.id).type
        return type_var, None

    @when(AssignNode)
    def visit(self, node: AssignNode, context: OtherContext, index: int = 0):
        errors = []
        type_var = context.get_variable_info(node.id).type
        expr_type, expr_err = self.visit(node.expr, context, index)
        util.update_err_type(errors, type_var, expr_type)
        util.update_errs(errors, expr_err)
        return errors

    @when(SetIndexNode)
    def visit(self, node: SetIndexNode, context: OtherContext, index: int = 0):
        errors = []
        type_var = context.get_variable_info(node.id).type
        util.update_err_type(errors, "Array", type_var)
        expr_type, expr_err = self.visit(node.expr, context, index)
        if not len(errors):
            type_index = type_var.type
            util.update_err_type(errors, type_index, expr_type)
        util.update_errs(errors, expr_err)
        return errors

    @when(CallNode)
    def visit(self, node: CallNode, context: OtherContext, index: int = 0):
        errors = []
        func_info = context.get_func_info(node.lex, node.args)
        for get_arg, set_arg in zip(node.args, func_info.args):
            get_type, _ = self.visit(get_arg)
            set_type = set_arg.type
            util.update_err_type(errors, set_type, get_type)
        return None, errors if len(errors) else None

    @when(BeginCallNode)
    def visit(self, node: BeginCallNode, context: OtherContext, index: int = 0):
        errors = []
        func_info = context.get_func_info(node.lex, node.args)
        for get_arg, set_arg in zip(node.args, func_info.args):
            get_type, _ = self.visit(get_arg)
            set_type = set_arg.type
            util.update_err_type(errors, set_type, get_type)

        poss_type, poss_err = self.visit(node.poss, context, index)
        util.update_err_type(errors, "vector", poss_type)
        util.update_errs(errors, poss_err)

        rot_type, rot_err = self.visit(node.rot, context, index)
        util.update_err_type(errors, "vector", rot_type)
        util.update_errs(errors, rot_err)
        return None, errors if len(errors) else None

    @when(UnaryNode)
    def visit(self, node: UnaryNode, context: OtherContext, index: int = 0):
        errors = []
        expr_type, expr_err = self.visit(node.expr, context, index)
        util.update_err_type(errors, node.type, expr_type)
        util.update_errs(errors, expr_err)
        return errors if len(errors) else None

    @when(BinaryNode)
    def visit(self, node: BinaryNode, context: OtherContext, index: int = 0):
        errors = []
        left_type, left_err = self.visit(node.left, context, index)
        util.update_err_type(errors, node.type, left_type)
        util.update_errs(errors, left_err)

        right_type, right_err = self.visit(node.right, context, index)
        util.update_err_type(errors, node.type, right_type)
        util.update_errs(errors, right_err)
        return errors if len(errors) else None

    @when(TernaryNode)
    def visit(self, node: TernaryNode, context: OtherContext, index: int = 0):
        errors = []
        left_type, left_err = self.visit(node.left, context, index)
        util.update_err_type(errors, node.type, left_type)
        util.update_errs(errors, left_err)

        expr_type, expr_err = self.visit(node.expr, context, index)
        util.update_err_type(errors, node.type, expr_type)
        util.update_errs(errors, expr_err)

        right_type, right_err = self.visit(node.right, context, index)
        util.update_err_type(errors, node.type, right_type)
        util.update_errs(errors, right_err)
        return errors if len(errors) else None
