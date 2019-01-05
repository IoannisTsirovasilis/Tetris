from GraphicsManager import GraphicsManager
from GameController import GameController


class GameUI(GraphicsManager):
    def __init__(self, width, height):
        super().__init__(width, height)

    def __draw_game_board(self, gc: GameController):
        for i in range(22):
            for j in range(10):
                if i in [0, 1]:
                    self.draw_rect(35, 35, 2 * (j + 12) + 35 * (j + 11), 2 * (i + 3) + 35 * (i + 2), self.BLACK)
                else:
                    self.draw_rect(35, 35, 2 * (j + 12) + 35 * (j + 11), 2 * (i + 3) + 35 * (i + 2),
                                   gc.get_piece_color(gc.board[i][j], self))

    def __draw_next_piece_board(self, gc: GameController, next_piece, is_I):
        color = gc.get_piece_color(next_piece[next_piece > 0][0], self)
        for i in range(5):
            for j in range(5):
                self.draw_rect(35, 35, 35 * (j + 24), 35 * (i + 13), self.GREY)
        self.draw_text(self.FONT, 30, "NEXT", self.WHITE, self.WIDTH - 298, 455)
        for i in range(next_piece.shape[0]):
            for j in range(next_piece.shape[1]):
                tmp_color = color if next_piece[i][j] > 0 else self.GREY
                if is_I:
                    self.draw_rect(30, 30, 2 * (j + 27) + 30 * (j + 27), 2 * (i + 18) + 30 * (i + 17), tmp_color)
                else:
                    self.draw_rect(30, 30, 2 * (j + 28) + 30 * (j + 28), 2 * (i + 18) + 30 * (i + 17), tmp_color)

    def __draw_score_board(self, score):
        self.draw_rect(175, 100, self.WIDTH - 346, 300, self.GREY)
        self.draw_text(self.FONT, 30, "SCORE", self.WHITE, self.WIDTH - 311, 305)
        self.draw_text(self.FONT, 30, str.zfill(str(score), 6), self.WHITE, self.WIDTH - 311, 355)

    def draw_game_ui(self, gc: GameController, next_piece, is_I):
        self.__draw_game_board(gc)
        self.__draw_next_piece_board(gc, next_piece, is_I)
        self.__draw_score_board(gc.score)

