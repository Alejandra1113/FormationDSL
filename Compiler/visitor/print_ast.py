from Compiler.semantic.language import *
from .visitor import *
from ._def import *

__all__ = ['PrintVisitor']


class PrintVisitor(object):
    @on('node')
    def visit(self, node):
        pass

    @when(ProgramNode)
    def visit(self, node: ProgramNode, tabs: int = 0):
        str_def = ''.join(self.visit(node.definitions, 1))
        str_begin = ''.join(self.visit(node.begin_with, 1))
        return f'.Definitions\n\t{str_def}\n\n.Begin\n\t{str_begin}'

    @when(DefinitionsNode)
    def visit(self, node: DefinitionsNode, tabs: int = 0):
        str_tabs = '\t' * tabs
        return f'\n{str_tabs}'.join(self.visit(t, tabs + 1) for t in node.functions)

    @when(BeginWithNode)
    def visit(self, node: BeginWithNode, tabs: int = 0):
        str_tabs = '\t' * tabs
        return f'\n{str_tabs}'.join(self.visit(t, tabs + 1) for t in node.step)

    @when(FuncDeclarationNode)
    def visit(self, node: FuncDeclarationNode, tabs: int = 0):
        str_tabs = '\t' * tabs
        str_close_tabs = '\t' * (tabs - 1)
        params = ', '.join(self.visit(x) for x in node.params)
        instructions = f'\n{str_tabs}'.join(self.visit(x, tabs + 1) for x in node.body)
        return f'def {node.id}({params}){{\n{str_tabs}{instructions}\n{str_close_tabs}}}'

    @when(StepNode)
    def visit(self, node: StepNode, tabs: int = 0):
        str_tabs = '\t' * tabs
        return f'\n{str_tabs}'.join(self.visit(x) for x in node.instructions)

    @when(VarDeclarationNode)
    def visit(self, node: VarDeclarationNode, tabs: int = 0):
        return f'{node.type} {node.id} = {self.visit(node.expr)}'

    @when(ArrayDeclarationNode)
    def visit(self, node: ArrayDeclarationNode, tabs: int = 0):
        return f'{node.type}[] {node.id} = {self.visit(node.expr)}'

    @when(ParamNode)
    def visit(self, node: ParamNode, tabs: int = 0):
        return f'{node.type} {node.idx}'

    @when(ParamArrayNode)
    def visit(self, node: ParamArrayNode, tabs: int = 0):
        return f'{node.type}[] {node.idx}'

    @when(GroupVarDeclarationNode)
    def visit(self, node: GroupVarDeclarationNode, tabs: int = 0):
        return f'{node.type} {node.id} = from {self.visit(node.collec)} take {self.visit(node.len)} starting_at {self.visit(node.init)}'

    @when(LoopNode)
    def visit(self, node: LoopNode, tabs: int = 0):
        str_tabs = '\t' * tabs
        str_while =  '\t' * (tabs - 1)
        body = f'\n{str_tabs}'.join(self.visit(t) for t in node.body)
        return f'while({self.visit(node.expr)}){"{" + body}\n{str_while + "}"}'

    @when(ArrayNode)
    def visit(self, node: ArrayNode, tabs: int = 0):
        return ''

    @when(IterNode)
    def visit(self, node: IterNode, tabs: int = 0):
        return ''

    @when(BorrowNode)
    def visit(self, node: BorrowNode, tabs: int = 0):
        return ''

    @when(ConditionNode)
    def visit(self, node: ConditionNode, tabs: int = 0):
        return ''

    @when(ExpressionNode)
    def visit(self, node: ExpressionNode, tabs: int = 0):
        return ''
