import numpy as np
from whcastar import *

def get_formation_route(step_positions : list(list(tuple(int,int))), roadmap):
    current_step = 1 
    path = np.ndarray( shape= len(step_positions), dtype= list())
    rrastar_list = np.ndarray(shape=len(step_positions), dtype=RRAstar)
    ids = [i for i in range(len(step_positions))]
    origin = [i for i in step_positions[0]]
    destiny = [i for i in step_positions[1]]
    
    while current_step < len(step_positions[0]):
    
        paths = whcastar_search(ids, origin, destiny, rrastar_list,roadmap, 16, None)
        
        if all( p[-1] == destiny[i] for i, (_, p) in enumerate(paths.items())) :
            current_step += 1
            rrastar_list = np.ndarray(shape=len(step_positions), dtype=RRAstar)
            origin = destiny
            destiny = [i for i in step_positions[current_step]]
            
        for i in range(len(step_positions)) :
            path[i] += paths[i]
            
    return path

