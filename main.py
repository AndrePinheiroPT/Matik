from DifferentialViewerlib.math_tools import *
import pygame
from pygame.locals import *

CONFIG = {'screen_width': 800, 'screen_height': 600}
viewer = Viewer(CONFIG)
grafic = GraficScene(viewer, [300, 300], 50, 50)
tools3D = Scense3D(20, 0, 0, viewer)

time = 0

def vect_field(x, y, z):
    r = 0.01 if (x**2 + y**2 + z**2) == 0 else (x**2 + y**2 + z**2)
    return [
        -x/r, 
        -y/r, 
        -z/r]

def scene():
    global time
    tools3D.phi = time
    tools3D.vector((2, 2, 1), (255, 0, 0), (3, 3, 1))
    tools3D.vector((-2, -2, 3), (255, 0, 0))
    tools3D.vector_field(vect_field, [-6, 6, -6, 6,-6, 6], 4)
    tools3D.three_dimensional_space()

    time += 0.01
    
    #tools3D.parametric_surface(cone, [0, 7*tan(pi/10), 0, 2*pi], (255, 255, 255, 255))
viewer.set_slides([scene])
viewer.init()

