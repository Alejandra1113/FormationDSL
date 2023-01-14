from Compiler.semantic.types import *
import Compiler.utils as util
from Compiler.semantic.language import *
from .visitor import *
from ._def import *

__all__ = ['CilVisitor']


class CilVisitor(object):
    def __init__(self):
        self.var_names = {}
        self.temp_names = []
        self.fun_names = {}

    def set_name(self, id):
        name = self.var_names.get(id)
        if not name:
            name = f"var_{len(self.var_names)}"
            self.var_names[id] = name
        return name
    
    def set_function(self, id):
        name = self.fun_names.get(id)
        if not name:
            name = f"fun_{len(self.fun_names)}"
            self.fun_names[id] = name
        return name

    @on('node')
    def visit(self, node):
        pass

    @when(ProgramNode)
    def visit(self, node):

        ######################################################
        # node.declarations -> DefinitionsNode
        # node.beginWith -> beginWithNode
        ######################################################

        definitions = self.visit(node.definitions)
        return ProgramNode(definitions, node.begin_with)

    @when(DefinitionsNode)
    def visit(self, node):
        ###############################
        # node.functions -> [ FuncDeclarationNode ... ]
        ###############################

        functions = []
        for definition in node.functions:
            inst = self.visit(definition)
            functions += inst if type(inst) is list else [inst]

        return DefinitionsNode(functions)

    @when(FuncDeclarationNode)
    def visit(self, node):
        ###############################
        # node.id -> str
        # node.params -> [ PramNode ... ]
        # node.body -> [ ExpressionNode ... ]
        ###############################

        params = []
        for param in node.params:
            p = self.visit(param)
            params += p if type(p) is list else [p]

        body = []
        for instruction in node.body:
            inst = self.visit(instruction)
            body += inst if type(inst) is list else [inst]

        return FuncDeclarationNode(self.set_function(node.id), params, body)

    @when(ParamArrayNode)
    def visit(self, node):
        ###############################
        # node.id -> str
        # node.type -> type
        ###############################

        return ParamArrayNode(self.set_name(node.idx), node.type)

    @when(ParamNode)
    def visit(self, node):
        ###############################
        # node.id -> str
        # node.type -> type
        ###############################

        return ParamNode(self.set_name(node.idx), node.type)

    @when(VarDeclarationNode)
    def visit(self, node):
        ###############################
        # node.id = str
        # node.type = str
        # node.expr = ExpressionNode
        ###############################
        expression = self.visit(node.expr)
        return VarDeclarationNode(self.set_name(node.id), node.type, expression)

    @when(ArrayDeclarationNode)
    def visit(self, node):
        ###############################
        # node.id = str
        # node.type = str
        # node.expr = ExpressionNode
        ###############################
        expression = self.visit(node.expr)
        return ArrayDeclarationNode(node.type, self.set_name(node.id), expression)

    @when(GroupVarDeclarationNode)
    def visit(self, node):
        ###############################
        # node.type = str
        # node.id = str
        # node.collec = str
        # node.init = ExpressionNode
        # node.len = ExpressionNode
        ###############################
        init = self.visit(node.init)
        lenn = self.visit(node.len)
        col = self.visit(node.collec)
        return GroupVarDeclarationNode(node.type, self.set_name(node.id), col, init, lenn)

    @when(LoopNode)
    def visit(self, node):
        # node.expr = ExpresionNode
        # node.body = [ ExpresionNode ... ]
        expr = self.visit(node.expr)
        body = []

        for ex in node.body:
            inst = self.visit(ex)
            body += inst if type(inst) is list else [inst]
        return LoopNode(expr, body)

    @when(DynamicCallNode)
    def visit(self, node):
        arg = []
        for a in node.args:
            arg.append(self.visit(a))
        h = self.visit(node.head)
        return DynamicCallNode(node.lex, h, arg, node.return_type)
    
    @when(CallNode)
    def visit(self, node):
        arg = []

        for a in node.args:
            arg.append(self.visit(a))
        return CallNode(self.fun_names(node.lex), arg, node.return_type)

    @when(IterNode)
    def visit(self, node):
        # node.collec = collec
        # node.expr = expr
        # node.dir = dir   
        name = self.visit(node.collec)
        temp = f"temp_{len(self.temp_names)}" 
        expr = self.visit(node.expr)
        self.temp_names.append(temp)
        lines = []
        if node.dir == "prev":
            lines.append(VarDeclarationNode(temp, 'int', MinusNode(CallNode("len", [
                         name], return_type=Int()), ConstantNode(1, 'int', return_type=Int()), return_type=Int())))
            link = LinkNode(
                GetIndexNode(name, VariableNode(
                    temp, return_type=Int())),
                GetIndexNode(name, MinusNode(VariableNode(
                    temp, return_type=Int()), ConstantNode(1, 'int', return_type=Int()))),
                expr
            )

            lines.append(LoopNode(GtNode(VariableNode( temp, Int()), ConstantNode(0, 'int', return_type=Int()), return_type=Bool()), [link, AssignNode(temp, MinusNode(
                VariableNode(temp, return_type=Int()), ConstantNode(1, 'int', return_type=Int()), return_type=Int()))]))
        else:
            lines.append(VarDeclarationNode(
                temp, 'int', ConstantNode(0, 'int', return_type=Int())))
            link = LinkNode(
                GetIndexNode(name, VariableNode(
                    temp, return_type=Int())),
                GetIndexNode(name, PlusNode(VariableNode(
                    temp, return_type=Int()), ConstantNode(1, 'int', return_type=Int()))),
                expr
            )
            lines.append(LoopNode(LtNode(VariableNode( temp, Int()), MinusNode(CallNode("len", [name], return_type=Int()), ConstantNode(1, 'int', return_type=Int()), return_type=Int()), return_type=Bool()), [
                         link, AssignNode(temp, PlusNode(VariableNode(temp, return_type=Int()), ConstantNode(1, 'int', return_type=Int())))]))

        return lines

    @when(BorrowNode)
    def visit(self, node):
        # node.from_collec = str
        # node.to_collec = str
        # node.init = ExpressionNode
        # node.len = ExpresionNode 
        fromm = self.visit(node.from_collec)
        to = self.visit(node.to_collec)
        init = self.visit(node.init)
        lenn = self.visit(node.len)
        return BorrowNode(fromm, to, init, lenn) 
    
    
    @when(ConditionNode)  
    def visit(self, node):
        # node.expr = ExpresionNode
        # node.body = [ ExpresionNode ... ]
        expr = self.visit(node.expr)
        body = []

        for ex in node.body:
            inst = self.visit(ex)
            body += inst if type(inst) is list else [inst]

        return ConditionNode(expr, body)

    @when(AssignNode)
    def visit(self, node):
        expr = self.visit(node.expr)

        return AssignNode(self.set_name(node.id), expr)

    @when(SetIndexNode)
    def visit(self, node):
        return SetIndexNode(self.set_name(node.id), self.visit(node.index), self.visit(node.expr))

    @when(ConstantNode)
    def visit(self, node):
        return node

    @when(VariableNode)
    def visit(self, node):
        return VariableNode(self.set_name(node.lex), node.return_type)

    @when(InstantiateNode)
    def visit(self, node):
        return node

    @when(SpecialNode)
    def visit(self, node):
        return node

    @when(NotNode)
    def visit(self, node):
        return NotNode(self.visit(node.expr), node.return_type)

    @when(PlusNode)
    def visit(self, node):
        return PlusNode(self.visit(node.left), self.visit(node.right), node.return_type)

    @when(MinusNode)
    def visit(self, node):
        return MinusNode(self.visit(node.left), self.visit(node.right), node.return_type)

    @when(StarNode)
    def visit(self, node):
        return StarNode(self.visit(node.left), self.visit(node.right), node.type)

    @when(DivNode)
    def visit(self, node):
        return DivNode(self.visit(node.left), self.visit(node.right), node.return_type)

    @when(ModNode)
    def visit(self, node):
        return ModNode(self.visit(node.left), self.visit(node.right), node.return_type)

    @when(VectNode)
    def visit(self, node):
        return VectNode(self.visit(node.left), self.visit(node.right), node.return_type)

    @when(AndNode)
    def visit(self, node):
        return AndNode(self.visit(node.left), self.visit(node.right), node.return_type)

    @when(OrNode)
    def visit(self, node):
        return (self.visit(node.left), self.visit(node.right), node.return_type)

    @when(EqNode)
    def visit(self, node):
        return (self.visit(node.left), self.visit(node.right), node.return_type)

    @when(EqlNode)
    def visit(self, node):
        return EqlNode(self.visit(node.left), self.visit(node.right), node.type)

    @when(EqgNode)
    def visit(self, node):
        return EqgNode(self.visit(node.left), self.visit(node.right), node.return_type)

    @when(GtNode)
    def visit(self, node):
        return GtNode(self.visit(node.left), self.visit(node.right), node.return_type)

    @when(LtNode)
    def visit(self, node):
        return LtNode(self.visit(node.left), self.visit(node.right), node.return_type)

    @when(GetIndexNode)
    def visit(self, node):
        return GetIndexNode(self.visit(node.left), self.visit(node.right), node.return_type)

    @when(SliceNode)
    def visit(self, node):
        return node

    @when(LinkNode)
    def visit(self, node):
        return LinkNode(self.visit(node.left), self.visit(node.right), self.visit(node.expr))

    @when(ArrayNode)
    def visit(self, node):
        elems = []
        for e in node.elements:
            elems.append(self.visit(e))
        return ArrayNode(elems, node.return_type)
