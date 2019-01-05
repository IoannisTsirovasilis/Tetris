import pygame as pg

class GraphicsManager:
    screen = None

    def __init__(self, width, height):
        if self.screen is None:
            self.SIZE = (width, height)
            self.WIDTH = width
            self.HEIGHT = height
            self.screen = pg.display.set_mode(self.SIZE)
            self.FONT = "Comic Sans Ms"
            self.BLACK = [0, 0, 0]
            self.GREY = [77, 77, 77]
            self.PURPLE = [255, 0, 255]
            self.BLUE = [128, 191, 255]
            self.ORANGE = [255, 165, 0]
            self.YELLOW = [204, 204, 0]
            self.CYAN = [0, 255, 255]
            self.RED = [255, 0, 0]
            self.GREEN = [0, 153, 51]
            self.WHITE = [255, 255, 255]

    def draw_rect(self, width, height, pos_x, pos_y, color):
        rect = pg.Rect((pos_x, pos_y), (width, height))
        pg.draw.rect(self.screen, color, rect)

    def draw_text(self, font, size, text, color, pos_x, pos_y):
        font = pg.font.SysFont(font, size)
        text = font.render(text, False, color)
        self.screen.blit(text, (pos_x, pos_y))
