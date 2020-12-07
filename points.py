import pygame as pg

import csv


class InteractableObject:
    """Class for mouse interactable elements on the screen."""

    def __init__(self, surface, x, y, rect_radius, color=(0, 0, 0)):
        # Center a rect object about the given x, y
        self.surface, self.rect_radius = surface, rect_radius
        self.x, self.y = x, y
        self.xy = (self.x, self.y)
        x, y = x - rect_radius, y - rect_radius
        self.rect = pg.Rect((x, y), (2 * rect_radius, 2 * rect_radius))
        self.rect_radius = rect_radius
        self.color = color

    def __setattr__(self, attr, value):
        """Helper function to set attributes for a dictionary of variable length."""
        super().__setattr__(attr, value)

    def draw(self):
        """Draw circle on given surface."""
        pg.draw.circle(self.surface, self.color, self.xy, self.rect_radius)

    def update_xy(self, x, y):
        self.x, self.y = x, y
        self.xy = (self.x, self.y)
        self.rect.center = self.xy


class Point(InteractableObject):
    """Class for point objects on a graph."""

    def __init__(
        self,
        surface,
        point_dictionary,
        x_data_type,
        y_data_type,
        color_data_type=None,
        size_data_type=None,
    ):
        self.dict = point_dictionary
        self.set_parameters(x_data_type, y_data_type, color_data_type)
        super().__init__(surface, self.x, self.y, self.size)

    def __repr__(self):
        string_list = []
        for key in self.dict:
            string_list.append(f'{key}: {self.dict.get(key)}')
        return string_list

    def set_parameters(self,
        x_data_type,
        y_data_type,
        color_data_type=None,
        size_data_type=None,
    ):
        """Set data types for x, y & color, size if applicable."""
        self.x_data_type, self.y_data_type = x_data_type, y_data_type
        self.color_data_type, self.size_data_type = color_data_type, size_data_type
        self.x, self.y = float(self.dict[self.x_data_type]), float(self.dict[self.y_data_type])
        self.x0, self.y0 = self.x, self.y
        self.xy = (self.x, self.y)
        self.c = float(self.dict[self.color_data_type])
        # set default values
        self.color = (0, 0, 0)
        self.size = 5
        # set custom values if chosen
        if self.size_data_type:
            self.size = int(float(self.dict[self.size_data_type]))

    def update_color(self, color):
        if type(color) == tuple:
            self.color = color
        else:
            print('Color must be (r, g, b)')
            self.color = (0, 0, 0)
