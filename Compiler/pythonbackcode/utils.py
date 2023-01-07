from cmath import inf
from enum import Enum


I_DIR = [-1,-1,0,1,1,1,0,-1]
J_DIR = [0,1,1,1,0,-1,-1,-1]

DIRECTIONS = Enum('DIRECTIONS','N NE E SE S SW W NW')
    
def validMove(x, y, max_x, max_y, min_x = 0, min_y = 0): 
    return  x >= min_x and x < max_x and y >= min_y and y < max_y

def norma2(n1, n2):
    x1, y1 = n1
    x2, y2 = n2
    return ((x1 - x2)**2 + (y1 - y2)**2)**(0.5)

def norma_inf(a, b):
    dist = -inf
    for i in range(len(a)):
        dist = max(abs(a[i] - b[i]), dist)
    return dist