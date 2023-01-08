import numpy as np
from whcastar import *
from UI import *
import pygame as pg 

step = [ [(-1,0),(2,3),(-2,1)], [(0,-3),(3,5),(5,2) ], [(2,5),(3,4),(0,0)]]

def get_formation_route(step_positions : list(list((int,int)))):
    
    min_x = min([x for k in step_positions for x,y in k ])
    min_y = min([y for k in step_positions for x,y in k ])
    
    
    if min_x < 0 :
        dev = - min_x
        step_positions =[[ (x + dev, y) for x,y in i ] for i in step_positions]
        
    if min_y < 0:
        dev = - min_y
        step_positions =[[ (x, y + dev) for x,y in i ] for i in step_positions]
    
    heigth = max([x for k in step_positions for x,y in k ]) +1 
    width = max([y for k in step_positions for x,y in k ]) +1
    
       
    table = ["_" * width]* heigth
    
    current_step = 1 
    path = [[] for i in step_positions]
    rrastar_list = np.ndarray(shape=len(step_positions), dtype=RRAstar)
    ids = [i for i in range(len(step_positions))]
    origin = [i for i in step_positions[0]]
    destiny = [i for i in step_positions[1]]
    
    while current_step < len(step_positions[0]):
    
        paths = whcastar_search(ids, origin, destiny, rrastar_list, heigth, width, 16, None)
        if all([p[-1][0] == destiny[i] for i, p in paths.items()]) :
            current_step += 1
            if current_step < len(step_positions[0]):               
                rrastar_list = np.ndarray(shape=len(step_positions), dtype=RRAstar)
                origin = destiny
                destiny = [i[current_step] for i in step_positions]
            
        for i in range(len(step_positions)) :
            path[i] += paths[i]
            
    return table, path

pg.init()

table, path = get_formation_route(step)
table = examples.paint.get_example_grid(table)
condition = lambda x: x < len(path[0])
render = Render(lambda x :condition(x), table, path , width=1400, height=800)
render.start()