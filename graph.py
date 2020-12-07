import pygame as pg

import csv

import points as ps
from settings import *


class Graph:
    def __init__(self, surface, filename, x_data_type, y_data_type, color_data_type, size_data_type):
        # Initialize properties and functions
        self.surface = surface
        self.filename = filename
        self.origin = self.surface.get_rect().bottomleft
        self.origin = self.origin[0]+50, self.origin[1]-50
        # Data types for graph which will be csv row names ie 'pl_name', 'st_masse'
        self.x_data_type, self.y_data_type = x_data_type, y_data_type
        self.color_data_type, self.size_data_type = color_data_type, size_data_type
        # Font
        self.font = pg.font.Font(FONTTYPE, FONTSIZE)
        # New
        self.new()

    # MAIN LOOP ---------------------------------------

    def new(self):
        # Group init functions
        self.init_points(4, self.filename)
        self.init_axis(AXISLENGTH, TICKS)
        self.init_legend()

    def update(self):
        self.update_axis()
        self.update_points()

    def draw(self):
        # Group draw functions
        self.surface.fill(pg.color.Color("Light Blue"))
        self.draw_points()
        self.draw_axis()
        self.draw_legend()

    # INIT -------------------------------

    def init_axis(self, axis_length, ticks):
        # Initialize axis lengths and tick intervals which is dependent on the data set
        self.axis_length = axis_length
        self.ticks_length, self.ticks = axis_length/50, ticks
        self.tick_interval = int(axis_length/ticks)
        self.x_axis = (self.origin[0]+axis_length, self.origin[1])
        self.y_axis = (self.origin[0], self.origin[1]-axis_length)
        # Scales
        self.x_max = float(getattr(self.minmax(self.points, 'x')[1], 'x'))
        self.y_max = float(getattr(self.minmax(self.points, 'y')[1], 'y'))
        self.x_scale = axis_length/self.x_max
        self.y_scale = axis_length/self.y_max
        # set proper point positions
        self.update_points()
        for point in self.points:
            c = point.c
            color = self.color_scale(c)
            point.update_color(color)

    def init_points(self, size, filename):
        lod = self.load_csv(filename)
        self.points = []
        for i, dictionary in enumerate(lod):
            for key in list(dictionary):
                point_dict = dictionary[key]
                point = ps.Point(
                    self.surface,
                    point_dict,
                    self.x_data_type, self.y_data_type,
                    self.color_data_type,
                    self.size_data_type
                )
                self.points.append(point)

    # UPDATE ----------------------------------------------------

    def update_points(self):
        for point in self.points:
            x, y = point.x0, point.y0
            # scale relative to axis length
            x, y = int(self.x_scale*x), -int(self.y_scale*y)
            # shift points to origin
            x, y = self.origin[0]+x, self.origin[1]+y
            point.update_xy(x, y)

    def update_axis(self):
        axis_length = self.axis_length
        self.ticks_length = axis_length/50
        self.tick_interval = int(axis_length/self.ticks)
        self.x_axis = (self.origin[0]+axis_length, self.origin[1])
        self.y_axis = (self.origin[0], self.origin[1]-axis_length)
        self.x_scale = axis_length/self.x_max
        self.y_scale = axis_length/self.y_max

    # DRAW --------------------------------------------------------

    def draw_points(self):
        # draw points relative to the axis length (x_data_type, y_data_type)
        for point in self.points:
            x, y = point.x, point.y
            c, r = point.color, point.size
            pg.draw.circle(self.surface, c, (x, y), r)

    def draw_axis(self):
        points = [self.y_axis, self.origin, self.x_axis]
        pg.draw.lines(self.surface, AXISCOLOR, False, points)
        for i in range(0, self.ticks+1):
            pos = self.tick_interval*i
            # x-axis ticks
            pg.draw.line(self.surface, TICKCOLOR , (self.origin[0]+pos, self.origin[1]+self.ticks_length),
                (self.origin[0]+pos, self.origin[1]-self.ticks_length))
            # y-axis ticks
            pg.draw.line(self.surface, TICKCOLOR , (self.origin[0]+self.ticks_length, self.origin[1]-pos),
                (self.origin[0]-self.ticks_length, self.origin[1]-pos))

    def color_scale(self, value):
        # Color scale function that maps input through (255, 0, 0) -> (0, 0, 255)
        # http://www.csb.yale.edu/userguides/graphics/vmd/ug/node76.html
        data_type = 'c'
        min_val_obj, max_val_obj = self.minmax(self.points, data_type)[:]
        min_val, max_val = getattr(min_val_obj, data_type), getattr(max_val_obj, data_type)
        self.c_minmax = (min_val, max_val)
        norm_value = self.normalize(min_val, max_val, value)
        if  norm_value >= 0.5:
            # 0.75 -> 1.0
            if norm_value >= 0.75:
                R = 0
                G = 255 - int(255 * (norm_value/1))
                B = int(255 * (norm_value/1))
            # 0.5 -> 0.75
            else:
                R = 0
                G = 255 - int(255 * (norm_value/1))
                B = int(255 * (norm_value/1))

        else:
            # if val=0 R=255, if val=midpoint R=0 G=255
            # 0.25 -> 0.5
            if norm_value >= 0.25:
                R = 255 - int(255 * (norm_value/0.5))
                G = int(255 * (norm_value/0.5))
                B = 0
            # 0 -> 0.25
            else:
                R = 255 - int(255 * (norm_value/0.5))
                G = int(255 * (norm_value/0.5))
                B = 0
        c = (R, G, B)
        return c

    # SCREEN FUNCTIONS ----------------------------------

    def zoom(self, percent_zoom):
        self.axis_length = self.axis_length +(self.axis_length * percent_zoom)

    def drag_scroll(self, m_rel):
        self.origin = (self.origin[0]+m_rel[0], self.origin[1]+m_rel[1])

    def keyboard_scroll(self, x, y):
        self.origin = (self.origin[0]+x, self.origin[1]+y)

    def hover_display(self, m_pos):
        """Creates a display at the mouse position if the mouse is over a point."""
        for point in self.points:
            if point.rect.collidepoint(m_pos):
                text_list = point.__repr__()
                text_surfaces = self.render_text(text_list)
                self.blit_text(self.surface, text_surfaces, m_pos)
                break

    def init_legend(self):
        """Returns surface objects to draw later."""
        min_val, max_val = self.c_minmax[:]
        text_list = [
            str(min_val),
            str(0.125*max_val),
            str(0.25*max_val),
            str(0.375*max_val),
            str(0.5*max_val),
            str(0.625*max_val),
            str(0.75*max_val),
            str(0.875*max_val),
            str(max_val),
            f'Color Legend: {self.color_data_type}'
        ]
        self.legend_surfaces = self.render_text(text_list)
        self.legend_colors = []
        for i in range(len(self.legend_surfaces)):
            if i == len(self.legend_surfaces)-1:
                break
            value = i/8*max_val
            # filter out value = 0
            if value == 0:
                c = (0, 0, 0)
            else:
                c = self.color_scale(value)
            self.legend_colors.append(c)

    def draw_legend(self):
        """Draw legend surfaces."""
        min_val, max_val = self.c_minmax[:]
        center = self.surface.get_rect().bottomleft
        for i, surface in enumerate(self.legend_surfaces):
            # blit text surface
            h, w = surface.get_rect().h, surface.get_rect().w
            pos = (center[0], center[1]-((i+1)*h))
            self.surface.blit(surface, pos)
            if i == len(self.legend_surfaces)-1:
                break
            # color rects
            offset = (pos[0]+w, pos[1])
            color_surface = pg.Rect(offset, (w, h))
            c = self.legend_colors[i]
            pg.draw.rect(self.surface, c, color_surface)

    # TEXT FUNCTIONS ----------------------------------

    def render_text(self, text_list):
        # Renders text lines as font.render can only render 1 line of text.
        text_surfaces = []
        for text in text_list:
            text_surfaces.append(self.font.render(text, True, (255, 255, 255), (255, 0, 0)))
        return text_surfaces

    def blit_text(self, target_surface, text_surfaces, pos, direction=True):
        # direction = True = descending, direction = False = Ascending
        for i, text_surface in enumerate(text_surfaces):
            h, w = text_surface.get_rect().h, text_surface.get_rect().w
            if direction:
                offset = (pos[0], pos[1]+(i*h))
            else:
                offset = (pos[0], pos[1]-(i*h))
            target_surface.blit(text_surface, offset)

    # HELPER FUNCTIONS --------------------------------

    @staticmethod
    def load_csv(filename):
        """Load system data from csv file."""
        with open(f'{filename}.csv') as csvfile:
            csv_dict_reader = csv.DictReader(csvfile, delimiter=',')
            list_of_dictionaries = []
            for row in csv_dict_reader:
                sub_dict = {}
                # key, dictionary, list_dictionaries = k, d, lod
                val_to_chk = row['pl_name']
                lod = list_of_dictionaries
                # filters out any duplicate host star names. not efficient but works for now
                """ Causes longer boot up time, since we are iterating through the growing list everytime."""
                if not any(val_to_chk in d for d in lod):
                    system_dictionary = {row['pl_name']: sub_dict}
                    for key in row:
                        sub_dict[key] = row[key]
                    list_of_dictionaries.append(system_dictionary)
            return list_of_dictionaries

    @staticmethod
    def minmax(list_, data_type):
        """Returns a tuple of objects of the min, max values."""
        # Sorts list and returns min, max value for inputed data type
        # Use this function to scale data relative to the axis length
        sorted_list = sorted(list_, key=lambda point: float(getattr(point, data_type)))
        min_val, max_val = sorted_list[0], sorted_list[-1]
        return (min_val, max_val)

    @classmethod
    def normalize(cls, min_val, max_val, value):
        # https://stats.stackexchange.com/questions/70801/how-to-normalize-data-to-0-1-range
        # zi = (xi - min(x))/(max(x)-min(x))
        num, denom = value-min_val, max_val-min_val
        return num/denom

    @staticmethod
    def get(target_object, attribute):
        # Get attribute from the target object using the specified attribute
        # specific to csv as values exist as strings
        return float(getattr(target_object,f'{attribute}'))


