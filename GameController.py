import random

import SoundManager
import GameUI
import math
import numpy as np


class GameController:
    def __init__(self, fps):
        self.FPS = fps
        self.I = np.array([[1, 1, 1, 1]])
        self.J = np.array([[2, 2, 2], [0, 0, 2]])
        self.L = np.array([[3, 3, 3], [3, 0, 0]])
        self.O = np.array([[4, 4], [4, 4]])
        self.S = np.array([[0, 5, 5], [5, 5, 0]])
        self.T = np.array([[6, 6, 6], [0, 6, 0]])
        self.Z = np.array([[7, 7, 0], [0, 7, 7]])
        self.PIECES = [self.I, self.J, self.L, self.O, self.S, self.T, self.Z]
        self.pivot = [2, 5]
        self.score = 0
        self.h_speed = 200
        self.lines = 0
        self.level = 0
        self.speed = 1000
        self.line_multipliers = [40, 100, 300, 1200]
        self.board = np.array([[0 for j in range(10)] for i in range(22)])
        self.track = "track1.wav"

        # 0 is Main Menu, 1 is Settings, 2 is Playing, 3 is Game Over
        self.game_state = 0

        self.rotated = False
        self.drop_counter = 0
        self.move_counter = 0
        self.piece_falling = False
        self.next_pieces = [np.copy(self.PIECES[random.randint(0, len(self.PIECES) - 1)])]
        self.theme_playing = False
        self.game_over_sound_played = False
        self.can_h_move = True
        self.can_rotate = True

    def set_speed(self, level):
        self.speed = math.floor((0.8 - level * 0.007) ** level * 1000)

    def create_piece_sequence(self):
        for i in range(7):
            self.next_pieces.append(np.copy(self.PIECES[random.randint(0, len(self.PIECES)-1)]))

    def state_initializer(self, game_state, gui: GameUI):
        self.game_state = game_state
        gui.screen.fill(gui.BLACK)
        self.board = np.array([[0 for j in range (10)] for i in range(22)])
        self.move_counter = 0
        self.drop_counter = 0
        self.piece_falling = False
        self.rotated = False
        self.next_pieces = [np.copy(self.PIECES[random.randint(0, len(self.PIECES) - 1)])]
        self.theme_playing = False
        self.game_over_sound_played = False
        self.score = 0
        self.can_h_move = True
        self.can_rotate = True

    def get_piece_color(self, index, gui: GameUI):
        if index == 0:
            return gui.GREY
        elif abs(index) == 1:
            return gui.CYAN
        elif abs(index) == 2:
            return gui.BLUE
        elif abs(index) == 3:
            return gui.ORANGE
        elif abs(index) == 4:
            return gui.YELLOW
        elif abs(index) == 5:
            return gui.GREEN
        elif abs(index) == 6:
            return gui.PURPLE
        else:
            return gui.RED

    def get_piece_coords(self):
        r, c = np.where(self.board > 0)
        return np.vstack((r, c))

    # checking vertical collision for piece's vertical movement
    def v_collision(self):
        # c stands for coordinates
        c = self.get_piece_coords()
        for j in range(4):
            # if piece is going to overlap another piece below, don't move it
            if self.board[c[0][j]+1][c[1][j]] < 0:
                return False
        return True

    # checking horizontal collision for piece's horizontal movement
    def h_collision(self, d):
        # d stands for direction (-1 for left, +1 for right)
        # c stands for coordinates
        c = self.get_piece_coords()
        for j in range(4):
            # if piece is going to move out of the sides, don't move it
            if c[1][j] + d < 0 or c[1][j] + d > 9:
                return False
            # if piece is going to overlap a placed piece, don't move it
            if self.board[c[0][j]][c[1][j] + d] < 0:
                return False
        # if piece can move, move it
        return True

    # vertical piece movement
    def v_move(self, index, sm: SoundManager):
        # if piece tries to move out of bounds, except IndexError
        try:
            # if there space to move vertically, then move
            if self.v_collision():
                # c stands for coordinates
                c = self.get_piece_coords()
                # erase piece from board
                for j in range(4):
                    self.board[c[0][j]][c[1][j]] = 0
                # redraw it in its new position, one row lower
                for j in range(4):
                    self.board[c[0][j]+1][c[1][j]] = index
                # update pivot's position
                self.pivot[0] += 1
                return True
            else:
                self.update_board(index, sm)
                return False
        except IndexError:
            self.update_board(index, sm)
            return False

    # horizontal piece movement
    def h_move(self, d, index):
        # d is the direction {-1, 1}
        try:
            if self.h_collision(d):
                c = self.get_piece_coords()
                for j in range(4):
                    self.board[c[0][j]][c[1][j]] = 0
                # redraw it in its new position, one column right/left
                for j in range(4):
                    self.board[c[0][j]][c[1][j] + d] = index
                # update pivot's position
                self.pivot[1] += d
                return True
        except IndexError:
            return False

    # piece rotation (clock-wise)
    def r_move(self, ptr, index, r):
        # p stands for piece to rotate
        # r stands for rotated {True, False}

        # piece O doesn't rotate
        if np.array_equal(ptr, self.O):
            return
        c = self.get_piece_coords()
        # i_rot, j_rot are the coordinates of rotated piece
        if any(np.array_equal(ptr, p) for p in [self.I, self.S, self.Z]):
            if not r:
                try:
                    for j in range(4):
                        # if they exceed boundaries, don't rotate
                        i_rot = -c[1][j]+self.pivot[1]+self.pivot[0]
                        j_rot = c[0][j] - self.pivot[0] + self.pivot[1]
                        if i_rot < 0 or i_rot > 21 or j_rot < 0 or j_rot > 9:
                            return False
                        # if after rotation, piece overlaps with another piece, don't rotate
                        if self.board[i_rot][j_rot] < 0:
                            return False
                except IndexError:
                    return False
                for j in range(4):
                    if c[0][j] != self.pivot[0] or c[1][j] != self.pivot[1]: # pivot block doesn't rotate
                        # erase block
                        self.board[c[0][j]][c[1][j]] = 0
                for j in range(4):
                    i_rot = -c[1][j] + self.pivot[1] + self.pivot[0]
                    j_rot = c[0][j] - self.pivot[0] + self.pivot[1]
                    if c[0][j] != self.pivot[0] or c[1][j] != self.pivot[1]:
                        # redraw block in new position
                        self.board[i_rot][j_rot] = index
                return True
        try:
            for j in range(4):
                i_rot = c[1][j] - self.pivot[1] + self.pivot[0]
                j_rot = -c[0][j] + self.pivot[0] + self.pivot[1]
                if i_rot < 0 or i_rot > 21 or j_rot < 0 or j_rot > 9:
                    return True
                if self.board[i_rot][j_rot] < 0:
                    return True
            for j in range(4):
                if c[0][j] != self.pivot[0] or c[1][j] != self.pivot[1]:
                    self.board[c[0][j]][c[1][j]] = 0
        except IndexError:
            return True
        for j in range(4):
            i_rot = c[1][j] - self.pivot[1] + self.pivot[0]
            j_rot = -c[0][j] + self.pivot[0] + self.pivot[1]
            if c[0][j] != self.pivot[0] or c[1][j] != self.pivot[1]:
                self.board[i_rot][j_rot] = index
        return False

    def update_board(self, index, sm: SoundManager):
        c = self.get_piece_coords()
        for j in range(4):
            self.board[c[0][j]][c[1][j]] = -index
        # returns true if every element in a row is non-zero, else false, for each row
        lines_state = np.all(self.board, axis=1)
        lines_to_erase = 0
        for i in range(lines_state.shape[0]):
            # if line is full of piece blocks
            if lines_state[i]:
                lines_to_erase += 1
                self.board[i] = 0
                for r in reversed(range(i+1)):
                    if r > 0:
                        self.board[r] = np.copy(self.board[r-1])
        if lines_to_erase == 4:
            sm.play_sound("tetris.wav", 2, 0)
        elif lines_to_erase > 0:
            sm.play_sound("line-remove.wav", 2, 0)
        else:
            sm.play_sound("piece-fall.wav", 2, 0)
        self.lines += lines_to_erase
        if lines_to_erase > 0:
            temp = (self.level+1)*self.line_multipliers[lines_to_erase-1]
            if self.score + temp > 999999:
                self.score = 999999
            else:
                self.score += temp

    def spawn_piece(self, pts):
        game_over = False
        self.pivot = [2, 5]
        for i in range(pts.shape[0]):
            for j in range(pts.shape[1]):
                if pts[i][j] == 0:
                    continue
                else:
                    if self.board[(i+2)][(j+4) - (2 - pts.shape[0])] < 0:
                        game_over = True
                    self.board[(i+2)][(j+4) - (2 - pts.shape[0])] = pts[i][j]
        return game_over

    def game_over(self, sm: SoundManager):
        sm.play_sound("game-over.wav", 0, 0)
        return True
