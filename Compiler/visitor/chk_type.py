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

    @when(StepNode)
    def visit(self, node: StepNode, context: BeginContext, index: int = 0):
        errors = []
        new_context = context.get_context(index)
        for child in node.instructions:
            _, child_err = self.visit(child, new_context, index)
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
        util.update_err_type(errors, "int", init_type)
        util.update_errs(errors, init_err)

        len_type, len_err = self.visit(node.len, context, index)
        util.update_err_type(errors, "int", len_type)
        util.update_errs(errors, len_err)
        return None, errors if len(errors) else None

    @when(LoopNode)
    def visit(self, node: LoopNode, context: OtherContext, index: int = 0):
        errors = []
        expr_type, expr_err = self.visit(node.expr, context, index)
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
        util.update_err_type(errors, "int", init_type)
        util.update_errs(errors, init_err)

        len_type, len_err = self.visit(node.len, context, index)
        util.update_err_type(errors, "int", len_type)
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
        return None, errors if len(errors) else None

    @when(ConstantNode)
    def visit(self, node: ConstantNode, context: OtherContext, index: int = 0):
        return node.type, None

    @when(VariableNode)
    def visit(self, node: VariableNode, context: OtherContext, index: int = 0):
        type_var = context.get_variable_info(node.lex).type
        return type_var, None

    @when(AssignNode)
    def visit(self, node: AssignNode, context: OtherContext, index: int = 0):
        errors = []
        type_var = context.get_variable_info(node.id).type
        expr_type, expr_err = self.visit(node.expr, context, index)
        util.update_err_type(errors, type_var, expr_type)
        util.update_errs(errors, expr_err)
        return None, errors if len(errors) else None

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
        return None, errors if len(errors) else None

    @when(CallNode)
    def visit(self, node: CallNode, context: OtherContext, index: int = 0):
        args = []
        for get_arg in node.args:
            get_type, _ = self.visit(get_arg, context, index)
            args.append(get_type)

        errors = []
        return_type = "error"
        funcs_info = context.get_all_func_info(node.lex, len(args))
        if not util.exist_func(args, funcs_info):
            err_args = "".join([f"{arg}, " for arg in args[:-1]] + [args[-1]])
            errors.append(f"el método {node.lex}({err_args}) no existe")
        else:
            return_type = funcs_info.return_type
        return return_type, errors if len(errors) else None

    @when(BeginCallNode)
    def visit(self, node: BeginCallNode, context: OtherContext, index: int = 0):
        args = []
        for get_arg in node.args:
            get_type, _ = self.visit(get_arg, context, index)
            args.append(get_type)

        errors = []
        funcs_info = context.get_all_func_info(node.lex, len(args))
        if not util.exist_func(args, funcs_info):
            err_args = "".join([f"{arg}, " for arg in args[:-1]] + [args[-1]])
            errors.append(f"el método {node.lex}({err_args}) no existe")

        poss_type, poss_err = self.visit(node.poss, context, index)
        util.update_err_type(errors, "vector", poss_type)
        util.update_errs(errors, poss_err)

        rot_type, rot_err = self.visit(node.rot, context, index)
        util.update_err_type(errors, "vector", rot_type)
        util.update_errs(errors, rot_err)
        return None, errors if len(errors) else None

    # @when(ArrayNode)
    # def visit(self, node: ArrayNode, context: OtherContext, index: int):
    #     pass

    @when(NotNode)
    def visit(self, node: NotNode, context: OtherContext, index: int):
        expr_type, errors = self.visit(node.expr, context, index)
        util.update_err_type(errors, "boolean", expr_type)
        if expr_type != "boolean":
            expr_type = "error"
        return expr_type, errors if len(errors) else None

    @when(PlusNode)
    def visit(self, node: PlusNode, context: OtherContext, index: int):
        errors = []
        left_type, left_err = self.visit(node.left, context, index)
        right_type, right_err = self.visit(node.right, context, index)
        util.update_errs(errors, left_err)

        if left_type == "error" or right_type == "error":
            return_type = "error"
        elif left_type != right_type:
            return_type = "vector"
        else:
            return_type = "int"

        if return_type != "error" and ((
                left_type != "vector" and left_type != "int") or (
                right_type != "vector" and right_type != "int")):
            return_type = "error"
            errors.append(
                f"operación inválida, esta tratando de sumar un {left_type} por {right_type}")
        util.update_errs(errors, right_err)
        return return_type, errors if len(errors) else None

    @when(MinusNode)
    def visit(self, node: MinusNode, context: OtherContext, index: int):
        errors = []
        left_type, left_err = self.visit(node.left, context, index)
        right_type, right_err = self.visit(node.right, context, index)
        util.update_errs(errors, left_err)

        if left_type == "error" or right_type == "error":
            return_type = "error"
        elif left_type != right_type:
            return_type = "vector"
        else:
            return_type = "int"

        if return_type != "error" and ((
                left_type != "vector" and left_type != "int") or (
                right_type != "vector" and right_type != "int")):
            return_type = "error"
            errors.append(
                f"operación inválida, esta tratando de restar un {left_type} por {right_type}")
        util.update_errs(errors, right_err)
        return return_type, errors if len(errors) else None

    @when(StarNode)
    def visit(self, node: StarNode, context: OtherContext, index: int):
        errors = []
        left_type, left_err = self.visit(node.left, context, index)
        right_type, right_err = self.visit(node.right, context, index)
        util.update_errs(errors, left_err)

        return_type = "int" if left_type != "error" and right_type != "error" else "error"
        if return_type != "error" and ((
                left_type != "vector" and left_type != "int") or (
                right_type != "vector" and right_type != "int") or (
                left_type == right_type and left_type == "vector")):
            return_type = "error"
            errors.append(
                f"operación inválida, esta tratando de multiplicar un {left_type} por {right_type}")
        util.update_errs(errors, right_err)
        return return_type, errors if len(errors) else None

    @when(DivNode)
    def visit(self, node: DivNode, context: OtherContext, index: int):
        errors = []
        left_type, left_err = self.visit(node.left, context, index)
        right_type, right_err = self.visit(node.right, context, index)
        util.update_errs(errors, left_err)

        return_type = "int" if left_type != "error" and right_type != "error" else "error"
        if return_type != "error" and ((
                left_type != "vector" and left_type != "int") or (
                right_type != "vector" and right_type != "int") or (
                left_type == right_type and left_type == "vector")):
            return_type = "error"
            errors.append(
                f"operación inválida, esta tratando de dividir un {left_type} por {right_type}")
        util.update_errs(errors, right_err)
        return return_type, errors if len(errors) else None

    @when(ModNode)
    def visit(self, node: ModNode, context: OtherContext, index: int):
        errors = []
        left_type, left_err = self.visit(node.left, context, index)
        right_type, right_err = self.visit(node.right, context, index)
        util.update_errs(errors, left_err)

        return_type = "int" if left_type != "error" and right_type != "error" else "error"
        if return_type != "error" and ((
                left_type != "vector" and left_type != "int") or (
                right_type != "vector" and right_type != "int") or (
                left_type == right_type and left_type == "vector")):
            return_type = "error"
            errors.append(
                f"operación inválida, esta tratando de hayar el resto de un {left_type} por {right_type}")
        util.update_errs(errors, right_err)
        return return_type, errors if len(errors) else None

    @when(VectNode)
    def visit(self, node: VectNode, context: OtherContext, index: int):
        errors = []
        left_type, left_err = self.visit(node.left, context, index)
        right_type, right_err = self.visit(node.right, context, index)

        left_type = util.update_err_type(errors, "int", left_type)
        util.update_errs(errors, left_err)
        right_type = util.update_err_type(errors, "int", right_type)
        util.update_errs(errors, right_err)

        return_type = "vector" if left_type != "error" and right_type != "error" else "error"
        return return_type, errors if len(errors) else None

    @when(BinaryLogicNode)
    def visit(self, node: BinaryLogicNode, context: OtherContext, index: int):
        errors = []
        left_type, left_err = self.visit(node.left, context, index)
        right_type, right_err = self.visit(node.right, context, index)
        util.update_errs(errors, left_err)

        return_type = "boolean" if left_type != "error" and right_type != "error" else "error"
        if return_type != "error" and (left_type != "boolean" or right_type != "boolean"):
            return_type = "error"
            errors.append(
                f"operación inválida, se esperaban ambos bool pero dieron {left_type} y {right_type}")
        util.update_errs(errors, right_err)
        return return_type, errors if len(errors) else None

    @when(EqNode)
    def visit(self, node: EqNode, context: OtherContext, index: int):
        errors = []
        left_type, left_err = self.visit(node.left, context, index)
        right_type, right_err = self.visit(node.right, context, index)
        util.update_errs(errors, left_err)

        return_type = "boolean" if left_type != "error" and right_type != "error" else "error"
        if return_type != "error" and (left_type != right_type):
            return_type = "error"
            errors.append(
                f"operación inválida, se esperaba una comparación con elementos del mismo tipo")
        util.update_errs(errors, right_err)
        return return_type, errors if len(errors) else None

    @when(NonEqNode)
    def visit(self, node: NonEqNode, context: OtherContext, index: int):
        errors = []
        left_type, left_err = self.visit(node.left, context, index)
        right_type, right_err = self.visit(node.right, context, index)
        util.update_errs(errors, left_err)

        return_type = "boolean" if left_type != "error" and right_type != "error" else "error"
        if return_type != "error" and (left_type != "int" or right_type != "int"):
            return_type = "error"
            errors.append(
                f"operación inválida, solo se puede comparar entre numeros, excepto en el equals")
        util.update_errs(errors, right_err)
        return return_type, errors if len(errors) else None

    @when(GetIndexNode)
    def visit(self, node: GetIndexNode, context: OtherContext, index: int):
        errors = []
        left_type, left_err = self.visit(node.left, context, index)
        right_type, right_err = self.visit(node.right, context, index)

        return_type = "error"
        if left_type == "group":
            return_type = "node"
        elif left_type == "array":
            return_type == "int"
        elif left_type != "error":
            errors.append(f"no se puede indexar en este tipo")
        util.update_errs(errors, left_err)
        right_type = util.update_err_type(errors, "int", right_type)
        util.update_errs(errors, right_err)

        return_type = return_type if right_type != "error" else "error"
        return return_type, errors if len(errors) else None

    @when(SliceNode)
    def visit(self, node: SliceNode, context: OtherContext, index: int):
        pass

    @when(LinkNode)
    def visit(self, node: LinkNode, context: OtherContext, index: int = 0):
        errors = []
        left_type, left_err = self.visit(node.left, context, index)
        util.update_err_type(errors, "node", left_type)
        util.update_errs(errors, left_err)

        expr_type, expr_err = self.visit(node.expr, context, index)
        util.update_err_type(errors, "vector", expr_type)
        util.update_errs(errors, expr_err)

        right_type, right_err = self.visit(node.right, context, index)
        util.update_err_type(errors, "node", right_type)
        util.update_errs(errors, right_err)
        return None, errors if len(errors) else None
