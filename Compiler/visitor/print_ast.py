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
        instructions = f'\n{str_tabs}'.join(
            self.visit(x, tabs + 1) for x in node.body)
        return f'def {node.id}({params}){{\n{str_tabs}{instructions}\n{str_close_tabs}}}'

    @when(StepNode)
    def visit(self, node: StepNode, tabs: int = 0):
        str_tabs = '\t' * tabs
        instructions = f'\n{str_tabs}'.join(self.visit(x) for x in node.instructions)
        return f'.step\n{str_tabs}{instructions}\n'

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
        str_while = '\t' * (tabs - 1)
        body = f'\n{str_tabs}'.join(self.visit(t, tabs + 1) for t in node.body)
        return f'while({self.visit(node.expr)}){"{"}\n{str_tabs + body}\n{str_while + "}"}'

    @when(ArrayNode)
    def visit(self, node: ArrayNode, tabs: int = 0):
        str_elements = ', '.join(self.visit(t) for t in node.elements)
        return f'[{str_elements}]'

    @when(IterNode)
    def visit(self, node: IterNode, tabs: int = 0):
        return f'all_of {self.visit(node.collec)} at {self.visit(node.expr)} of {node.dir}'

    @when(BorrowNode)
    def visit(self, node: BorrowNode, tabs: int = 0):
        return f'from {self.visit(node.from_collec)} borrow {self.visit(node.len)} starting_at {self.visit(node.init)} to {self.visit(node.to_collec)}'

    @when(ConditionNode)
    def visit(self, node: ConditionNode, tabs: int = 0):
        str_tabs = '\t' * tabs
        str_if = '\t' * (tabs - 1)
        body = f'\n{str_tabs}'.join(self.visit(t, tabs + 1) for t in node.body)
        return f'if({self.visit(node.expr)}){"{"}\n{str_tabs + body}\n{str_if + "}"}'

    @when(AssignNode)
    def visit(self, node: AssignNode, tabs: int = 0):
        return f'{node.id} = {self.visit(node.expr)}'

    @when(SetIndexNode)
    def visit(self, node: SetIndexNode, tabs: int = 0):
        return f'{node.id}[{self.visit(node.index)}] = {self.visit(node.expr)}'

    @when(ConstantNode)
    def visit(self, node: ConstantNode, tabs: int = 0):
        return f'{node.lex}'

    @when(VariableNode)
    def visit(self, node: VariableNode, tabs: int = 0):
        return f'{node.lex}'

    @when(SpecialNode)
    def visit(self, node: SpecialNode, tabs: int = 0):
        return f'{node.lex}'

    @when(DynamicCallNode)
    def visit(self, node: DynamicCallNode, tabs: int = 0):
        args = ', '.join(self.visit(x) for x in node.args)
        return f'{self.visit(node.head)}.{node.lex}({args})'

    @when(CallNode)
    def visit(self, node: CallNode, tabs: int = 0):
        args = ', '.join(self.visit(x) for x in node.args)
        return f'{node.lex}({args})'

    @when(BeginCallNode)
    def visit(self, node: BeginCallNode, tabs: int = 0):
        args = ', '.join(self.visit(x) for x in node.args)
        return f'line_up {node.lex} with {self.visit(node.args[0])} in {self.visit(node.poss)} heading {self.visit(node.rot)} args({args})'

    @when(NotNode)
    def visit(self, node: NotNode, tabs: int = 0):
        return f'!{self.visit(node.expr)}'

    @when(PlusNode)
    def visit(self, node: PlusNode, tabs: int = 0):
        return f'{self.visit(node.left)} + {self.visit(node.right)}'

    @when(MinusNode)
    def visit(self, node: MinusNode, tabs: int = 0):
        return f'{self.visit(node.left)} - {self.visit(node.right)}'

    @when(StarNode)
    def visit(self, node: StarNode, tabs: int = 0):
        return f'{self.visit(node.left)} * {self.visit(node.right)}'

    @when(DivNode)
    def visit(self, node: DivNode, tabs: int = 0):
        return f'{self.visit(node.left)} / {self.visit(node.right)}'

    @when(ModNode)
    def visit(self, node: ModNode, tabs: int = 0):
        return f'{self.visit(node.left)} % {self.visit(node.right)}'

    @when(VectNode)
    def visit(self, node: VectNode, tabs: int = 0):
        return f'({self.visit(node.left)}, {self.visit(node.right)})'

    @when(AndNode)
    def visit(self, node: AndNode, tabs: int = 0):
        return f'{self.visit(node.left)} & {self.visit(node.right)}'

    @when(OrNode)
    def visit(self, node: OrNode, tabs: int = 0):
        return f'{self.visit(node.left)} | {self.visit(node.right)}'

    @when(EqNode)
    def visit(self, node: EqNode, tabs: int = 0):
        return f'{self.visit(node.left)} == {self.visit(node.right)}'

    @when(EqlNode)
    def visit(self, node: EqlNode, tabs: int = 0):
        return f'{self.visit(node.left)} <= {self.visit(node.right)}'

    @when(EqgNode)
    def visit(self, node: EqgNode, tabs: int = 0):
        return f'{self.visit(node.left)} >= {self.visit(node.right)}'

    @when(GtNode)
    def visit(self, node: GtNode, tabs: int = 0):
        return f'{self.visit(node.left)} > {self.visit(node.right)}'

    @when(LtNode)
    def visit(self, node: LtNode, tabs: int = 0):
        return f'{self.visit(node.left)} < {self.visit(node.right)}'

    @when(GetIndexNode)
    def visit(self, node: GetIndexNode, tabs: int = 0):
        return f'{self.visit(node.left)}[{self.visit(node.right)}]'

    @when(SliceNode)
    def visit(self, node: SliceNode, tabs: int = 0):
        return f'[{self.visit(node.left)}:{self.visit(node.right)}]'

    @when(LinkNode)
    def visit(self, node: LinkNode, tabs: int = 0):
        return f'{self.visit(node.left)} {self.visit(node.expr)} of {self.visit(node.right)}'
