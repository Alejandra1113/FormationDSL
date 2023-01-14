import numpy as np
from whcastar import *
from UI import *
import pygame as pg 

def get_formation_route(step_positions : list(list(tuple(int,int)))):
    
    min_x = min([x for k in step_positions for x,y in k ])
    min_y = min([y for k in step_positions for x,y in k ])
    
    
    if min_x < 0 :
        dev = - min_x
        step_positions =[[ (x + dev, y) for x,y in i ] for i in step_positions]
        
    if min_y < 0:
        dev = - min_y
        step_positions =[[ (x, y + dev) for x,y in i ] for i in step_positions]
    
    width = max([x for k in step_positions for x,y in k ])
    heigth = max([y for k in step_positions for x,y in k ])
    
       
    table = ["_" * width]* heigth
    
    current_step = 1 
    path = np.ndarray( shape= len(step_positions), dtype= list())
    rrastar_list = np.ndarray(shape=len(step_positions), dtype=RRAstar)
    ids = [i for i in range(len(step_positions))]
    origin = [i for i in step_positions[0]]
    destiny = [i for i in step_positions[1]]
    
    while current_step < len(step_positions[0]):
    
        paths = whcastar_search(ids, origin, destiny, rrastar_list, heigth, width, 16, None)
        if all( p[-1] == destiny[i] for i, (_, p) in enumerate(paths.items())) :
            current_step += 1
            rrastar_list = np.ndarray(shape=len(step_positions), dtype=RRAstar)
            origin = destiny
            destiny = [i for i in step_positions[current_step]]
            
        for i in range(len(step_positions)) :
            path[i] += paths[i]
            
    return table, path

pg.init()

table, path = get_formation_route()
table = examples.paint.get_example_grid(table)
condition = lambda x: x < len(path[0]) - 1
render = Render(lambda:condition, table, path , width=1400, height=800)
render.start()