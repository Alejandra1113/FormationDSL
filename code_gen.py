
from Compiler.pythonbackcode.utils import DIRECTIONS, direction_to_int, direction_to_tuple, int_to_direction,dir_tuple
from Compiler.pythonbackcode.formationroute import get_formation_route
from Compiler.pythonbackcode.UI import *
from enum import Enum
import pygame as pg 

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

def fun_0(var_0,var_1,rot):
	old_dir = var_0[0].direction
	var_0[0].direction = rot
	var_2 = 0
	var_3 = [1,2,3,4]
	while(var_2 < len(var_3)):
		var_3[var_2] = var_3[var_2] + 1
		var_2 = var_2 + 1
	var_0[0].direction = old_dir

def fun_1(var_0,rot):
	old_dir = var_0[0].direction
	var_0[0].direction = rot
	var_4 = len(var_0) // 2
	var_5 = len(var_0) % 2
	var_2 = 0
	while(var_2 < var_4 + var_5):
		if(var_2 < var_4):
			of_rel(var_0[var_4 + var_2],var_0[var_2],(1,0))
		if(var_2 > 0):
			of_rel(var_0[var_4 + var_2 - 1],var_0[var_4 + var_2],(0,-1))
		var_2 = var_2 + 1
	var_0[0].direction = old_dir

def fun_2(var_0,rot):
	old_dir = var_0[0].direction
	var_0[0].direction = rot
	var_6 = []
	borrow(var_0,var_6,len(var_0) // 2,0)
	temp_0 = len(var_6) - 1
	while(temp_0 > 0):
		of_rel(var_6[temp_0],var_6[temp_0 - 1],(1,0))
		temp_0 = temp_0 - 1
	temp_1 = len(var_0) - 1
	while(temp_1 > 0):
		of_rel(var_0[temp_1],var_0[temp_1 - 1],(1,0))
		temp_1 = temp_1 - 1
	of_rel(var_6[0],var_0[0],(0,-1))
	var_0[0].direction = old_dir

steps = []
for _ in range(5):
   steps.append([])
G = SimpleFormationNode.create_formation(5)
runner = PosRunner()

fun_1([G[0],G[1],G[2]],dir_tuple[(-1,0)])
runner.set_and_check_positions(G[0],(0,0))


fun_2([G[3],G[4]],dir_tuple[(-1,-1)])
runner.set_and_check_positions(G[3],(2,0))

for i in range(len(G)):
   steps[i].append(G[i].position)

G = SimpleFormationNode.create_formation(5)
runner = PosRunner()

fun_2([G[0],G[1],G[2]],dir_tuple[(-1,0)])
runner.set_and_check_positions(G[0],(0,0))


fun_1([G[3],G[4]],dir_tuple[(-1,0)])
runner.set_and_check_positions(G[3],(0,2))

for i in range(len(G)):
   steps[i].append(G[i].position)

pg.init()

table, path = get_formation_route(steps)
table = examples.paint.get_example_grid(table)
condition = lambda x: x < len(path[0]) - 1
render = Render(condition, table, path , width=1400, height=800)
render.start()
