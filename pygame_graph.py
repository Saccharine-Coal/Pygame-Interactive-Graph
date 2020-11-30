import pygame as pg

import csv

from os import sys

# GENERAL SETTINGS
WIDTH, HEIGHT = 1280, 720
FPS = 60

# FONT
FONTTYPE = 'freesansbold.ttf'
FONTSIZE = 24

# PLOT SETTINGS
AXISLENGTH = 30000
AXISCOLOR = (0, 0, 0)
TICKS = 50
TICKCOLOR = (255, 0, 0)
POINTSIZE = 7

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500, 100)
        self.font = pg.font.Font(FONTTYPE, FONTSIZE)

    # MAIN LOOP ---------------------------------------

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
                self.up = True
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    sys.exit()
                if event.key == pg.K_w:
                    self.graph.center = (self.graph.center[0], self.graph.center[1]+100)
                if event.key == pg.K_s:
                    self.graph.center = (self.graph.center[0], self.graph.center[1]-100)
                if event.key == pg.K_d:
                    self.graph.center = (self.graph.center[0]-100, self.graph.center[1])
                if event.key == pg.K_a:
                    self.graph.center = (self.graph.center[0]+100, self.graph.center[1])
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Left click
                    for point in self.graph.object_points:
                        if point.rect.collidepoint(self.mpos):
                            self.window1 = True
                            text_list = point.__str__(False)
                            self.render_text(text_list)
                if event.button == 3:
                    # Right Click
                    self.m_up = pg.mouse.get_pos()
                if event.button == 4:
                    # Scroll wheel up
                    self.graph.update(0.10)
                if event.button == 5:
                    # Scroll wheel down
                    self.graph.update(-0.10)

            if event.type == pg.MOUSEBUTTONUP:
                if event.button == 3:
                    # Right Click
                    self.m_down = pg.mouse.get_pos()
                    self.drag_scroll()

    def render_text(self, text_list):
        self.text_surfaces = []
        # Renders text lines as font.render can only render 1 line of text.
        for text in text_list:
            self.text_surfaces.append(self.font.render(text, True, (255, 255, 255), (255, 0, 0)))

    def init(self):
        self.up = False
        self.graph = Graph(self.screen, 'PS_2020.11.24_15.36.44(VALUES)')
        self.graph.new(AXISLENGTH, TICKS, "Stellar Mass", "Stellar Radius",
            "Stellar Effective Temperature", POINTSIZE
        )
        # Window
        self.window1 = False
        self.tl = self.screen.get_rect().topleft
        #self.graph.center = self.screen.get_rect().bottomleft

    def update(self):
        # FPS
        self.mpos = pg.mouse.get_pos()
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        if self.up:
            self.graph.update()
            self.up = False

    def draw(self):
        # Draw
        self.screen.fill(pg.color.Color("Light Blue"))
        self.graph.draw()
        # UI
        if self.window1:
            for i, surface in enumerate(self.text_surfaces):
                pos = (self.tl[0], self.tl[1]+(i*surface.get_rect().h))
                self.screen.blit(surface, pos)
        for point in self.graph.object_points:
            if point.rect.collidepoint(self.mpos):
                text = self.font.render(point.dict["Planet Name"], True, (255, 255, 255), (255, 0, 0))
                text_rect = text.get_rect()
                self.screen.blit(text, self.mpos)
                break
        pg.display.flip()

    def drag_scroll(self):
        self.m_rel = (-self.m_up[0]+self.m_down[0], -self.m_up[1]+self.m_down[1])
        self.graph.center = (self.graph.center[0]+self.m_rel[0], self.graph.center[1]+self.m_rel[1])
        self.up = True

class Graph:
    def __init__(self, screen, filename):
        # Initialize properties and functions
        self.screen = screen
        self.center = self.screen.get_rect().center
        self.data_list = csv_to_listed_dict(filename)
        # Font
        self.font = pg.font.Font(FONTTYPE, FONTSIZE)

    # MAIN LOOP ---------------------------------------

    def new(self, axis_length, ticks, x_axis_type, y_axis_type, color_type, size=3):
        # Group init functions
        self.init_axis(axis_length, ticks, x_axis_type, y_axis_type, color_type)
        self.init_objects(size)

    def update(self, axis_change=0):
        # Group update functions
        axis_length = self.axis_length +(self.axis_length * axis_change)
        if axis_length > 0:
            self.init_axis(axis_length, self.ticks, self.data_types[0], self.data_types[1], self.color_type)
            self.init_objects(self.size)

    def draw(self):
        # Group draw functions
        self.screen.fill(pg.color.Color("Light Blue"))
        self.draw_axis()
        self.draw_points(3)
        self.legend()
        # Axis titles
        self.axis_titles()

    # INIT -------------------------------

    def minmax(self, data_type):
        # Sorts list and returns min, max value for inputed data type
        sorted_list = sorted(self.data_list, key=lambda planet: planet.get(data_type))
        min_val, max_val = sorted_list[0], sorted_list[-1]
        return (min_val, max_val)

    def init_axis(self, axis_length, ticks, x_axis_type, y_axis_type, color_type):
        # Initialize axis lengths and tick intervals which is dependent on the data set
        self.axis_length = axis_length
        self.data_types = [x_axis_type, y_axis_type]
        self.ticks_length, self.ticks, self.color_type = axis_length/50, ticks, color_type
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


    def axis_titles(self):
        self.render_text(self.data_types)
        for i, surface in enumerate(self.text_surfaces):
            h, w = surface.get_rect().h, surface.get_rect().w
            if i == 0:
                pos = (self.center[0]+w, self.center[1])
            else:
                pos = (self.center[0]-w, self.center[1]-w)
            self.screen.blit(surface, pos)


    def init_objects(self, size):
        # Listed_dict -> Star objects -> List of Star objects
        self.size = size
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
        pg.draw.lines(self.screen, AXISCOLOR, False, points)
        for i in range(0, self.ticks+1):
            pos = self.tick_interval*i
            # x-axis ticks
            pg.draw.line(self.screen, TICKCOLOR , (self.center[0]+pos, self.center[1]+self.ticks_length),
                (self.center[0]+pos, self.center[1]-self.ticks_length))
            # y-axis ticks
            pg.draw.line(self.screen, TICKCOLOR , (self.center[0]+self.ticks_length, self.center[1]-pos),
                (self.center[0]-self.ticks_length, self.center[1]-pos))

    def draw_points(self, size=2):
        # draw points relative to the axis length (x_data_type, y_data_type)
        for planet in self.object_points:
            c = self.color(planet.dict["Stellar Effective Temperature"])
            pg.draw.circle(self.screen, c, (planet.x, planet.y), planet.rect_radius)

    def legend(self):
        # blits a legend onto the screen
        center = self.screen.get_rect().bottomleft
        text_list = []
        for i in range(0, 3):
            text_list.append(str(round(self.color_scale*(i+1)))+'k')
        text_list.append('Color Legend: Stellar Effective Temperature')
        self.render_text(text_list)
        for i, surface in enumerate(self.text_surfaces):
            h, w = surface.get_rect().h, surface.get_rect().w
            pos = (center[0], center[1]-((i+1)*h))
            self.screen.blit(surface, pos)
            if i == len(self.text_surfaces)-1:
                break
            c = self.color((i+1)*self.color_scale)
            offset = (pos[0]+w, pos[1])
            color_surface = pg.Rect(offset, (w, h))
            pg.draw.rect(self.screen, c, color_surface)

    def render_text(self, text_list):
        # Renders text lines as font.render can only render 1 line of text.
        self.text_surfaces = []
        for text in text_list:
            self.text_surfaces.append(self.font.render(text, True, (255, 255, 255), (255, 0, 0)))

    def color(self, temperature):
        # Color scale function that maps input through (0, 0, 0) -> (255, 255, 255)
        cs = self.color_scale
        i = temperature / (255)
        if temperature >= 2*cs:
            c = (255, 255, i)
        if temperature >= cs:
            c = (255, i, 0)
        else:
            c = (i, 0, 0)
        return c


class InteractableObject:
    """Class for mouse interactable elements on the screen."""
    # Will refactor functions into this class
    def __init__(self, x, y, rect_radius):
        # Center a rect object about the given x, y
        self.x, self.y, self.rect_radius = x, y, rect_radius
        x, y = x-rect_radius, y-rect_radius
        self.rect = pg.Rect((x, y), (2*rect_radius, 2*rect_radius))
        self.rect_radius = rect_radius


class Star(InteractableObject):
    """Class to store star specific methods and properties. Child of InteractableObject."""
    def __init__(self, name, temperature, radius, mass, x, y, rect_radius):
        self.name = name
        self.temperature = temperature
        super().__init__(x, y, rect_radius)
        self.x, self.y = x, y
        self.dict = {"Planet Name": name,
                            "Stellar Effective Temperature": temperature,
                            "Stellar Radius": radius,
                            "Stellar Mass": mass
                        }

    def __repr__(self):
        return self.dict

    def __str__(self, formatted=True):
        string = ''
        if formatted:
            for key in self.dict:
                    string += f'{key}: {self.dict.get(key)} |'
        else:
            string = []
            for key in self.dict:
                string.append(f'{key}: {self.dict.get(key)}')
        return string



def csv_to_listed_dict(filename):
    # list of dict objs with planet name as keys such that
    # [list of planets] = [{"Planet Name": val,
    #                       "Stellar Effective Temperature": val,
    #                       "Stellar Radius": val,
    #                       "Stellar Mass": val
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
