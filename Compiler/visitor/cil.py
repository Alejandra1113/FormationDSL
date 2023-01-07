import Compiler.utils as util
from Compiler.semantic.language import *
from .visitor import *
from ._def import *

__all__ = ['CilVisitor']

class CilVisitor:
    def __init__(self, context):
        self.current_type = None
        self.current_method = None
        self.current_function = None
        self.context = context
        
    @property
    def params(self):
        return self.current_function.params
    
    @property
    def localvars(self):
        return self.current_function.localvars
    
    @property
    def instructions(self):
        return self.current_function.instructions
    
    def register_local(self, vinfo):
        vinfo.name = f'local_{self.current_function.name[9:]}_{vinfo.name}_{len(self.localvars)}'
        local_node = cil.LocalNode(vinfo.name)
        self.localvars.append(local_node)
        return vinfo.name

    def define_internal_local(self):
        vinfo = VariableInfo('internal', None)
        return self.register_local(vinfo)

    def register_instruction(self, instruction):
        self.instructions.append(instruction)
        return instruction
    
    def to_function_name(self, method_name, type_name):
        return f'function_{method_name}_at_{type_name}'
    
    def register_function(self, function_name):
        function_node = cil.FunctionNode(function_name, [], [], [])
        self.dotcode.append(function_node)
        return function_node
    
    def register_type(self, name):
        type_node = cil.TypeNode(name)
        self.dottypes.append(type_node)
        return type_node

    def register_data(self, value):
        vname = f'data_{len(self.dotdata)}'
        data_node = cil.DataNode(vname, value)
        self.dotdata.append(data_node)
        return data_node
     
    @on('node')
    def visit(self, node):
        pass
    
    @when(ProgramNode)
    def visit(self, node, scope):
        
        ######################################################
        # node.declarations -> [ ClassDeclarationNode ... ]
        # node.beginWith -> beginWithNode
        ######################################################
        
        # self.current_function = self.register_function('entry')
        # instance = self.define_internal_local()
        # result = self.define_internal_local()
        # main_method_name = self.to_function_name('main', 'Main')
        # self.register_instruction(cil.AllocateNode('Main', instance))
        # self.register_instruction(cil.ArgNode(instance))
        # self.register_instruction(cil.StaticCallNode(main_method_name, result))
        # self.register_instruction(cil.ReturnNode(0))
        # self.current_function = None
        
        for declaration, child_scope in zip(node.declarations, scope.children):
            self.visit(declaration, child_scope)

        return ProgramNode(self.functioons, node.beggin_with)