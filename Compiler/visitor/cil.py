import Compiler.utils as util
from Compiler.semantic.language import *
from .visitor import *
from ._def import *

__all__ = ['CilVisitor']


class CilVisitor(object):
    def __init__(self):
        self.var_names = { }
        self.temp_names = [ ]
    
    def set_name(self,id):
        name = self.var_names.get(id)
        if not name: 
            name = f"var_{len(self.var_names)}"
            self.var_names[id] = name
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

        return FuncDeclarationNode(node.id, params, body)

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
        # node.type1 = str
        # node.type2 = VarNode
        # node.expr = ExpressionNode
        ###############################   
        expression = self.visit(node.expr)
        return ArrayDeclarationNode(node.type1, node.type2, self.set_name(node.id), expression)
    
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
        g = self.visit(node.collec)
        return GroupVarDeclarationNode(node.type, self.set_name(node.id),g, init, lenn)
            
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
    
    @when(CallNode)
    def visit(self, node):
        arg = [] 
        
        for a in node.args:
            arg.append(self.visit(a))
        return CallNode(node.lex, arg)
         
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
            lines.append(VarDeclarationNode(name,"int",MinusNode(CallNode("len",[ name] ) ,ConstantNode(1,"int"))))
            link = LinkNode(
                            GetIndexNode(name,VariableNode(temp)), 
                            GetIndexNode(name,MinusNode(VariableNode(temp), ConstantNode(1,"int"))),
                            expr
                            )
            
            lines.append(LoopNode(GtNode(name,ConstantNode(0,"int")), [link, AssignNode(VariableNode(temp),MinusNode(VariableNode(temp),ConstantNode(1, "int")))]))   
        else:   
            lines.append(VarDeclarationNode(name,"int",ConstantNode(0, "int")))
            link = LinkNode(
                            GetIndexNode(name,VariableNode(temp)), 
                            GetIndexNode(name,PlusNode(VariableNode(temp), ConstantNode(1, "int"))),
                            expr
                            )
            lines.append(LoopNode(LtNode(name,MinusNode(CallNode("len",[ name] ) ,ConstantNode(1, "int"))), [link, AssignNode(VariableNode(temp),PlusNode(VariableNode(temp),ConstantNode(1, "int")))]))   
    
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
        name = self.visit(node.from_collec)
        return AssignNode(name ,expr)
    
    @when(SetIndexNode)
    def visit(self, node):                
        return SetIndexNode(self.visit(node.idx), self.visit(node.index), self.visit(self.expr))
    
                        
    @when(ConstantNode)
    def visit(self,node):
        return node

    @when(VariableNode)
    def visit(self,node):
        return VariableNode(self.set_name(node.lex))

    @when(InstantiateNode)
    def visit(self,node):
        return node

    @when(SpecialNode)
    def visit(self,node):
        return node
    

    @when(NotNode)
    def visit(self, node):
        return NotNode(self.visit(node.expr))


    @when(PlusNode)
    def visit(self, node):
        return PlusNode(self.visit(node.left), self.visit(node.right))


    @when(MinusNode)
    def visit(self, node):
        return MinusNode(self.visit(node.left), self.visit(node.right))


    @when(StarNode)
    def visit(self, node):
        return StarNode(self.visit(node.left), self.visit(node.right))


    @when(DivNode)
    def visit(self, node):
        return DivNode(self.visit(node.left), self.visit(node.right))


    @when(ModNode)
    def visit(self, node):
        return ModNode(self.visit(node.left), self.visit(node.right))


    @when(VectNode)
    def visit(self, node):
        return VectNode(self.visit(node.left), self.visit(node.right))


    @when(AndNode)
    def visit(self, node):
        return AndNode(self.visit(node.left), self.visit(node.right))


    @when(OrNode)
    def visit(self, node):
        return (self.visit(node.left), self.visit(node.right))


    @when(EqNode)
    def visit(self, node):
        return (self.visit(node.left), self.visit(node.right))


    @when(EqlNode)
    def visit(self, node):
        return EqlNode(self.visit(node.left), self.visit(node.right))


    @when(EqgNode)
    def visit(self, node):
        return EqgNode(self.visit(node.left), self.visit(node.right))


    @when(GtNode)
    def visit(self, node):
        return GtNode(self.visit(node.left), self.visit(node.right))


    @when(LtNode)
    def visit(self, node):
        return LtNode(self.visit(node.left), self.visit(node.right))


    @when(GetIndexNode)
    def visit(self, node):
        return GetIndexNode(self.visit(node.left), self.visit(node.right))


    @when(SliceNode)
    def visit(self, node):
        return node


    @when(LinkNode)
    def visit(self, node):
        return LinkNode(self.visit(node.left), self.visit(node.right), self.visit(node.expr))