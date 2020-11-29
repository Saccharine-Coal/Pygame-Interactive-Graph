import pygame as pg

import csv

from os import sys

# Settings
WIDTH, HEIGHT = 1280, 720
FPS = 60

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500, 100)
        self.font = pg.font.Font('freesansbold.ttf', 24)

    def new(self):
        self.init()

    def run(self):
        """Runs pygame."""
        while True:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def events(self):
        """Catch all events here."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    sys.exit()

    def init(self):
        self.graph = Graph(self.screen, 'PS_2020.11.24_15.36.44(VALUES)')
        self.graph.new(30000, 50, "Stellar Mass", "Stellar Radius", "Stellar Effective Temperature", 7)

    def update(self):
        # FPS
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))

    def draw(self):
        # Draw
        self.screen.fill(pg.color.Color("Light Blue"))
        self.graph.draw_axis()
        self.graph.draw_points(3)
        # UI
        mpos = pg.mouse.get_pos()
        for point in self.graph.object_points:
            if point.rect.collidepoint(mpos):
                text = self.font.render(point.dict["Planet Name"], True, (255, 255, 255), (255, 0, 0))
                text_rect = text.get_rect()
                self.screen.blit(text, mpos)
                break
        pg.display.flip()

class Graph:
    def __init__(self, screen, filename):
        # Initialize properties and functions
        self.screen = screen
        self.center = self.screen.get_rect().center
        self.data_list = csv_to_listed_dict(filename)

    def new(self, axis_length, ticks, x_axis_type, y_axis_type, color_type, size=3):
        self.init_axis(axis_length, ticks, x_axis_type, y_axis_type, color_type)
        self.init_objects(size)

    def update(self):
        # Group update functions
        foo = 0

    def draw(self):
        # Group draw functions
        foo = 0

    # INIT -------------------------------

    def init_surface(self, surface_dim):
        self.surface = pg.Surface((surface_dim, surface_dim))

    def minmax(self, data_type):
        # Sorts lists of planets based on a data type and returns min, and max values for the list
        sorted_list = sorted(self.data_list, key=lambda planet: planet.get(data_type))
        min_val, max_val = sorted_list[0], sorted_list[-1]
        return (min_val, max_val)

    def init_axis(self, axis_length, ticks, x_axis_type, y_axis_type, color_type):
        # Initialize axis lengths and tick intervals which is dependent on the data set
        self.data_types = [x_axis_type, y_axis_type]
        self.ticks_length, self.ticks = axis_length/50, ticks
        self.tick_interval = int(axis_length/ticks)
        self.x_axis = (self.center[0]+axis_length, self.center[1])
        self.y_axis = (self.center[0], self.center[1]-axis_length)
        # Scales
        x_max = self.minmax(x_axis_type)[1][x_axis_type]
        y_max = self.minmax(y_axis_type)[1][y_axis_type]
        color_max = self.minmax(color_type)[1][color_type]
        self.x_scale = axis_length/x_max
        self.y_scale = axis_length/y_max
        self.color_scale = color_max /3

    def init_objects(self, size):
        self.object_points = []
        for planet in self.data_list:
            pos = (int(planet[self.data_types[0]]*self.x_scale), -int(planet[self.data_types[1]]*self.y_scale))
            shifted_pos = (pos[0]+self.center[0], pos[1]+self.center[1])
            s = Star(planet["Planet Name"], planet["Stellar Effective Temperature"],
                planet["Stellar Radius"], planet["Stellar Mass"],
                shifted_pos[0], shifted_pos[1], size
            )
            self.object_points.append(s)


    def draw_axis(self):
        points = [self.y_axis, self.center, self.x_axis]
        pg.draw.lines(self.screen, (0, 0, 0), False, points)
        for i in range(0, self.ticks+1):
            pos = self.tick_interval*i
            # x-axis
            pg.draw.line(self.screen, (255, 0, 0), (self.center[0]+pos, self.center[1]+self.ticks_length),
                (self.center[0]+pos, self.center[1]-self.ticks_length))
            # y-axis
            pg.draw.line(self.screen, (255, 0, 0), (self.center[0]+self.ticks_length, self.center[1]-pos),
                (self.center[0]-self.ticks_length, self.center[1]-pos))

    def draw_points(self, size=2):
        # draw points relative to the axis length (x_data_type, y_data_type)
        for planet in self.object_points:
            c = self.color(planet.dict["Stellar Effective Temperature"])
            pg.draw.circle(self.screen, c, (planet.x, planet.y), planet.rect_radius)

    def color(self, temperature):
        cs = self.color_scale
        i = temperature / (255)
        if temperature >= 2*cs:
            c = (255, 255, i)
        elif temperature >= cs:
            c = (255, i, 0)
        else:
            c = (i, 0, 0)
        return c


class InteractableObject:
    """Class for mouse interactable elements on the screen."""
    def __init__(self, x, y, rect_radius):
        # Center a rect object about the given x, y
        self.x, self.y, self.rect_radius = x, y, rect_radius
        x, y = x-rect_radius, y-rect_radius
        self.rect = pg.Rect((x, y), (2*rect_radius, 2*rect_radius))
        self.rect_radius = rect_radius


class Star(InteractableObject):
    """Class to store star specific methods and properties. Child of MassObject."""
    def __init__(self, name, temperature, radius, mass, x, y, rect_radius):
        self.name = name
        self.temperature = temperature
        super().__init__(x, y, rect_radius)
        self.dict = {"Planet Name": name,
                            "Stellar Effective Temperature": temperature,
                            "Stellar Radius": radius,
                            "Stellar Mass": mass
                        }

#     def __repr__(self):
#         return self.dict

    def __str__(self):
        string = ''
        for key in self.dict:
            string += f'{key}: {self.dict.get(key)} |'
        return string



def csv_to_listed_dict(filename):
    # list of dict objs with planet name as keys such that
    # [list of planets] = [{"Planet Name":
    #                       {"Stellar Effective Temperature": val},
    #                       {"Stellar Radius": val},
    #                       {"Stellar Mass": val}
    #                     }]
    with open(f'{filename}.csv') as csvfile:
        csv_dict_reader = csv.DictReader(csvfile, delimiter=',')
        csv_list = []
        line_count = 0
        for row in csv_dict_reader:
            planet_dict = {"Planet Name": row["pl_name"],
                            "Stellar Effective Temperature": float(row["st_teff"]),
                            "Stellar Radius": float(row["st_rad"]),
                            "Stellar Mass": float(row["st_mass"])
                        }
            csv_list.append(planet_dict)
        return csv_list

# Create graph object.
g = Game()
g.new()
g.run()
