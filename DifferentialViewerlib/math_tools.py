import pygame
import pygame.gfxdraw
import matplotlib.pyplot as plt
from matplotlib import rcParams
import os
import numpy as np
from PIL import Image
from pygame.locals import *
from math import *

CONFIG = {
    'screen_width': 900,
    'screen_height': 600,
    'x_max': 8,
    'y_max': 3,
    'x_min': -1,
    'y_min': -1,
    'x_label': 'Re',
    'y_label': 'Im'
}

CYAN = (55, 55, 55)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
state = [0, 0]
standard_values = []
screen = None
font = None

class Viewer():
    def __init__(self, config):
        self.slide_index = 0
        self.slides = []
        self.mouse_state = []
        self.config = config
        self.time = 0

        path = os.path.dirname(os.path.realpath(__file__)) + '/img'
        for f in os.listdir(path):
            os.remove(os.path.join(path, f))
    
    def set_slides(self, slides):
        self.slides = slides

    def init(self):
        global screen, font, CONFIG
        CONFIG = self.config
        pygame.init()

        screen = pygame.display.set_mode((CONFIG['screen_width'], CONFIG['screen_height']))
        pygame.display.set_caption('DifferentialViewer')

        draw_surface = pygame.Surface((CONFIG['screen_width'], CONFIG['screen_height']))

        pygame.font.init()
        font = pygame.font.SysFont('Arial', 12)

        clock = pygame.time.Clock()
        while True:
            clock.tick(100)
            screen.fill((0, 0, 0))
            self.mouse_state = convert_coords(pygame.mouse.get_pos(), 0)

            self.slides[self.slide_index]()

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        if self.slide_index >= 1:
                            self.slide_index -= 1
                    if event.key == pygame.K_RIGHT:
                        if self.slide_index < len(self.slides) - 1:
                            self.slide_index += 1

            self.time += 0.01
            pygame.display.update()


def update_standard_values():
    global settings
    standard_values = [
        (CONFIG['screen_width']/2) * (state[0]/CONFIG['x_max'] + 1),
        (CONFIG['screen_height']/2) * (1 - state[1]/CONFIG['y_max'])
    ]
    

def convert_coords(coords, standard):
    if standard:
        return [
            CONFIG['screen_width']/(CONFIG['x_max'] - CONFIG['x_min']) * (coords[0] - CONFIG['x_min']),
            CONFIG['screen_height']/(CONFIG['y_max'] - CONFIG['y_min']) * (CONFIG['y_max'] - coords[1])
        ]
    else:
        return [
            coords[0] * (CONFIG['x_max'] - CONFIG['x_min']) / CONFIG['screen_width'] + CONFIG['x_min'],
            -coords[1] * (CONFIG['y_max'] - CONFIG['y_min']) / CONFIG['screen_height'] + CONFIG['x_max']
        ]


def cartesian_plane():
    x_value = round(CONFIG['x_min'])
    y_value = round(CONFIG['y_min'])

    unit_lenght_x = round(convert_coords((0, 0), 1)[0] - convert_coords((-1, 0), 1)[0])
    unit_lenght_y = convert_coords((0, 0), 1)[1] - convert_coords((0, 1), 1)[1]

    for x in range(round(convert_coords((round(CONFIG['x_min']), 0),1)[0]), CONFIG['screen_width'], unit_lenght_x):
        pygame.draw.line(screen, CYAN, (x, 0), (x, CONFIG['screen_height']), 1)
        screen.blit(font.render(f'{x_value:.1f}', False, WHITE), (x+2, convert_coords((0, 0), 1)[1]))
        x_value += 1
        
    y = round(convert_coords((0, round(CONFIG['y_min'])), 1)[1])
    while y >= 0:
        pygame.draw.line(screen, CYAN, (0, y), (CONFIG['screen_width'], y), 1)
        if y_value != 0:
            screen.blit(font.render(f'{y_value:.1f}', False, WHITE), (convert_coords((0, 0), 1)[0]+3, y-12))
        y_value += 1
        y -= unit_lenght_y

    screen.blit(font.render(f'{CONFIG["x_label"]}', False, WHITE), (CONFIG['screen_width'] - 10, convert_coords((0, 0), 1)[1]))
    screen.blit(font.render(f'{CONFIG["y_label"]}', False, WHITE), (convert_coords((0, 0), 1)[0] + 5 , 0))

    pygame.draw.line(screen, WHITE, (convert_coords((0, 0), 1)[0], 0), (convert_coords((0, 0), 1)[0], CONFIG['screen_height']), 1)
    pygame.draw.line(screen, WHITE, (0, convert_coords((0, 0), 1)[1]), (CONFIG['screen_width'], convert_coords((0, 0), 1)[1]), 1)


def linear_transformation(matrix):
    alpha = CONFIG['screen_width']/ (0.001 if matrix[0][0] == 0 else matrix[0][0])
    beta = CONFIG['screen_height']/ (0.001 if matrix[1][1] == 0 else matrix[1][1])

    n = round(CONFIG['x_min'])
    while n <= CONFIG['x_max']:
        pygame.draw.line(screen, YELLOW, 
        convert_coords((-beta*matrix[0][1] + n*matrix[0][0], -beta*matrix[1][1] + n*matrix[1][0]), 1), 
        convert_coords((beta*matrix[0][1] + n*matrix[0][0], beta*matrix[1][1] + n*matrix[1][0]), 1))
        n += 1

    n = round(CONFIG['y_min']) 
    while n <= CONFIG['y_max']:
        pygame.draw.line(screen, YELLOW, 
        convert_coords((-alpha*matrix[0][0] + n*matrix[0][1], -alpha*matrix[1][0] + n*matrix[1][1]), 1), 
        convert_coords((alpha*matrix[0][0] + n*matrix[0][1], alpha*matrix[1][0] + n*matrix[1][1]), 1))
        n += 1
    

def vector(dx, dy, color, origin_point):
    vector_length = 0.001 if sqrt(dx**2 + dy**2) == 0 else sqrt(dx**2 + dy**2)

    v_stick1 = (
        0.15*(dy/vector_length - dx/vector_length),
        -0.15*(dx/vector_length + dy/vector_length)
    ) 

    v_stick2 = (
        -0.15*(dy/vector_length + dx/vector_length),
        0.15*(dx/vector_length - dy/vector_length)
    )

    x_component = origin_point[0] + dx
    y_component = origin_point[1] + dy

    pygame.draw.line(screen, color, convert_coords((origin_point[0], origin_point[1]), 1), convert_coords((x_component, y_component), 1), 3)
    pygame.draw.line(screen, color, convert_coords((x_component, y_component), 1), convert_coords((x_component + v_stick1[0], y_component + v_stick1[1]), 1), 3)
    pygame.draw.line(screen, color, convert_coords((x_component, y_component), 1), convert_coords((x_component + v_stick2[0], y_component + v_stick2[1]), 1), 3)


def real_functions(function, xd_min, xd_max, dx=0.01, color=(255, 255, 0)):
    x = xd_min
    function_points = []
    while xd_min <= x <= xd_max:
        x += dx
        y = function(x)

        function_points.append(convert_coords((x, y), 1))

    if len(function_points) >= 2:
        pygame.draw.lines(screen, color, False, function_points, 3)


def complex_functions(func, domain_func, t_min, t_max, dt=0.01, color=(255, 255, 0)):

    complex_function_points = []
    t = t_min 
    while t_min <= t <= t_max:
        t += dt

        z = []
        for i in range(0, 2):
            z.append(func(*domain_func(t))[i])

        function_points.append(convert_coords((z[0], z[1]), 1))

    if len(complex_function_points) >= 2:
        pygame.draw.lines(screen, color, False, complex_function_points, 2)


def vector_field(func, space, scalar, color=(0, 255, 0)):

    for x in range(-CONFIG['x_max'], CONFIG['x_max']+ 1, space):
        for y in range(-CONFIG['y_max'], CONFIG['y_max']+ 1, space):
            vector_length = 0.001 if sqrt(func(x, y)[0]**2 + func(x, y)[1]**2) == 0 else sqrt(func(x, y)[0]**2 + func(x, y)[1]**2)

            v_stick1 = (
                0.15*(func(x, y)[1]/vector_length - func(x, y)[0]/vector_length),
                -0.15*(func(x, y)[0]/vector_length + func(x, y)[1]/vector_length)
            ) 

            v_stick2 = (
                -0.15*(func(x, y)[1]/vector_length + func(x, y)[0]/vector_length),
                0.15*(func(x, y)[0]/vector_length - func(x, y)[1]/vector_length)
            )

            output_fx = x + func(x, y)[0] * scalar
            output_fy = y + func(x, y)[1] * scalar

            pygame.draw.line(screen, color, convert_coords((x, y), 1), convert_coords((output_fx, output_fy), 1), 2)
            pygame.draw.line(screen, color, convert_coords((output_fx, output_fy), 1), convert_coords((output_fx + v_stick1[0], output_fy + v_stick1[1]), 1), 2)
            pygame.draw.line(screen, color, convert_coords((output_fx, output_fy), 1), convert_coords((output_fx + v_stick2[0], output_fy + v_stick2[1]), 1), 2)


def derivative_line(func, x, range_line, h=0.0001, color=(230, 0, 85)):
    
    derivative = 0

    derivative = (func(x+h) - func(x)) / h  # slope
    b = func(x) - derivative*x

    x_range = range_line/(1+derivative**2)**0.5
    pygame.draw.line(screen, color, 
    convert_coords((x - x_range, (x - x_range)*derivative + b), 1), 
    convert_coords((x + x_range, (x + x_range)*derivative + b), 1), 3)
        
    return derivative


def riemann_rectangles(func, x_min, x_max, n, color_init=[131, 47, 0, 200], color_end=[231, 242, 0, 200]):
    reason_x = (convert_coords((CONFIG['x_max'], CONFIG['y_max']), 1)[0] - convert_coords((0, 0), 1)[0]) / CONFIG['x_max']
    reason_y = (convert_coords((CONFIG['x_max'], CONFIG['y_max']), 1)[1] - convert_coords((0, 0), 1)[1]) / CONFIG['y_max']

    color = [0, 0, 0, 0]
    d_color = [0, 0, 0, 0]
    for k in range(0, 4):
        d_color[k] = (color_end[k] - color_init[k]) / n

    dx = (x_max - x_min) / n
    total_sum = 0
    for i in range(0, n):
        for k in range(0, 4):
            color[k] = color_init[k] + d_color[k]*i

        x = x_min + i*dx
        dy = func(x)

        total_sum += dy*dx

        pygame.gfxdraw.box(screen, pygame.Rect(convert_coords((x, func(x)), 1), (dx * reason_x, -dy * reason_y + 1)), color)

    return total_sum


def limit_aproximation(func, h, delta, color=(255, 255, 0)):
    real_functions(func, h - delta, h + delta)
    standard_limit = convert_coords((h, func(h)), 1)
    for i in range(0, 2):
        standard_limit[i] = round(standard_limit[i])
    pygame.draw.circle(screen, color, standard_limit, 4)

    return func(h)


def latex_text(equation, name_file, position=None, scaler=0.15, update=False):
    my_path = os.path.dirname(os.path.realpath(__file__))
    rcParams['text.usetex'] = True
    rcParams['text.latex.preamble'] = r'\usepackage{{amsmath}}'

    if not os.path.isfile(my_path + '/img/{}.png'.format(name_file)):
        eq = equation.strip('$').replace(' ', '')

        fig = plt.figure()
        ax = plt.axes([0,0,1,1])
        r = fig.canvas.get_renderer()

        t = ax.text(0.5, 0.5, '${}$'.format(eq), fontsize=200, 
        horizontalalignment='center', verticalalignment='center', color='white')

        bb = t.get_window_extent(renderer=r)
        w,h = bb.width/fig.dpi, np.ceil(bb.height/fig.dpi)
        fig.set_size_inches((0.1+w, 0.1+h))

        plt.xlim([0,1])
        plt.ylim([0,1])
        ax.grid(False)
        ax.set_axis_off()

        plt.savefig(my_path + '/img/{}.png'.format(name_file), transparent=True)
    else:
        formula = pygame.image.load(my_path + '/img/{}.png'.format(name_file))

        formula_img = Image.open(my_path + '/img/{}.png'.format(name_file))
        width, height = formula_img.size

        formula_scaled = pygame.transform.scale(formula, (round(width*scaler), round(height*scaler)))
        screen.blit(formula_scaled, convert_coords(position, 1))

# TODO
def differential(x, y, z):
        dt = 0.01
        #dx = (10 * (y - x)) * dt
        #dy = (x * (24 - z) - y) * dt
        #dz = (x * y - 8/3 * z) * dt

        dx = (-y - 0.1 * x) * dt
        dy = (x - 0.4 * y) * dt
        dz = 0

        state[0] += dx
        state[1] += dy
        state[2] += dz
        update_standard_values()
        points.append((standard_values[0], standard_values[1])) 


def complex_conjectures(a, b, sum_length):
    global points
    for n in range(1, sum_length+1):
        if -(x_max + 1000) < state[0] < x_max + 1000 and -(y_max + 1000) < state[1] < y_max + 1000:
            prev_z0 = state[0]**2 - state[1]**2 + a
            prev_z1 = 2 * state[0] * state[1] + b 
            
            state[0] += prev_z0
            state[1] += prev_z1
            
            update_standard_values()
            points.append((standard_values[0], standard_values[1]))

    pygame.draw.circle(screen, (255, 255, 255), (standard_values[0], standard_values[1]), 3)
    
    state = [0, 0, 0]
    update_standard_values()
    points = [(standard_values[0], standard_values[1])]