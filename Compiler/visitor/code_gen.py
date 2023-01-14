import itertools
from Compiler.semantic.types import *
import Compiler.utils as util
from Compiler.semantic.language import *
from .visitor import *
from ._def import *
import re

__all__ = ['CodeGenVisitor']


def replace(dict,code):
    repl_pattern = '|'.join([f'({key})' for key in dict.keys()])
    def create_repl_func(repl_dict):
        def repl_func(match):
            return repl_dict[match.group()]
        return repl_func
    final_code = re.sub(repl_pattern,create_repl_func(dict),code)
    return final_code


init_code = """
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
<tab>old_dir = <origin>[0].direction
<tab><origin>[0].direction = rot
<body><tab><origin>[0].direction = old_dir
"""

param_code = '<id>'

assign_code = '<id> = <value>'

take_code = '<id> = []\n<tab>borrow(<src>,<id>,<init>,<len>)'

declaration_code = '<id> = <expr>'

while_code = 'while(<cond>):\n<body>'

borrow_code = 'borrow(<src>,<dst>,<init>,<len>)'

if_code = 'if(<cond>):\n<body>'

var_code = '<id>'

vec_code = '(<a>,<b>)'

true_code = 'True'

false_code = 'False'

const_arr_code = '[<body>]'

set_index_code = '<id>[<index>] = <expr>'

get_index_code = '<id>[<index>]'

slice_code = '[index for index in range(<a>,<b> + 1)]'

link_code = "of_rel(<left>,<right>,<expr>)"

return_code = 'return'

break_code = 'break'

continue_code = 'continue'

call_code = '<id>(<params>)'

change_line_code = '\n'

len_code = 'len(<id>)'

array_declaration_code = '<id> = <array>'

dynamic_call_code = '<head>.<id>(<args>)'

line_up_code = """<id>(<args>,dir_tuple[<rot>])
<tab>runner.set_and_check_positions(<origin>,<pos>)
"""
array_code = '[<content>]'

NotNode_code = 'not <expr>'

PlusNode_code = '<left> + <right>'

PlusNode_vector_code = 'sum_vec(<a>, <b>)'

MinusNode_code = '<left> - <right>'

MinusNode_vector_code = 'sum_vec(<a>, scalar_product(<b>, -1))'

StarNode_code = '<left> * <right>'

StarNode_vector_code = 'scalar_product(<a>, <b>)'

DivNode_code = '<left> // <right>'

ModNode_code = '<left> % <right>'

AndNode_code = '<left> and <right>'

OrNode_code = '<left> or <right>'

EqNode_code = '<left> == <right>'

NonEqNode_code = '<left> != <right>'

EqlNode_code = '<left> <= <right>'

EqgNode_code = '<left> >= <right>'

GtNode_code = '<left> > <right>'

LtNode_code = '<left> < <right>'

python_tamplate = (init_code,start_step_code,func_def_code
                ,param_code,assign_code ,take_code,declaration_code
                ,while_code, borrow_code, if_code,var_code,vec_code
                ,true_code, false_code, const_arr_code, set_index_code
                ,return_code, break_code, continue_code,call_code,change_line_code
                ,line_up_code, array_code ,NotNode_code, PlusNode_code, MinusNode_code
                , StarNode_code, DivNode_code, ModNode_code, AndNode_code, OrNode_code,dynamic_call_code
                , EqNode_code, NonEqNode_code, EqlNode_code, EqgNode_code, GtNode_code, LtNode_code
                , PlusNode_vector_code, MinusNode_vector_code, StarNode_vector_code,array_declaration_code
                ,get_index_code,slice_code,link_code,len_code)

class CodeGenVisitor(object):
    def __init__(self,init_code,start_step_code,func_def_code
                ,param_code,assign_code ,take_code,declaration_code
                ,while_code, borrow_code, if_code,var_code,vec_code
                ,true_code, false_code, const_arr_code, set_index_code
                ,return_code, break_code, continue_code,call_code,change_line_code
                ,line_up_code, array_code ,NotNode_code, PlusNode_code, MinusNode_code
                , StarNode_code, DivNode_code, ModNode_code, AndNode_code, OrNode_code,dynamic_call_code
                , EqNode_code, NonEqNode_code, EqlNode_code, EqgNode_code, GtNode_code, LtNode_code
                , PlusNode_vector_code, MinusNode_vector_code, StarNode_vector_code,array_declaration_code
                ,get_index_code,slice_code,link_code,len_code):
        
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
        self.slice_code = slice_code
        #keyword (<body>: coma separated numbers)
        self.const_arr_code = const_arr_code
        #keyword (<id>: nombre del array a indexar)
        #        (<index>: expresion que da el indice )
        #        (<body> : expresion a asignar)
        self.set_index_code = set_index_code
        self.len_code = len_code
        self.return_code = return_code
        self.break_code = break_code
        self.continue_code = continue_code
        #keyword (<id>: nombre de la funcion a llamar)
        #        (<params>: los argumentos separados por coma)
        self.call_code = call_code
        #keyword (<head>: objecto sobre el que se hace el llamado)
        #        (<id>: funcion que se llama)
        #        (<args>: argumentos)
        self.dynamic_call_code = dynamic_call_code
        self.change_line_code = change_line_code
        #keyword (<id>: nombre de la fomracion)
        #        (<args>: argumentos de la formacion)
        #        (<rot>: rotacion) 
        #        (<origin>: el nodo que es centro de la formacion)
        #        (<pos>: la posición donde se va a poner el centro)
        self.line_up_code = line_up_code
        self.get_index_code = get_index_code
        #keyword (<content>: las expresiones con las que se inicializa el array)
        self.array_code = array_code
        #keyword (<id>: nombre de la variable, <array>: el array, <type>: el tipo del array)
        self.array_declaration_code = array_declaration_code
        self.link_code = link_code

        self.NotNode_code = NotNode_code
        self.PlusNode_code = PlusNode_code
        self.MinusNode_code = MinusNode_code
        self.StarNode_vector_code = StarNode_vector_code
        self.PlusNode_vector_code = PlusNode_vector_code
        self.MinusNode_vector_code = MinusNode_vector_code
        self.StarNode_code = StarNode_code
        self.DivNode_code = DivNode_code
        self.ModNode_code = ModNode_code
        self.AndNode_code = AndNode_code
        self.OrNode_code = OrNode_code
        self.EqNode_code = EqNode_code
        self.NonEqNode_code = NonEqNode_code
        self.EqlNode_code = EqlNode_code
        self.EqgNode_code = EqgNode_code
        self.GtNode_code = GtNode_code
        self.LtNode_code = LtNode_code

        
    def build_body_arr(self,body,current_depth):
        result_body = []
        for line in body:
            result_body.append('\t'*current_depth)
            result_body.append(self.visit(line,current_depth))
            result_body.append(self.change_line_code)
        return result_body
    
    @on('node')
    def visit(self, node,depth,count):
        pass

    @when(ProgramNode)
    def visit(self, node: ProgramNode, depth: int = 0):
        arr = []
        arr.append(self.init_code)
        arr.append(self.visit(node.definitions, depth))
        arr.append(self.visit(node.begin_with, depth))
        return ''.join(arr)
        

    @when(DefinitionsNode)
    def visit(self, node: DefinitionsNode, depth: int = 0):
        return '\n'.join([self.visit(child,depth) for child in node.functions]) + '\n'

    @when(BeginWithNode)
    def visit(self, node: BeginWithNode, depth: int = 0):
        return ''.join([self.visit(child,depth,node.num) for child in node.step])

    @when(StepNode)
    def visit(self, node: StepNode, depth: int = 0,count: int = 0):
        
        result = ['\t'*depth,replace({'<count>':str(count)}
                          ,self.start_step_code)]
        # node.body una lista de begin call node
        for call in node.instructions:
            result.append('\t'*depth)
            result.append(self.visit(call,depth))
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
                       ,'<id>': node.id
                       ,'<params>': ','.join([self.visit(prm,depth) for prm in node.params])
                       ,'<body>': ''.join(body)
                       ,'<origin>': self.visit(node.params[0],depth)}
                       ,self.func_def_code)

    @when(ParamNode)
    def visit(self,node: ParamNode,depth):
        return replace({'<id>':node.idx
                       ,'<type>': node.type}
                       ,self.param_code)      

    @when(VarDeclarationNode)
    def visit(self, node: VarDeclarationNode , depth: int = 0):
        return replace({'<id>' : node.id
                       ,'<type>':node.type
                       ,'<expr>':self.visit(node.expr,depth)}
                       ,self.declaration_code)

    @when(AssignNode)
    def visit(self,node: AssignNode, depth: int = 0):
        return replace({'<id>' : node.id
                       ,'<value>': self.visit(node.expr,depth)}
                       ,self.assign_code )



    @when(GroupVarDeclarationNode)
    def visit(self, node: GroupVarDeclarationNode, depth: int = 0):
        # collec de donde
        # init donde empieza
        # len hasta donde
        # id a donde
        
        return replace({'<tab>' : '\t'*depth
                       ,'<id>'  : node.id
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
                       ,'<array>': self.visit(node.expr,depth)
                       ,'<type>': node.type},self.array_declaration_code)
        
    @when(SetIndexNode)
    def visit(self,node: SetIndexNode,depth: int = 0):
        return replace({'<id>': node.id
                       ,'<index>': self.visit(node.index,depth)
                       ,'<expr>': self.visit(node.expr,depth)
                       ,'<tab>': '\t'*depth}
                       ,self.set_index_code)

    @when(ConstantNode)#numeros, direc, bool, array
    def visit(self,node : ConstantNode,depth: int = 0):
        if(type(node.return_type) == Int):
            return str(node.lex)
        elif(type(node.return_type) == Vector):
            return replace({'<a>': str(node.lex[0])
                           ,'<b>': str(node.lex[1])}
                           ,self.vec_code) 
        elif(type(node.return_type) == Bool):
            if(node.lex):
                return self.true_code
            return self.false_code
        elif(type(node.return_type) == Array):
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
    def visit(self,node:BeginCallNode,depth):
        first_arg = self.visit(ArrayNode([GetIndexNode(VariableNode('G'), ConstantNode(index,'int',Int())) for index in node.args[0].lex]),depth)
        args = [self.visit(item,depth) for item in node.args[1:]]
        args.insert(0,first_arg)
        origin = self.visit(GetIndexNode(VariableNode('G'), ConstantNode(node.args[0].lex[0],'int',Int())),depth)
        return replace({'<id>': node.lex
                       ,'<args>': ','.join(args)
                       ,'<rot>': self.visit(node.rot,depth)
                       ,'<tab>': '\t'*depth
                       ,'<origin>': origin
                       ,'<pos>': self.visit(node.poss,depth)}
                       ,self.line_up_code)

    @when(DynamicCallNode)
    def visit(self,node : DynamicCallNode,depth):
        if(node.lex == 'len'):
            return replace({'<id>':self.visit(node.head,depth)},self.len_code)
        return replace({'<head>':self.visit(node.head,depth)
                       ,'<id>':node.lex
                       ,'<args>':','.join([self.visit(arg) for arg in node.args])}
                       ,self.dynamic_call_code)
    

    @when(ArrayNode)
    def visit(self,node:ArrayNode,depth):
        return replace({'<content>': ','.join([self.visit(cont,depth) for cont in node.elements])},self.array_code)


    @when(NotNode)
    def visit(self, node :NotNode, depth :int = 0):
        return replace({'<expr>': self.visit(node.expr, depth)}, self.NotNode_code)
    
    @when(PlusNode)
    def visit(self, node :PlusNode, depth :int = 0):
        if type(node.left.return_type) == Int:
            return replace({'<left>': self.visit(node.left, depth), '<right>': self.visit(node.right, depth) }, self.PlusNode_code)
        elif type(node.left.return_type) == Vector:
            return replace({'<a>': self.visit(node.left, depth), '<b>': self.visit(node.right, depth) }, self.PlusNode_vector_code)
            

    @when(MinusNode)
    def visit(self, node :MinusNode, depth :int = 0):
        if type(node.left.return_type) == Int:
            return replace({'<left>': self.visit(node.left, depth), '<right>': self.visit(node.right, depth) }, self.PlusNode_code)
        elif type(node.left.return_type) == Vector:
            return replace({'<a>': self.visit(node.left, depth), '<b>': self.visit(node.right, depth) }, self.PlusNode_vector_code)
         

    @when(StarNode)
    def visit(self, node :StarNode, depth :int = 0):
        if node.left.return_type is Int and node.right.return_type is Int:
            return replace({'<left>': self.visit(node.left, depth), '<right>': self.visit(node.right, depth) }, self.PlusNode_code)
        elif node.left.return_type is Vector or node.right.return_type is Vector:
            if node.right.return_type is Vector:
                node.left , node.right = node.right, node.left
            return replace({'<a>': self.visit(node.left, depth), '<b>': self.visit(node.right, depth) }, self.PlusNode_vector_code)
    

    @when(DivNode)
    def visit(self, node :DivNode, depth :int = 0):
        return replace({'<left>': self.visit(node.left, depth), '<right>': self.visit(node.right, depth) }, self.DivNode_code)
   

    @when(ModNode)
    def visit(self, node :ModNode, depth :int = 0):
        return replace({'<left>': self.visit(node.left, depth), '<right>': self.visit(node.right, depth) }, self.ModNode_code)
        

    @when(AndNode)
    def visit(self, node :AndNode, depth :int = 0):
        return replace({'<left>': self.visit(node.left, depth), '<right>': self.visit(node.right, depth) }, self.AndNode_code)


    @when(OrNode)
    def visit(self, node :OrNode, depth :int = 0):
        return replace({'<left>': self.visit(node.left, depth), '<right>': self.visit(node.right, depth) }, self.OrNode_code)



    @when(EqNode)
    def visit(self, node :EqNode, depth :int = 0):
        return replace({'<left>': self.visit(node.left, depth), '<right>': self.visit(node.right, depth) }, self.EqNode_code)



    @when(NonEqNode)
    def visit(self, node :NonEqNode, depth :int = 0):
        return replace({'<left>': self.visit(node.left, depth), '<right>': self.visit(node.right, depth) }, self.NonEqNode_code)
        


    @when(EqlNode)
    def visit(self, node :EqlNode, depth :int = 0):
        return replace({'<left>': self.visit(node.left, depth), '<right>': self.visit(node.right, depth) }, self.EqlNode_code)
        


    @when(EqgNode)
    def visit(self, node :EqgNode, depth :int = 0):
        return replace({'<left>': self.visit(node.left, depth), '<right>': self.visit(node.right, depth) }, self.EqgNode_code)



    @when(GtNode)
    def visit(self, node :GtNode, depth :int = 0):
        return replace({'<left>': self.visit(node.left, depth), '<right>': self.visit(node.right, depth) }, self.GtNode_code)



    @when(LtNode)
    def visit(self, node :LtNode, depth :int = 0):
        return replace({'<left>': self.visit(node.left, depth), '<right>': self.visit(node.right, depth) }, self.LtNode_code)
       


    @when(VectNode)
    def visit(self, node :VectNode, depth :int = 0):
        return replace({'<a>': self.visit(node.left,depth)
                        ,'<b>': self.visit(node.right,depth)}
                        ,self.vec_code)

    @when(GetIndexNode)
    def visit(self,node: GetIndexNode, depth:int = 0):
        return replace({'<id>': self.visit(node.left,depth)
                       ,'<index>': self.visit(node.right,depth)}
                       ,self.get_index_code)
    @when(SliceNode)
    def visit(self,node: SliceNode, depth: int = 0):
        return replace({'<a>': str(node.left)
                       ,'<b>': str(node.right)}
                       ,self.slice_code)
    @when(LinkNode)
    def visit(self,node: LinkNode, depth: int = 0):
        return replace({'<left>': self.visit(node.left,depth)
                       ,'<right>':self.visit(node.right,depth)
                       ,'<expr>': self.visit(node.expr,depth)
                       ,'<tab>': '\t'*depth}
                       ,self.link_code)

