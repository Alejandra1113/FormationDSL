from Compiler.semantic.types import Type, Array
import Compiler.utils as util
from Compiler.semantic.language import *
from .visitor import *
from ._def import *

__all__ = ['SemanticCheckerVisitor']


class SemanticCheckerVisitor(object):
    @on('node')
    def visit(self, node, context: Context, index):
        pass

    @when(ProgramNode)
    def visit(self, node: ProgramNode, context: ProgramContext, index: int = 0):
        def_error = self.visit(node.definitions, context, index)
        begin_error = self.visit(node.begin_with, context, index)
        return def_error + begin_error

    @when(DefinitionsNode)
    def visit(self, node: DefinitionsNode, context: ProgramContext, index: int = 0):
        errors = []
        for i, child in enumerate(node.functions):
            child_err = self.visit(child, context.define_context, i)
            util.update_errs(errors, child_err)
        return errors

    @when(BeginWithNode)
    def visit(self, node: BeginWithNode, context: ProgramContext, index: int = 0):
        errors = []
        num_err = self.visit(node.num, context.begin_context, index)
        util.update_errs(errors, num_err)
        for i, child in enumerate(node.step):
            child_err = self.visit(child, context.begin_context, i)
            util.update_errs(errors, child_err)
        return errors

    @when(FuncDeclarationNode)
    def visit(self, node: FuncDeclarationNode, context: DefineContext, index: int = 0):
        errors = []
        new_context = context.get_context(index)
        for i, child in enumerate(node.params):
            child_err = self.visit(child, new_context, i)
            util.update_errs(errors, child_err)
        for i, child in enumerate(node.body):
            child_err = self.visit(child, new_context, i)
            util.update_errs(errors, child_err)
        return errors if len(errors) else None

    @when(StepNode)
    def visit(self, node: StepNode, context: BeginContext, index: int = 0):
        errors = []
        new_context = context.get_context(index)
        for child in node.instructions:
            child_err = self.visit(child, new_context, index)
            util.update_errs(errors, child_err)
        return errors

    @when(VarDeclarationNode)
    def visit(self, node: VarDeclarationNode, context: OtherContext, index: int = 0):
        errors = []
        type_var, type_err = util.get_type(node.type)
        util.update_errs(errors, type_err)
        if context.is_var_defined(node.id):
            errors.append(f"variable {node.id} está ya definida")
        else:
            context.define_variable(node.id, type_var)
        expr_err = self.visit(node.expr, context, index)
        util.update_errs(errors, expr_err)
        return errors if len(errors) else None

    @when(ArrayDeclarationNode)
    def visit(self, node: ArrayDeclarationNode, context: OtherContext, index: int = 0):
        errors = []
        type_var, type_err = util.get_type(node.type)
        util.update_errs(errors, type_err)
        if context.is_var_defined(node.id):
            errors.append(f"variable {node.id} está ya definida")
        else:
            context.define_variable(node.id, Array(type_var))
        expr_err = self.visit(node.expr, context, index)
        util.update_errs(errors, expr_err)
        return errors if len(errors) else None

    @when(ParamNode)
    def visit(self, node: ParamNode, context: OtherContext, index: int = 0):
        type_var, errors = util.get_type(node.type)
        context.define_variable(node.idx, type_var)
        return errors

    @when(ParamArrayNode)
    def visit(self, node: ParamArrayNode, context: OtherContext, index: int = 0):
        type_var, errors = util.get_type(node.type)
        context.define_variable(node.idx, Array(type_var))
        return errors

    @when(GroupVarDeclarationNode)
    def visit(self, node: GroupVarDeclarationNode, context: OtherContext, index: int = 0):
        errors = []
        type_var, type_err = util.get_type(node.type)
        util.update_errs(errors, type_err)
        if context.is_var_defined(node.id):
            errors.append(f"{node.id} está ya definida")
        else:
            context.define_variable(node.id, type_var)
        collec_err = self.visit(node.collec, context, index)
        util.update_errs(errors, collec_err)

        init_err = self.visit(node.init, context, index)
        util.update_errs(errors, init_err)

        len_err = self.visit(node.len, context, index)
        util.update_errs(errors, len_err)
        return errors if len(errors) else None

    @when(LoopNode)
    def visit(self, node: LoopNode, context: OtherContext, index: int = 0):
        expr_err = self.visit(node.expr, context)
        errors = expr_err or []
        new_context = context.get_context(index)
        for i, child in enumerate(node.body):
            child_err = self.visit(child, new_context, i)
            util.update_errs(errors, child_err)
        return errors if len(errors) else None

    @when(ArrayNode)
    def visit(self, node: ArrayNode, context: OtherContext, index: int = 0):
        errors = []
        for child in node.elements:
            child_err = self.visit(child, context, index)
            util.update_errs(errors, child_err)
        return errors if len(errors) else None

    @when(IterNode)
    def visit(self, node: IterNode, context: OtherContext, index: int = 0):
        errors = []
        collec_err = self.visit(node.collec, context, index)
        util.update_errs(errors, collec_err)

        expr_err = self.visit(node.expr, context, index)
        util.update_errs(errors, expr_err)
        return errors if len(errors) else None

    @when(BorrowNode)
    def visit(self, node: BorrowNode, context: OtherContext, index: int = 0):
        errors = []
        from_collec_err = self.visit(node.from_collec, context, index)
        util.update_errs(errors, from_collec_err)

        to_collec_err = self.visit(node.to_collec, context, index)
        util.update_errs(errors, to_collec_err)

        init_err = self.visit(node.init, context, index)
        util.update_errs(errors, init_err)

        len_err = self.visit(node.len, context, index)
        util.update_errs(errors, len_err)
        return errors if len(errors) else None

    @when(ConditionNode)
    def visit(self, node: ConditionNode, context: OtherContext, index: int = 0):
        errors = []
        expr_err = self.visit(node.expr, context, index)
        util.update_errs(errors, expr_err)
        new_context = context.get_context(index)
        for i, child in enumerate(node.body):
            child_err = self.visit(child, new_context, i)
            util.update_errs(errors, child_err)
        return errors if len(errors) else None

    @when(AssignNode)
    def visit(self, node: AssignNode, context: OtherContext, index: int = 0):
        errors = []
        if not context.is_var_defined(node.id):
            errors.append(f"variable {node.lex} no esta definida")

        expr_err = self.visit(node.expr, context, index)
        util.update_errs(errors, expr_err)
        return errors

    @when(SetIndexNode)
    def visit(self, node: SetIndexNode, context: OtherContext, index: int = 0):
        errors = []
        if not context.is_var_defined(node.id):
            errors.append(f"variable {node.id} no esta definida")

        index_err = self.visit(node.index, context, index)
        util.update_errs(errors, index_err)

        expr_err = self.visit(node.expr, context, index)
        util.update_errs(errors, expr_err)
        return errors

    @when(ConstantNode)
    def visit(self, node: ConstantNode, context: OtherContext, index: int = 0):
        return None

    @when(VariableNode)
    def visit(self, node: VariableNode, context: OtherContext, index: int = 0):
        if not context.is_var_defined(node.lex):
            return [f"variable {node.lex} no esta definida"]
        return None

    @when(SpecialNode)
    def visit(self, node: SpecialNode, context: OtherContext, index: int = 0):
        return None

    @when(CallNode)
    def visit(self, node: CallNode, context: OtherContext, index: int = 0):
        errors = []
        if not context.is_func_defined(node.lex, len(node.args)):
            errors.append(
                f"funcion {node.lex} no esta definida con {len(node.args)} argumentos")
        for arg in node.args:
            arg_err = self.visit(arg, context, index)
            util.update_errs(errors, arg_err)
        return errors if len(errors) else None
    
    @when(DynamicCallNode)
    def visit(self, node: DynamicCallNode, context: OtherContext, index: int = 0):
        return None

    @when(BeginCallNode)
    def visit(self, node: BeginCallNode, context: StepContext, index: int = 0):
        errors = []
        if not context.is_func_defined(node.lex, len(node.args)):
            errors.append(
                f"funcion {node.lex} no esta definida con {len(node.args)} argumentos")
        arg = node.args[0]
        arg_err = self.visit(arg, context, index)
        util.update_errs(errors, arg_err)
        if not arg_err:
            members = arg.lex if type(arg) is ConstantNode else list(range(arg.left.lex, arg.right.lex + 1))
            context.define_members(members)
            if context.error_member:
                errors.append(f'integrantes del grupo invalidos')
        for arg in node.args[1:]:
            arg_err = self.visit(arg, context, index)
            util.update_errs(errors, arg_err)

        poss_err = self.visit(node.poss, context, index)
        util.update_errs(errors, poss_err)

        rot_err = self.visit(node.rot, context, index)
        util.update_errs(errors, rot_err)
        return errors if len(errors) else None

    @when(UnaryNode)
    def visit(self, node: UnaryNode, context: OtherContext, index: int = 0):
        return self.visit(node.expr, context, index)

    @when(BinaryNode)
    def visit(self, node: BinaryNode, context: OtherContext, index: int = 0):
        errors = []
        left_err = self.visit(node.left, context, index)
        util.update_errs(errors, left_err)

        right_err = self.visit(node.right, context, index)
        util.update_errs(errors, right_err)
        return errors if len(errors) else None

    @when(TernaryNode)
    def visit(self, node: TernaryNode, context: OtherContext, index: int = 0):
        errors = []
        left_err = self.visit(node.left, context, index)
        util.update_errs(errors, left_err)

        expr_err = self.visit(node.expr, context, index)
        util.update_errs(errors, expr_err)

        right_err = self.visit(node.right, context, index)
        util.update_errs(errors, right_err)
        return errors if len(errors) else None
