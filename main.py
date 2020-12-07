import pygame as pg

from os import sys

import graph as gp
from settings import *


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

    # MUTABLE LOOPS ------------------------------------

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
                if event.key == pg.K_w:
                    print("K_w")
                    self.graph.keyboard_scroll(0, -50)
                if event.key == pg.K_s:
                    print("K_s")
                    self.graph.keyboard_scroll(0, 50)
                if event.key == pg.K_d:
                    print("K_d")
                    self.graph.keyboard_scroll(50, 0)
                if event.key == pg.K_a:
                    print("K_a")
                    self.graph.keyboard_scroll(-50, 0)
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Left Click
                    print("Left Click")
                if event.button == 3:
                    # Right Click
                    print("Right Click")
                if event.button == 4:
                    # Scroll Wheel Up
                    print("Scroll Wheel Up")
                    self.graph.zoom(0.10)
                if event.button == 5:
                    # Scroll Wheel Down
                    print("Scroll Wheel Down")
                    self.graph.zoom(-0.10)

    def init(self):
        # Initialize
        self.text_surface = self.font.render(TEXT, True, TEXTCOLOR, TEXTBACKGROUND)
        self.graph = gp.Graph(
            self.screen,
            FILENAME,
            x_data_type,
            y_data_type,
            color_data_type,
            size_data_type,
        )

    def update(self):
        # Update
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        self.m_pos = pg.mouse.get_pos()
        self.graph.update()

    def draw(self):
        # Draw
        self.screen.fill(pg.color.Color("Light Blue"))
        self.screen.blit(self.text_surface, self.screen.get_rect().center)
        self.graph.draw()
        self.graph.hover_display(self.m_pos)
        pg.display.flip()


# Create game object.
g = Game()
g.new()
g.run()
