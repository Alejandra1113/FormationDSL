import sys
import time
import numpy as np
import pygame as pg
from ._map_elements import *

# from entities import Cell
from typing import Iterable
from ._grid import get_grid, get_sprint, transform
# from entities.connector import StateMannager
# from entities.agent import *
# from entities._units import *
# from IA._definitions import *

class Render:
    def __init__(self, condition, map: np.matrix = None, path: list(list((int,int))) = None ,width: int = 800, height: int = 600):
        """
        inicializador de clase, crea un screen de dimensiones (width, height)

        condition -> condición de parada,
        last_state -> estado inicial,
        height -> alto del screen, 
        width -> ancho del screen
        """
        self.first_time = True
        self.path = path
        self.__screen = pg.display.set_mode(size=(width, height))
        self.map = map if map is not None else get_grid(width, height)
        self.index = 0
        self.condition = condition(self.index)
        # self.last_state = StateMannager(self.map, agents)
        
        self.__max_shape_size = max(self.map.shape[1], self.map.shape[0])
        self.__min_screen_size = min(self.__screen.get_size()[0], self.__screen.get_size()[1])

        self.__shape_correction = (self.__max_shape_size - self.map.shape[0]) / 2 , (self.__max_shape_size - self.map.shape[1]) / 2
        self.__screan_correction = (self.__screen.get_size()[0] - self.__min_screen_size) / 2 , (self.__screen.get_size()[1] - self.__min_screen_size) / 2
        
        self.__scale = int(self.__min_screen_size / self.__max_shape_size) + 1, int(self.__min_screen_size / self.__max_shape_size) + 1
        self.update(map.A1)

    # def __iter__(self) -> Iterable[list[Cell]]:
    #     """
    #     iterador que recorre la simulación después de que pygame haya iniciado

    #     return -> Iterable[list[Cell]]
    #     """
    #     while self.condition():
    #         for event in pg.event.get():
    #             if event.type == pg.QUIT:
    #                 sys.exit()
    #         yield self.last_state.exec_round()  # new state

    def start(self, time: int = 1000):
        """
        start se encarga de recorrer la simulación hasta el final después de que pygame haya iniciado

        time -> cantidad de frames por segundo
        """
        clock = pg.time.Clock()
        last =  [Cell(i[self.index]) for i in self.path]
        current = [Cell(i[self.index + 1 ]) for i in self.path]    
        for i in current: 
            last[i].unit = None 
            current[i].unit = i
        current += last
        self.update(current)
        self.first_time = False
        clock.tick(time)

    def update(self, state: list[Cell]):
        """
        update se encarga de actualizar la imagen que se muestra en el screen de pygame

        return -> bool
        """
        for Cell in state:
            sprint = get_sprint(self.__scale, Cell, first_time=self.first_time)
            pos = transform(sprint, self.__scale, Cell.location, self.__shape_correction, self.__screan_correction)
            try:
                self.__screen.blit(sprint, pos)
            except:
                return False
        pg.display.update()
        return True

    def clean(self):
        """
        clean limpia toda la imagen que se muestra en el screen de pygame
        """
        self.__screen.fill((0, 0, 0))
