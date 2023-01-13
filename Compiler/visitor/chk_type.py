from Compiler.semantic.types import Bool, Group, Int, NodeType, Array, Vector
from Compiler.semantic.language import *
import Compiler.utils as util
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
        for i, child in enumerate(node.functions):
            _, child_err = self.visit(child, context.define_context, i)
            util.update_errs(errors, child_err)
        return None, errors

    @when(BeginWithNode)
    def visit(self, node: BeginWithNode, context: ProgramContext, index: int = 0):
        errors = []
        for i, child in enumerate(node.step):
            _, child_err = self.visit(child, context.begin_context, i)
            util.update_errs(errors, child_err)
        return None, errors

    @when(FuncDeclarationNode)
    def visit(self, node: FuncDeclarationNode, context: DefineContext, index: int = 0):
        errors = []
        new_context = context.get_context(index)
        for i, child in enumerate(node.body):
            _, child_err = self.visit(child, new_context, i)
            util.update_errs(errors, child_err)
        return None, errors if len(errors) else None

    @when(StepNode)
    def visit(self, node: StepNode, context: BeginContext, index: int = 0):
        errors = []
        new_context = context.get_context(index)
        for child in node.instructions:
            _, child_err = self.visit(child, new_context, index)
            util.update_errs(errors, child_err)
        return None, errors

    @when(VarDeclarationNode)
    def visit(self, node: VarDeclarationNode, context: OtherContext, index: int = 0):
        errors = []
        expr_type, expr_err = self.visit(node.expr, context, index)
        var_type = context.get_variable_info(node.id).type
        util.update_err_type(errors, var_type, expr_type)
        util.update_errs(errors, expr_err)
        return None, errors if len(errors) else None

    @when(ArrayDeclarationNode)
    def visit(self, node: ArrayDeclarationNode, context: OtherContext, index: int = 0):
        errors = []
        expr_type, expr_err = self.visit(node.expr, context, index)
        var_type = context.get_variable_info(node.id).type
        util.update_err_type(errors, var_type, expr_type)
        util.update_errs(errors, expr_err)
        return None, errors if len(errors) else None

    @when(GroupVarDeclarationNode)
    def visit(self, node: GroupVarDeclarationNode, context: OtherContext, index: int = 0):
        errors = []
        var_type = context.get_variable_info(node.id).type
        collec_type, collec_err = self.visit(node.collec, context, index)
        util.update_err_type(errors, var_type, collec_type)
        util.update_errs(errors, collec_err)

        init_type, init_err = self.visit(node.init, context, index)
        util.update_err_type(errors, Int(), init_type)
        util.update_errs(errors, init_err)

        len_type, len_err = self.visit(node.len, context, index)
        util.update_err_type(errors, Int(), len_type)
        util.update_errs(errors, len_err)
        return None, errors if len(errors) else None

    @when(LoopNode)
    def visit(self, node: LoopNode, context: OtherContext, index: int = 0):
        errors = []
        expr_type, expr_err = self.visit(node.expr, context, index)
        util.update_err_type(errors, Bool(), expr_type)
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
        util.update_err_type(errors, Vector(), expr_type)
        util.update_errs(errors, expr_err)
        return None, errors if len(errors) else None

    @when(BorrowNode)
    def visit(self, node: BorrowNode, context: OtherContext, index: int = 0):
        errors = []
        init_type, init_err = self.visit(node.init, context, index)
        util.update_err_type(errors, Int(), init_type)
        util.update_errs(errors, init_err)

        len_type, len_err = self.visit(node.len, context, index)
        util.update_err_type(errors, Int(), len_type)
        util.update_errs(errors, len_err)
        return None, errors if len(errors) else None

    @when(ConditionNode)
    def visit(self, node: ConditionNode, context: OtherContext, index: int = 0):
        errors = []
        expr_type, expr_err = self.visit(
            node.expr, context, index) if node.expr else (Bool(), None)
        util.update_err_type(errors, Bool(), expr_type)
        util.update_errs(errors, expr_err)

        new_context = context.get_context(index)
        for i, child in enumerate(node.body):
            _, child_err = self.visit(child, new_context, i)
            util.update_errs(errors, child_err)
        return None, errors if len(errors) else None

    @when(ConstantNode)
    def visit(self, node: ConstantNode, context: OtherContext, index: int = 0):
        return node.type, None

    @when(SpecialNode)
    def visit(self, node: SpecialNode, context: OtherContext, index: int = 0):
        return None, None

    @when(VariableNode)
    def visit(self, node: VariableNode, context: OtherContext, index: int = 0):
        var_type = context.get_variable_info(node.lex).type
        return var_type, None

    @when(AssignNode)
    def visit(self, node: AssignNode, context: OtherContext, index: int = 0):
        errors = []
        expr_type, expr_err = self.visit(node.expr, context, index)
        var_type = context.get_variable_info(node.id).type
        util.update_err_type(errors, var_type, expr_type)
        util.update_errs(errors, expr_err)
        return None, errors if len(errors) else None

    @when(SetIndexNode)
    def visit(self, node: SetIndexNode, context: OtherContext, index: int = 0):
        errors = []
        var_type = context.get_variable_info(node.id).type
        expr_type, expr_err = self.visit(node.expr, context, index)
        if type(var_type) == Array:
            util.update_err_type(errors, var_type.sub_type, expr_type)
        else:
            err = TypeError(
                f"error de tipo, no se puede indexar en un {var_type}")
            errors.append(err)
        util.update_errs(errors, expr_err)
        return None, errors if len(errors) else None

    @when(CallNode)
    def visit(self, node: CallNode, context: OtherContext, index: int = 0):
        args = []
        for get_arg in node.args:
            get_type, _ = self.visit(get_arg, context, index)
            args.append(get_type)

        errors = []
        err_args = "".join([f"{arg}, " for arg in args[:-1]] + [str(args[-1])]) if len(args) else ""
        return_type = TypeError(f"el método {node.lex}({err_args}) no existe")

        info = context.get_function_info(node.lex, args)
        if not info:
            errors.append(return_type)
        else:
            return_type = info.return_type
        return return_type, errors if len(errors) else None

    @when(DynamicCallNode)
    def visit(self, node: DynamicCallNode, context: OtherContext, index: int = 0):
        args = []
        for get_arg in node.args:
            get_type, _ = self.visit(get_arg, context, index)
            args.append(get_type)

        errors = []
        err_args = "".join([f"{arg}, " for arg in args[:-1]] + [str(args[-1])]) if len(args) else ""
        return_type = TypeError(f"el método {node.lex}({err_args}) no existe")

        var_type, var_err = self.visit(node.head, context, index)
        util.update_errs(errors, var_err)
        info = var_type.get_function_info(node.lex, node.args)
        if not info:
            errors.append(return_type)
        else:
            return_type = info.return_type
        return return_type, errors if len(errors) else None

    @when(BeginCallNode)
    def visit(self, node: BeginCallNode, context: OtherContext, index: int = 0):
        args = []
        for get_arg in node.args:
            get_type, _ = self.visit(get_arg, context, index)
            args.append(get_type)

        errors = []
        err_args = "".join([f"{arg}, " for arg in args[:-1]] + [str(args[-1])]) if len(args) else ""
        return_type = TypeError(f"el método {node.lex}({err_args}) no existe")

        info = context.get_function_info(node.lex, args)
        if not info:
            errors.append(return_type)

        poss_type, poss_err = self.visit(node.poss, context, index)
        util.update_err_type(errors, Vector(), poss_type)
        util.update_errs(errors, poss_err)

        rot_type, rot_err = self.visit(node.rot, context, index)
        util.update_err_type(errors, Vector(), rot_type)
        util.update_errs(errors, rot_err)
        return None, errors if len(errors) else None

    @when(ArrayNode)
    def visit(self, node: ArrayNode, context: OtherContext, index: int):
        errors = []
        expr_type, expr_err = self.visit(node.elements[0], context, index)
        util.update_errs(errors, expr_err)
        for child in node.elements[1:]:
            child_type, child_err = self.visit(child, context, index)
            expr_type = util.update_err_type(errors, expr_type, child_type)
            util.update_errs(errors, child_err)

        return_type = expr_type if type(
            expr_type) == TypeError else Array(expr_type)
        return return_type, errors if len(errors) else None

    @when(NotNode)
    def visit(self, node: NotNode, context: OtherContext, index: int):
        expr_type, errors = self.visit(node.expr, context, index)
        expr_type = util.update_err_type(errors, Bool(), expr_type)
        return expr_type, errors if len(errors) else None

    @when(PlusNode)
    def visit(self, node: PlusNode, context: OtherContext, index: int):
        errors = []
        left_type, left_err = self.visit(node.left, context, index)
        right_type, right_err = self.visit(node.right, context, index)
        util.update_errs(errors, left_err)

        if type(left_type) == TypeError or type(right_type) == TypeError:
            return_type = TypeError()
        elif left_type != right_type:
            return_type = Vector()
        else:
            return_type = Int()

        if type(return_type) != TypeError and ((
                type(left_type) != Vector and type(left_type) != Int) or (
                type(right_type) != Vector and type(right_type) != Int)):
            return_type = TypeError(
                f"operación inválida, esta tratando de sumar un {left_type} por {right_type}")
            errors.append(return_type)
        util.update_errs(errors, right_err)
        return return_type, errors if len(errors) else None

    @when(MinusNode)
    def visit(self, node: MinusNode, context: OtherContext, index: int):
        errors = []
        left_type, left_err = self.visit(node.left, context, index)
        right_type, right_err = self.visit(node.right, context, index)
        util.update_errs(errors, left_err)

        if type(left_type) == TypeError or type(right_type) == TypeError:
            return_type = TypeError()
        elif left_type != right_type:
            return_type = Vector()
        else:
            return_type = Int()

        if type(return_type) != TypeError and ((
                type(left_type) != Vector and type(left_type) != Int) or (
                type(right_type) != Vector and type(right_type) != Int)):
            return_type = TypeError(
                f"operación inválida, esta tratando de restar un {left_type} por {right_type}")
            errors.append(return_type)
        util.update_errs(errors, right_err)
        return return_type, errors if len(errors) else None

    @ when(StarNode)
    def visit(self, node: StarNode, context: OtherContext, index: int):
        errors = []
        left_type, left_err = self.visit(node.left, context, index)
        right_type, right_err = self.visit(node.right, context, index)
        util.update_errs(errors, left_err)

        return_type = Int() if type(left_type) != TypeError and type(
            right_type) != TypeError else TypeError()
        if type(return_type) != TypeError and ((
                type(left_type) != Vector and type(left_type) != Int) or (
                type(right_type) != Vector and type(right_type) != Int) or (
                type(left_type) == type(right_type) and type(left_type) == Vector)):
            return_type = TypeError(
                f"operación inválida, esta tratando de multiplicar un {left_type} por {right_type}")
            errors.append(return_type)
        util.update_errs(errors, right_err)
        return return_type, errors if len(errors) else None

    @ when(DivNode)
    def visit(self, node: DivNode, context: OtherContext, index: int):
        errors = []
        left_type, left_err = self.visit(node.left, context, index)
        right_type, right_err = self.visit(node.right, context, index)
        util.update_errs(errors, left_err)

        return_type = Int() if type(left_type) != TypeError and type(
            right_type) != TypeError else TypeError()
        if type(return_type) != TypeError and ((
                type(left_type) != Vector and type(left_type) != Int) or (
                type(right_type) != Vector and type(right_type) != Int) or (
                type(left_type) == type(right_type) and type(left_type) == Vector)):
            return_type = TypeError(
                f"operación inválida, esta tratando de dividir un {left_type} por {right_type}")
            errors.append(return_type)
        util.update_errs(errors, right_err)
        return return_type, errors if len(errors) else None

    @ when(ModNode)
    def visit(self, node: ModNode, context: OtherContext, index: int):
        errors = []
        left_type, left_err = self.visit(node.left, context, index)
        right_type, right_err = self.visit(node.right, context, index)
        util.update_errs(errors, left_err)

        return_type = Int() if type(left_type) != TypeError and type(
            right_type) != TypeError else TypeError()
        if type(return_type) != TypeError and ((
                type(left_type) != Vector and type(left_type) != Int) or (
                type(right_type) != Vector and type(right_type) != Int) or (
                type(left_type) == type(right_type) and type(left_type) == Vector)):
            return_type = TypeError(
                f"operación inválida, esta tratando de hayar el resto de un {left_type} por {right_type}")
            errors.append(return_type)
        util.update_errs(errors, right_err)
        return return_type, errors if len(errors) else None

    @ when(VectNode)
    def visit(self, node: VectNode, context: OtherContext, index: int):
        errors = []
        left_type, left_err = self.visit(node.left, context, index)
        right_type, right_err = self.visit(node.right, context, index)

        left_type = util.update_err_type(errors, Int(), left_type)
        util.update_errs(errors, left_err)
        right_type = util.update_err_type(errors, Int(), right_type)
        util.update_errs(errors, right_err)

        return_type = Vector() if type(left_type) != TypeError and type(
            right_type) != TypeError else TypeError()
        return return_type, errors if len(errors) else None

    @ when(BinaryLogicNode)
    def visit(self, node: BinaryLogicNode, context: OtherContext, index: int):
        errors = []
        left_type, left_err = self.visit(node.left, context, index)
        right_type, right_err = self.visit(node.right, context, index)
        util.update_errs(errors, left_err)

        return_type = Bool() if type(left_type) != TypeError and type(
            right_type) != TypeError else TypeError()
        if type(return_type) != TypeError and (type(left_type) != Bool or type(right_type) != Bool):
            return_type = TypeError(
                f"operación inválida, se esperaban ambos bool pero dieron {left_type} y {right_type}")
            errors.append(return_type)
        util.update_errs(errors, right_err)
        return return_type, errors if len(errors) else None

    @ when(EqNode)
    def visit(self, node: EqNode, context: OtherContext, index: int):
        errors = []
        left_type, left_err = self.visit(node.left, context, index)
        right_type, right_err = self.visit(node.right, context, index)
        util.update_errs(errors, left_err)

        return_type = Bool() if type(left_type) != TypeError and type(
            right_type) != TypeError else TypeError()
        if type(return_type) != TypeError and (type(left_type) != type(right_type)):
            return_type = TypeError(
                f"operación inválida, se esperaba una comparación con elementos del mismo tipo")
            errors.append(return_type)
        util.update_errs(errors, right_err)
        return return_type, errors if len(errors) else None

    @ when(NonEqNode)
    def visit(self, node: NonEqNode, context: OtherContext, index: int):
        errors = []
        left_type, left_err = self.visit(node.left, context, index)
        right_type, right_err = self.visit(node.right, context, index)
        util.update_errs(errors, left_err)

        return_type = Bool() if type(left_type) != TypeError and type(
            right_type) != TypeError else TypeError()
        if type(return_type) != TypeError and (type(left_type) != Int or type(right_type) != Int):
            return_type = TypeError(
                f"operación inválida, solo se puede comparar entre numeros, excepto en el equals")
            errors.append(return_type)
        util.update_errs(errors, right_err)
        return return_type, errors if len(errors) else None

    @ when(GetIndexNode)
    def visit(self, node: GetIndexNode, context: OtherContext, index: int):
        errors = []
        left_type, left_err = self.visit(node.left, context, index)
        right_type, right_err = self.visit(node.right, context, index)

        return_type = TypeError(f"no se puede indexar en este tipo")
        if type(left_type) == Group:
            return_type = NodeType()
        elif type(left_type) == Array:
            return_type == Int
        elif type(left_type) != TypeError:
            errors.append(return_type)
        util.update_errs(errors, left_err)
        right_type = util.update_err_type(errors, Int(), right_type)
        util.update_errs(errors, right_err)

        return_type = return_type if type(right_type) != TypeError else TypeError()
        return return_type, errors if len(errors) else None

    @ when(SliceNode)
    def visit(self, node: SliceNode, context: OtherContext, index: int):
        pass

    @ when(LinkNode)
    def visit(self, node: LinkNode, context: OtherContext, index: int = 0):
        errors = []
        left_type, left_err = self.visit(node.left, context, index)
        util.update_err_type(errors, NodeType(), left_type)
        util.update_errs(errors, left_err)

        expr_type, expr_err = self.visit(node.expr, context, index)
        util.update_err_type(errors, Vector(), expr_type)
        util.update_errs(errors, expr_err)

        right_type, right_err = self.visit(node.right, context, index)
        util.update_err_type(errors, NodeType(), right_type)
        util.update_errs(errors, right_err)
        return None, errors if len(errors) else None
