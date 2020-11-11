import pygame as pg
import DQN_40_Actions.GameControllerIdea as GameController

FONT = "Comic Sans Ms"
BLACK = [0, 0, 0]
GREY = [77, 77, 77]
PURPLE = [255, 0, 255]
BLUE = [128, 191, 255]
ORANGE = [255, 165, 0]
YELLOW = [204, 204, 0]
CYAN = [0, 255, 255]
RED = [255, 0, 0]
GREEN = [0, 153, 51]
WHITE = [255, 255, 255]
PIECES_COLORS = [GREY, CYAN, BLUE, ORANGE, YELLOW, GREEN, PURPLE, GREY]


class GraphicsManager:
    def __init__(self, width, height):
        self.size = (width, height)
        self.width = width
        self.height = height
        self.screen = pg.display.set_mode(self.size)

    def draw_rect(self, width, height, pos_x, pos_y, color):
        rect = pg.Rect((pos_x, pos_y), (width, height))
        pg.draw.rect(self.screen, color, rect)

    def draw_text(self, font, size, text, color, pos_x, pos_y):
        font = pg.font.SysFont(font, size)
        text = font.render(text, False, color)
        self.screen.blit(text, (pos_x, pos_y))

    def __draw_game_board(self):
        # Pieces are 35x35 and between its block there is a 2-pixels black padding
        for i in range(GameController.BOARD_HEIGHT):
            for j in range(GameController.BOARD_WIDTH):
                if i in [0, 1]:
                    self.draw_rect(35, 35, 2 * (j + 12) + 35 * (j + 11), 2 * (i + 3) + 35 * (i + 2), BLACK)
                else:
                    self.draw_rect(35, 35, 2 * (j + 12) + 35 * (j + 11), 2 * (i + 3) + 35 * (i + 2),
                                   GameController.get_piece_color(GameController.BOARD[i][j]))

    def __draw_next_piece_board(self, next_piece, is_I):
        color = GameController.get_piece_color(next_piece[next_piece > 0][0])
        for i in range(5):
            for j in range(5):
                self.draw_rect(35, 35, 35 * (j + 24), 35 * (i + 13), GREY)
        self.draw_text(FONT, 30, "NEXT", WHITE, self.width - 298, 455)
        for i in range(next_piece.shape[0]):
            for j in range(next_piece.shape[1]):
                tmp_color = color if next_piece[i][j] > 0 else GREY
                if is_I:
                    self.draw_rect(30, 30, 2 * (j + 27) + 30 * (j + 27), 2 * (i + 18) + 30 * (i + 17), tmp_color)
                else:
                    self.draw_rect(30, 30, 2 * (j + 28) + 30 * (j + 28), 2 * (i + 18) + 30 * (i + 17), tmp_color)

    def __draw_score_board(self, score):
        self.draw_rect(175, 100, self.width - 346, 300, GREY)
        self.draw_text(FONT, 30, "SCORE", WHITE, self.width - 311, 305)
        self.draw_text(FONT, 30, str.zfill(str(score), 6), WHITE, self.width - 311, 355)

    def __draw_lines_board(self, lines):
        self.draw_rect(175, 100, self.width - 346, 150, GREY)
        self.draw_text(FONT, 30, "LINES", WHITE, self.width - 311, 155)
        self.draw_text(FONT, 30, str.zfill(str(lines), 3), WHITE, self.width - 291, 205)

    def __draw_level_board(self, level):
        self.draw_rect(175, 60, self.width - 346, 650, GREY)
        self.draw_text(FONT, 30, "LEVEL " + str(level).zfill(2), WHITE, self.width - 324, 655)

    def draw_game_ui(self, gc: GameController, next_piece, is_I):
        self.__draw_game_board()
        self.__draw_next_piece_board(next_piece, is_I)
        self.__draw_score_board(gc.score)
        self.__draw_lines_board(gc.lines)
        self.__draw_level_board(gc.level)
