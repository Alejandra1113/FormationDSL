import itertools
import Compiler.utils as util
from Compiler.semantic.language import *
from .visitor import *
from ._def import *
import re

__all__ = ['ScopeCheckerVisitor']


def replace(dict,code):
    repl_pattern = '|'.join([f'({key})' for key in dict.keys()])
    def create_repl_func(repl_dict):
        def repl_func(match):
            return repl_dict[match.group()]
        return repl_func
    final_code = re.sub(repl_pattern,create_repl_func(dict),code)
    return final_code


init_code = """
from unittest import result
from IA.formations import Formation
from entities.utils import DIRECTIONS, direction_to_int, direction_to_tuple, int_to_direction,dir_tuple
from enum import Enum

rpos = Enum('rpos', 'next prev')

class IncompleteNodeException(Exception):
    def __init__(self,text):
        Exception.__init__(self,text)

class InconsistentNodeException(Exception):
    def __init__(self,text):
        Exception.__init__(self,text)

class SimpleFormationNode:
    def __init__(self,direction_var):
        self.position = None
        self.childs = []
        self.direction_var = direction_var
        self.last_visit = 0

    def add_child(self,node,rel):
        real_rel = SimpleFormationNode.rot_rel(rel,self.direction_var.value)
        self.childs.append((node,real_rel))

    @property
    def direction(self):
        return self.direction_var.value
    
    @direction.setter
    def direction(self,dir):
        self.direction_var.value = dir

    def create_formation(count):
        dir_var = DirectionVar()
        result = []
        for _ in range(count):
            result.append(SimpleFormationNode(dir_var))
        return result

    def rot_rel(rel,direction):
        i,j = rel
        #computing new axis
        #componentes del vector canonico I para esta rotacion
        Ican_i,Ican_j = direction_to_tuple(direction)
        #componentes del vector canonico J para esta rotacion
        Jcan_i,Jcan_j = direction_to_tuple(int_to_direction((direction_to_int(direction) + 2)%8))
        return (i*Ican_i + j*Jcan_i,i*Ican_j + j*Jcan_j)
    
class DirectionVar:
    def __init__(self,direction = DIRECTIONS.N):
        self.value = direction

class PosRunner:
    def __init__(self):
        self.last_run = 0

    def set_and_check_positions(self,origin : SimpleFormationNode, pos):
        if(origin.position):
            if(pos != origin.position):
                raise InconsistentNodeException("Two diferent positions were resolved for this node")
        else:
            origin.position = pos
        self.last_run += 1
        origin.last_visit = self.last_run
        self.inner_set_and_check_positions(origin)

    def inner_set_and_check_positions(self,origin : SimpleFormationNode):
        for child, rel in origin.childs:
            if(child.position):
                if(sum_vec(origin.position,rel) != child.position):
                    raise InconsistentNodeException("Two diferent positions were resolved for this node")
                elif(child.last_visit == self.last_run):
                    continue
            else:
                child.position = sum_vec(origin.position,rel)
            child.last_visit = self.last_run
            self.inner_set_and_check_positions(child)

def dos_filas(group,direction):
    old_dir = group[0].direction
    group[0].direction = direction
    temp = len(group)//2
    resto = len(group)%2
    i = 0
    while(i < temp + resto):
        if(i < temp):
            group[temp + i].add_child(group[i],(1,0))
            group[i].add_child(group[temp + i],(-1,0))
        
        if(i > 0):
            group[temp + i - 1].add_child(group[temp + i],(0,1))
            group[temp + i].add_child(group[temp + i - 1],(0,-1))
        i += 1
    group[0].direction = old_dir

def borrow(src_list,dst_list,length,starting_at):
    for i in range(starting_at,starting_at + length):
        dst_list.append(src_list.pop(i))


def sum_vec(a,b):
    x_a, y_a = a
    x_b, y_b = b
    return (x_a + x_b,y_a + y_b)

def scalar_product(vec,a):
    x,y = vec
    return (x*a, y*a)

def of_rel(node_a,node_b,vec):
    node_a.add_child(node_b,vec)
    node_b.add_child(node_a,scalar_product(vec,-1))

"""

start_step_code = """G = SimpleFormationNode.create_formation(<count>)
runner = PosRunner()"""


func_def_code = """def <id>(<params>,rot):
<tab>old_dir = group[0].direction
<tab>group[0].direction = direction
<body><tab>group[0].direction = old_dir
"""

param_code = '<id>'

assign_code = '<id> = <value>'

take_code = '<id> = []\n<tab>borrow(<src>,<id>,<init>,<len>)'

declaration_code = '<id> = None'

while_code = 'while(<cond>):\n<body>'

borrow_code = 'borrow(<src>,<dst>,<init>,<len>)'

if_code = 'if(<cond>):\n<body>'

var_code = '<id>'

vec_code = '(<a>,<b>)'

true_code = 'True'

false_code = 'False'

const_arr_code = '[<body>]'

set_index_code = '<id>[<index>] = <expr>'

return_code = 'return'

break_code = 'break'

continue_code = 'continue'

call_code = '<id>(<params>)'

change_line_code = '\n'

line_up_code = """<id>(<args>,dir_tuple[<rot>])
<tab>runner.set_and_check_positions(<origin>,<pos>)
"""
array_code = '[<content>]'


class CodeGenVisitor(object):
    def __init__(self,init_code,start_step_code,func_def_code
                ,param_code,assign_code ,take_code,declaration_code
                ,while_code, borrow_code, if_code,var_code,vec_code
                ,true_code, false_code, const_arr_code, set_index_code
                ,return_code, break_code, continue_code,call_code,change_line_code
                ,line_up_code, array_code):
        self.init_code = init_code
        #keyword (<count>: cantidad de individuos)
        self.start_step_code = start_step_code
        #keyword (<id>: nombre de la funcion, <params>: nombre de los parametros, <body>: el cuerpo)
        self.func_def_code = func_def_code
        #keyword (<id>: nombre, <type>: tipo)
        self.param_code = param_code
        #keyword (<id>: nombre de la variable, <value>: valor a asignar)
        self.assign_code = assign_code
        #keyword (<id>: nombre de la variable donde guardar el grupo)
        #        (<src>: de donde se sacan los elementos)
        #        (<init>: indice de donde se empieza a tomar)
        #        (<len>: cuantos se van a tomar)
        #        (<type>: tipo de la variable que va a recibir)
        self.take_code = take_code
        #keyword  (<type>: tipo de la variable, <id>: id de la variable)
        self.declaration_code = declaration_code
        #keyword (<cond>: la condicion, <body>: el cuerpo)
        self.while_code = while_code
        #keyword (<src>: fuente)
        #        (<dst>: destino)
        #        (<init>: posicion de inicio)
        #        (<len>: cantidad)
        self.borrow_code = borrow_code
        #keyword (<cond>: condicion)
        #        (<body>: cuerpo)
        self.if_code = if_code
        #keyword (<id>: id de la variable)
        self.var_code = var_code
        #keyword (<a>: numero a la izda
        #         <b>: numero a la dcha)
        self.vec_code = vec_code
        self.true_code = true_code
        self.false_code = false_code
        #keyword (<body>: coma separated numbers)
        self.const_arr_code = const_arr_code
        #keyword (<id>: nombre del array a indexar)
        #        (<index>: expresion que da el indice )
        #        (<body> : expresion a asignar)
        self.set_index_code = set_index_code
        self.return_code = return_code
        self.break_code = break_code
        self.continue_code = continue_code
        #keyword (<id>: nombre de la funcion a llamar)
        #        (<params>: los argumentos separados por coma)
        self.call_code = call_code
        self.change_line_code = change_line_code
        #keyword (<id>: nombre de la fomracion)
        #        (<args>: argumentos de la formacion)
        #        (<rot>: rotacion) 
        #        (<origin>: el nodo que es centro de la formacion)
        #        (<pos>: la posición donde se va a poner el centro)
        self.line_up_code = line_up_code
        #keyword (<content>: las expresiones con las que se inicializa el array)
        self.array_code = array_code

    def build_body_arr(self,body,current_depth):
        result_body = []
        for line in body:
            result_body.append('\t'*current_depth)
            result_body.append(self.visit(line,current_depth))
            result_body.append(self.change_line_code)
        return result_body

    @on('node')
    def visit(self, node,depth):
        pass

    @when(ProgramNode)
    def visit(self, node: ProgramNode, depth: int = 0):
        arr = []
        arr.append(self.init_code)
        arr.append(self.visit(node.definition, depth))
        arr.append(self.visit(node.begin_wit, depth))
        return ''.join(arr)
        

    @when(DefinitionsNode)
    def visit(self, node: DefinitionsNode, depth: int = 0):
            
        return ''.join([self.visit(child,depth) for child in node.functions])

    @when(BeginWithNode)
    def visit(self, node: BeginWithNode, depth: int = 0):
        return ''.join([self.visit(child,depth,node.num) for child in node.step])

    @when(StepNode)
    def visit(self, node: StepNode, depth: int = 0,count: int = 0):
        
        result = ['\t'*depth,replace({'<count>':count}
                          ,self.start_step_code)]
        # node.body una lista de begin call node
        for call in node.body:
            result.append('\t'*depth)
            result.append(self.visit(call,depth,count))
        return self.change_line_code.join(result) + self.change_line_code

    @when(FuncDeclarationNode)
    def visit(self, node: FuncDeclarationNode, depth: int = 0):
        # node.idx identificador de las funciones
        # node.params tipos y nombres de los parámetros
        # node.params.idx
        # node.params.type
        # node.body
        body = self.build_body_arr(node.body,depth + 1)
        return replace({'<tab>': '\t'*(depth + 1)
                       ,'<id>': node.idx 
                       ,'<params>': ','.join([self.visit(prm,depth) for prm in node.params])
                       ,'<body>': ''.join(body)}
                       ,self.func_def_code)

    @when(ParamNode)
    def visit(self,node: ParamNode,depth):
        return replace({'<id>':node.idx
                       ,'<type>': node.type}
                       ,self.param_code)      

    @when(VarDeclarationNode)
    def visit(self, node: VarDeclarationNode , depth: int = 0):
        return replace({'<id>' : node.id
                       ,'<type>':node.type}
                       ,self.declaration_code)

    @when(AssignNode)
    def visit(self,node: AssignNode, depth: int = 0):
        return replace({'<id>' : self.visit(node.id,depth)
                       ,'<value>': self.visit(node.expr,depth)}
                       ,self.assign_code )


    @when(GroupVarDeclarationNode)
    def visit(self, node: GroupVarDeclarationNode, depth: int = 0):
        # collec de donde
        # init donde empieza
        # len hasta donde
        # id a donde
        
        return replace({'<tab>' : '\t'*depth
                       ,'<id>'  : self.visit(node.id,depth)
                       ,'<src>' : self.visit(node.collec,depth)
                       ,'<init>': self.visit(node.init,depth)
                       ,'<len>' : self.visit(node.len,depth)
                       ,'<type>': node.type }
                       , self.take_code)
    @when(LoopNode)
    def visit(self, node: LoopNode, depth: int = 0):
        body = self.build_body_arr(node.body,depth + 1)
        return replace({'<cond>': self.visit(node.expr,depth)
                       ,'<body>': ''.join(body)}
                       ,self.while_code)

    @when(BorrowNode)
    def visit(self, node: BorrowNode, depth: int = 0):
        return replace({'<src>' :  self.visit(node.from_collec,depth)
                       ,'<dst>' :  self.visit(node.to_collec,depth)
                       ,'<init>':  self.visit(node.init,depth)
                       ,'<len>' :  self.visit(node.len,depth)}
                       ,self.borrow_code)

    @when(ConditionNode)
    def visit(self, node: ConditionNode, depth: int = 0):
        body = self.build_body_arr(node.body,depth + 1)
        return replace({'<cond>': self.visit(node.expr,depth)
                       ,'<body>': ''.join(body)}
                       , self.if_code)
    

    @when(ArrayDeclarationNode)
    def visit(self,node: ArrayDeclarationNode,depth: int = 0):
        return replace({'<id>': node.id
                       ,'<value>': self.visit(node.expr,depth)})
        
    @when(SetIndexNode)
    def visit(self,node: SetIndexNode,depth: int = 0):
        return replace({'<id>': self.visit(node.id,depth)
                       ,'<index>': self.visit(node.expr,depth)
                       ,'<expr>': self.visit(node.expr,depth)
                       ,'<tab>': '\t'*depth}
                       ,self.set_index_code)

    @when(ConstantNode)#numeros, direc, bool, array
    def visit(self,node : ConstantNode,depth: int = 0):
        if(node.type.name ==  'num'):
            return str(node.lex)
        elif(node.type.name == 'vec'):
            return replace({'<a>': node.lex[0]
                           ,'<b>': node.lex[1]}
                           ,self.vec_code) 
        elif(node.type.name == 'bool'):
            if(node.lex):
                return self.true_code
            return self.false_code
        elif(node.type.name == 'array'):
            return replace({'<body>': ','.join([str(num) for num in node.lex])}
                           , self.const_arr_code)

    @when(VariableNode)
    def visit(self,node : VariableNode, depth : int = 0):
        return replace({'<id>': node.lex},self.var_code)
    
    @when(SpecialNode)
    def visit(self,node: SpecialNode, depth : int = 0):
        if(node.lex == 'return'):
            return self.return_code
        elif(node.lex == 'break'):
            return self.break_code
        return self.continue_code
        
    @when(CallNode)
    def visit(self,node: CallNode, depth: int = 0):
        return replace({'<id>': node.lex
                       ,'<params>': ','.join([self.visit(arg,depth) for arg in node.args])}
                       ,self.call_code)

    @when(BeginCallNode)
    def view(self,node:BeginCallNode,depth):
        first_arg = self.visit(ArrayNode([GetIndexNode(VariableNode('G'), ConstantNode(index,'num')) for index in node.args[0]]))
        args = [self.visit(item,depth) for item in node.args[1:]].insert(0,first_arg)
        origin = self.visit(GetIndexNode(VariableNode('G'), ConstantNode(node.args[0],'num')),depth)
        return replace({'<id>': node.lex
                       ,'<args>': ','.join(args)
                       ,'<rot>': self.visit(node.rot,depth)
                       ,'<tab>': '\t'*depth
                       ,'<origin>': origin
                       ,'<pos>': self.visit(node.poss,depth)}
                       ,self.line_up_code)

    @when(ArrayNode)
    def visit(self,node:ArrayNode,depth)
        return replace({'<content>': ','.join([self.visit(cont,depth) for cont in node.lex])})


    @when(NotNode)
    def visit(node :NotNode, depth :int = 0):
        pass


    @when(PlusNode)
    def visit(node :PlusNode, depth :int = 0):
        pass


    @when(MinusNode)
    def visit(node :MinusNode, depth :int = 0):
        pass


    @when(StarNode)
    def visit(node :StarNode, depth :int = 0):
        pass


    @when(DivNode)
    def visit(node :DivNode, depth :int = 0):
        pass


    @when(ModNode)
    def visit(node :ModNode, depth :int = 0):
        pass

    @when(BinaryLogicNode)
    def visit(node :BinaryLogicNode, depth :int = 0):
        pass


    @when(AndNode)
    def visit(node :AndNode, depth :int = 0):
        pass


    @when(OrNode)
    def visit(node :OrNode, depth :int = 0):
        pass


    @when(EqNode)
    def visit(node :EqNode, depth :int = 0):
        pass


    @when(NonEqNode)
    def visit(node :NonEqNode, depth :int = 0):
        pass


    @when(EqlNode)
    def visit(node :EqlNode, depth :int = 0):
        pass


    @when(EqgNode)
    def visit(node :EqgNode, depth :int = 0):
        pass


    @when(GtNode)
    def visit(node :GtNode, depth :int = 0):
        pass


    @when(LtNode)
    def visit(node :LtNode, depth :int = 0):
        pass


class VectNode(BinaryNode):
    pass

class GetIndexNode(BinaryNode):
    pass


class SliceNode(BinaryNode):
    pass


class LinkNode(TernaryNode):
    pass
