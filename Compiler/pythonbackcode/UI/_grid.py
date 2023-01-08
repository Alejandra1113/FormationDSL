from typing import Union
import numpy as np
from pygame import Rect, Surface, Color, image
from pygame.transform import scale
from ._map_elements import Cell, MountainCell, RiverCell, RoadCell, WallCell, GrassCell
# from entities._units import Fighter, Explorer, Base, Knight, Pikeman
# from entities.connector import StateMannager
class Singleton(type):
    """
    clase usada para que todas las intancias hagan referencia al mismo objeto

    __instance -> unica instancia de la clase
    """
    def __init__(cls, *args, **kwargs):
        cls.__instance = None
        type.__init__(cls, *args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = type.__call__(cls, *args,**kwargs)
        return cls.__instance

default = {
    'MountainCell': Color(255, 196, 70),
    'RiverCell': Color(116, 116, 255),
    'RoadCell': Color(254, 221, 150),
    'WallCell': Color(255, 251, 217),
    'GrassCell': Color(109, 255, 123),
    'Team-1': Color(255, 0, 0),
    'Team-2': Color(0, 0, 255)
}

def paint_empty_Cell(i: int, j: int) -> Cell:
    """
    dada una posición i, j crea una Celda cualquiera

    i y j -> índices o posiciones de la Celda en el grid

    return -> Cell
    """
    return Cell((i, j))

class SprintSurface(Surface):
    """
    clase que representa un sprint de una superficie a pintar
    """
    def __new__(cls, source: Union[Color, Surface], *args, **kwargs) -> None:
        return Surface.__new__(cls, *args, **kwargs)

    def __init_subclass__(cls) -> None:
        return Surface.__init_subclass__()

    def __init__(self, source: Union[Color, Surface], *args, **kwargs) -> None:
        Surface.__init__(self, *args, **kwargs)
        if type(source) is Color:
            self.fill(source)
        elif type(source) is Surface:
            self.blit(source, source.get_rect())
        else:
            raise TypeError("source debe ser Color o Surface")


class MountainSurface(SprintSurface, metaclass=Singleton):
    def __init__(self, source: Union[Color, Surface], *args, **kwargs):
        return SprintSurface.__init__(self, source, *args, **kwargs)


class RiverSurface(SprintSurface, metaclass=Singleton):
    def __init__(self, source: Union[Color, Surface], *args, **kwargs):
        return SprintSurface.__init__(self, source, *args, **kwargs)


class RoadSurface(SprintSurface, metaclass=Singleton):
    def __init__(self, source: Union[Color, Surface], *args, **kwargs):
        return SprintSurface.__init__(self, source, *args, **kwargs)


class WallSurface(SprintSurface, metaclass=Singleton):
    def __init__(self, source: Union[Color, Surface], *args, **kwargs):
        return SprintSurface.__init__(self, source, *args, **kwargs)


class GrassSurface(SprintSurface, metaclass=Singleton):
    def __init__(self, source: Union[Color, Surface], *args, **kwargs):
        return SprintSurface.__init__(self, source, *args, **kwargs)


def get_sprint(newscale: tuple[int, int], Cell: Cell, source: Union[Color, Surface] = None, first_time = False):
    """
    dado un tipo de Celda retorna su representante en sprint

    newscale -> escala del screen,
    Cell -> Celda a convertir en sprint,
    source -> representación de la Celda

    return -> Surface
    """
    source = source if source is not None else default[type(Cell).__name__]
    surface = None
    if (type(Cell) is MountainCell):
        surface = MountainSurface(source, newscale)
    elif (type(Cell) is RiverCell):
        surface = RiverSurface(source, newscale)
    elif (type(Cell) is RoadCell):
        surface = RoadSurface(source, newscale)
    elif (type(Cell) is WallCell):
        surface = WallSurface(source, newscale)
    elif (type(Cell) is GrassCell):
        if first_time:
            surface = GrassSurface(source, newscale)
        else:
            surface = SprintSurface(Color(59, 100, 53), newscale)
    else:
        raise NotImplementedError("Cell type indefinido")

    if not Cell.is_empty:
        surface = SprintSurface(Color(0, 0, 255), newscale)
        # name_color = "Blue"
        # draw = image.load(f".\\contents\\icons\\{type(Cell.unit.unit).__name__}.png").convert_alpha()
        # background_draw = image.load(f".\\contents\\BG\\{name_color}BG{type(Cell.unit.unit).__name__}.png").convert_alpha()
        # x, y = surface.get_size()
        
        # life_background = SprintSurface(Color(150, 0, 0), (x, y*0.10))
        # life = SprintSurface(Color(0, 150, 0), (x * Cell.unit.get_health_points() / Cell.unit.unit.get_health_points, y*0.10))
        
        # surface.blit(scale(background_draw, (x, y)), (0, 0))
        # surface.blit(scale(draw, (x*3/4, y*3/4)), (x/8, y/8))
        # surface.blit(life_background, (0, y*0.90))
        # surface.blit(life, (0, y*0.90))
    return surface

def transform( sprint: Surface, 
               scale: tuple[int, int], 
               location: tuple[int, int], 
               shape_correction: tuple[float, float] = (0, 0),
               scale_correction: tuple[float, float] = (0, 0)
               ) -> Rect:
    """
    traslada un Surface a una posición escalada para su representación en el screen de pygame

    sprint -> superficie a mover,
    scale -> escala del screen,
    location -> posición relativa del sprint,
    shape_correction -> corrección relativa a la posición,
    scale_correction -> corrección relativa al screen

    return -> Rect
    """
    return sprint.get_rect().move((location[1] + shape_correction[1]) * scale[0] + scale_correction[0], 
                                  (location[0] + shape_correction[0]) * scale[1] + scale_correction[1])


def get_grid(width: int, height: int, paint=paint_empty_Cell) -> np.matrix:
    """
    Crea una grilla a partir de las dimensiones que se pasan en el método

    height -> alto del grid, 
    width -> ancho del grid, 
    paint -> función que determina que Celda va en x y

    return -> np.matrix
    """
    return np.matrix([[paint(i, j) for j in range(width)] for i in range(height)], copy=False)
