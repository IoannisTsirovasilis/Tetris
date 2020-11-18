import random
import math
import numpy as np
import GraphicsManager as GraphicsManager
from math import floor
from time import sleep


PIVOT = [2, 5]
H_SPEED = 80
LINES_MULTIPLIERS = [40, 100, 300, 1200]
BOARD_WIDTH = 10
BOARD_HEIGHT = 22
STARTING_LEVEL = 9
PLAYING_STATE = 1
GAME_OVER_STATE = 0
MAP_BLOCK = 1
MAP_EMPTY = 0
MAP_BLOCK_FALLING = 2
INITIAL_BOARD = np.zeros((BOARD_HEIGHT, BOARD_WIDTH), dtype=int)
BOARD = np.zeros((BOARD_HEIGHT, BOARD_WIDTH), dtype=int)
SIMULATE_BOARD = np.zeros((BOARD_HEIGHT, BOARD_WIDTH), dtype=int)
SIMULATE_PIVOT = [2, 5]

I = np.array([[MAP_BLOCK_FALLING, MAP_BLOCK_FALLING, MAP_BLOCK_FALLING, MAP_BLOCK_FALLING]])
J = np.array([[MAP_BLOCK_FALLING, MAP_BLOCK_FALLING, MAP_BLOCK_FALLING], [MAP_EMPTY, MAP_EMPTY, MAP_BLOCK_FALLING]])
L = np.array([[MAP_BLOCK_FALLING, MAP_BLOCK_FALLING, MAP_BLOCK_FALLING], [MAP_BLOCK_FALLING, MAP_EMPTY, MAP_EMPTY]])
O = np.array([[MAP_BLOCK_FALLING, MAP_BLOCK_FALLING], [MAP_BLOCK_FALLING, MAP_BLOCK_FALLING]])
S = np.array([[MAP_EMPTY, MAP_BLOCK_FALLING, MAP_BLOCK_FALLING], [MAP_BLOCK_FALLING, MAP_BLOCK_FALLING, MAP_EMPTY]])
T = np.array([[MAP_BLOCK_FALLING, MAP_BLOCK_FALLING, MAP_BLOCK_FALLING], [MAP_EMPTY, MAP_BLOCK_FALLING, MAP_EMPTY]])
Z = np.array([[MAP_BLOCK_FALLING, MAP_BLOCK_FALLING, MAP_EMPTY], [MAP_EMPTY, MAP_BLOCK_FALLING, MAP_BLOCK_FALLING]])
PIECES = [I, J, L, O, S, T, Z]

COORDS = [[0, 0] for i in range(4)]
SIMULATE_COORDS = [[0, 0] for i in range(4)]


def get_piece_id(piece):
    if np.array_equal(piece, O):
        return 0
    elif np.array_equal(piece, S):
        return 1
    elif np.array_equal(piece, Z):
        return 2
    elif np.array_equal(piece, T):
        return 3
    elif np.array_equal(piece, I):
        return 4
    elif np.array_equal(piece, L):
        return 5
    else:
        return 6

def copy_env_to_simulation():
    for i in range(BOARD.shape[0]):
        for j in range(BOARD.shape[1]):
            SIMULATE_BOARD[i, j] = BOARD[i, j]
    SIMULATE_PIVOT[0] = PIVOT[0]
    SIMULATE_PIVOT[1] = PIVOT[1]
    for i in range(len(COORDS)):
        for j in range(len(COORDS[0])):
            SIMULATE_COORDS[i][j] = COORDS[i][j]


def calculate_speed(level):
    return math.floor((0.8 - level * 0.007) ** level * 1000)


def get_piece_color(index):
    return GraphicsManager.PIECES_COLORS[int(floor(index))]


def get_piece_coords(is_simulation):
    return SIMULATE_COORDS if is_simulation else COORDS


# checking vertical collision for piece's vertical movement
def v_collision(board, is_simulation):
    # c stands for coordinates
    c = get_piece_coords(is_simulation)
    for j in range(4):
        # if piece is going to overlap another piece below, don't move it
        if board[c[j][0]+1][c[j][1]] == MAP_BLOCK and [c[j][0] + 1, c[j][1]] not in c:
            return False
    return True


# checking horizontal collision for piece's horizontal movement
def h_collision(d, board, is_simulation):
    # d stands for direction (-1 for left, +1 for right)
    # c stands for coordinates
    c = get_piece_coords(is_simulation)
    for j in range(4):
        # if piece is going to move out of the sides, don't move it
        if c[j][1] + d < 0 or c[j][1] + d > 9:
            return False
        # if piece is going to overlap a placed piece, don't move it
        if board[c[j][0]][c[j][1] + d] == MAP_BLOCK and [c[j][0], c[j][1] + d] not in c:
            return False
    # if piece can move, move it
    return True


# horizontal piece movement
def h_move(d, index, board, pivot, is_simulation):
    # d is the direction {-1, 1}
    try:
        if h_collision(d, board, is_simulation):
            c = get_piece_coords(is_simulation)
            for j in range(4):
                board[c[j][0]][c[j][1]] = MAP_EMPTY
            # redraw it in its new position, one column right/left
            for j in range(4):
                board[c[j][0]][c[j][1] + d] = index
                c[j][1] += d
            # update pivot's position
            pivot[1] += d
            return True
    except IndexError:
        return False


# piece rotation (clock-wise)
# It works with pivoting. When you see the game board the block at first row and sixth column plays the role
# of the pivot. All other piece's block rotate around this block. That's what this method accomplishes.
def r_move(ptr, index, r, board, pivot, is_simulation):
    # ptr stands for piece to rotate
    # r stands for rotated {True, False}

    # piece O doesn't rotate
    if np.array_equal(ptr, O):
        return False
    c = get_piece_coords(is_simulation)
    # i_rot, j_rot are the coordinates of rotated piece
    if any(np.array_equal(ptr, p) for p in [I, S, Z]):
        # I, S and Z have a different rotation. What the code below does is that it returns the piece to its
        # spawn state every second rotation.
        # so if it's not r (rotated) then perform a typical rotation
        if not r:
            try:
                for j in range(4):
                    # if they exceed boundaries, don't rotate
                    i_rot = -c[j][1] + pivot[1] + pivot[0]
                    j_rot = c[j][0] - pivot[0] + pivot[1]
                    if i_rot < 0 or i_rot > 21 or j_rot < 0 or j_rot > 9:
                        return False
                    # if after rotation, piece overlaps with another piece, don't rotate
                    if board[i_rot][j_rot] == MAP_BLOCK and [i_rot, j_rot] not in c:
                        return False
            except IndexError:
                return False
            for j in range(4):
                if c[j][0] != pivot[0] or c[j][1] != pivot[1]: # pivot block doesn't rotate
                    # erase block
                    board[c[j][0]][c[j][1]] = MAP_EMPTY
            for j in range(4):
                i_rot = -c[j][1] + pivot[1] + pivot[0]
                j_rot = c[j][0] - pivot[0] + pivot[1]
                if c[j][0] != pivot[0] or c[j][1] != pivot[1]:
                    # redraw block in new position
                    board[i_rot][j_rot] = index
                    c[j][0] = i_rot
                    c[j][1] = j_rot
            return True
    # else if it is rotated, return it to its original state.
    # The code below also works for L,J and T pieces.
    try:
        for j in range(4):
            i_rot = c[j][1] - pivot[1] + pivot[0]
            j_rot = -c[j][0] + pivot[0] + pivot[1]
            if i_rot < 0 or i_rot > 21 or j_rot < 0 or j_rot > 9:
                return True
            if board[i_rot][j_rot] == MAP_BLOCK and [i_rot, j_rot] not in c:
                return True
        for j in range(4):
            if c[j][0] != pivot[0] or c[j][1] != PIVOT[1]:
                board[c[j][0]][c[j][1]] = MAP_EMPTY
    except IndexError:
        return True
    for j in range(4):
        i_rot = c[j][1] - pivot[1] + pivot[0]
        j_rot = -c[j][0] + pivot[0] + pivot[1]
        if c[j][0] != pivot[0] or c[j][1] != pivot[1]:
            board[i_rot][j_rot] = index
            c[j][0] = i_rot
            c[j][1] = j_rot
    return False


def spawn_piece(pts):
    game_over = False
    reset_pivot()
    k = 0
    for i in range(pts.shape[0]):
        for j in range(pts.shape[1]):
            if pts[i][j] == MAP_EMPTY:
                continue
            else:
                if BOARD[(i+2)][(j+4) - (2 - pts.shape[0])] == MAP_BLOCK:
                    game_over = True

                BOARD[(i+2)][(j+4) - (2 - pts.shape[0])] = pts[i][j]
                COORDS[k][0] = i + 2
                COORDS[k][1] = (j+4) - (2 - pts.shape[0])
                SIMULATE_COORDS[k][0] = i + 2
                SIMULATE_COORDS[k][1] = (j + 4) - (2 - pts.shape[0])
                k += 1
    return game_over


def reset_pivot():
    PIVOT[0] = 2
    PIVOT[1] = 5


def game_over():
    return True


def heights_diff():
    col_heights = []

    for col in zip(*BOARD):
        i = 0
        while i < BOARD_HEIGHT and col[i] == MAP_EMPTY:
            i += 1
        height = BOARD_HEIGHT - i
        col_heights.append(height)
    return col_heights


class GameController:
    def __init__(self, fps):
        self.state_initializer()
        self.fps = fps
        self.score = 0
        self.lines = 0
        self.level = STARTING_LEVEL
        self.speed = calculate_speed(self.level)
        self.lines_to_level_up = 10
        # 1 is Playing, 0 is Game Over
        self.game_state = 1
        self.rotated = False
        self.drop_counter = 0
        self.move_counter = 0
        self.piece_falling = False
        self.next_pieces = [np.copy(PIECES[random.randint(0, len(PIECES) - 1)])]
        self.can_h_move = True
        self.can_rotate = True
        self.holes = 0
        self.total_bumpiness = 0
        self.total_height = 0
        self.previous_lines = self.lines
        self.current_piece = None
        self.simulation_lines_to_erase = 0

    def state_initializer(self):
        self.game_state = PLAYING_STATE
        BOARD[BOARD != MAP_EMPTY] = MAP_EMPTY
        self.level = STARTING_LEVEL
        self.set_speed(self.level)
        self.move_counter = 0
        self.drop_counter = 0
        self.lines_to_level_up = 10
        self.lines = 0
        self.piece_falling = False
        self.rotated = False
        self.next_pieces = [np.copy(PIECES[random.randint(0, len(PIECES) - 1)])]
        self.score = 0
        self.can_h_move = True
        self.can_rotate = True
        self.holes = 0
        self.total_bumpiness = 0
        self.total_height = 0
        self.previous_lines = self.lines
        self.current_piece = None
        self.simulation_lines_to_erase = 0

    def set_speed(self, level):
        self.speed = calculate_speed(level)

    def create_piece_sequence(self):
        for i in range(7):
            self.next_pieces.append(np.copy(PIECES[random.randint(0, len(PIECES)-1)]))

    # vertical piece movement
    def v_move(self, index, board, pivot, is_simulation):
        # if piece tries to move out of bounds, except IndexError
        try:
            # if there space to move vertically, then move
            if v_collision(board, is_simulation):
                # c stands for coordinates
                c = get_piece_coords(is_simulation)
                # erase piece from board
                for j in range(4):
                    board[c[j][0]][c[j][1]] = MAP_EMPTY
                # redraw it in its new position, one row lower
                for j in range(4):
                    board[c[j][0]+1][c[j][1]] = index
                    c[j][0] += 1
                # update pivot's position
                pivot[0] += 1
                return True
            raise IndexError()
        except IndexError:
            self.update_board(board, is_simulation)
            return False

    def update_board(self, board, is_simulation):
        c = get_piece_coords(is_simulation)
        for j in range(4):
            board[c[j][0]][c[j][1]] = MAP_BLOCK
        # returns true if every element in a row is non-zero, else false, for each row
        if is_simulation:
            self.simulation_lines_to_erase = np.sum(np.all(board[:, ...] == MAP_BLOCK, axis=1))
            return

        lines_state = np.all(board[:, ...] == MAP_BLOCK, axis=1)
        lines_to_erase = 0
        for i in range(lines_state.shape[0]):
            # if line is full of piece blocks
            if lines_state[i]:
                lines_to_erase += 1
                board[i] = MAP_EMPTY
                for r in reversed(range(i+1)):
                    if r > 0:
                        board[r] = np.copy(board[r-1])
        self.lines += lines_to_erase
        if lines_to_erase > 0:
            self.score += lines_to_erase
            if self.score > 999999:
                self.score = 999999

    def level_up(self):
        self.level += 1
        self.set_speed(self.level)

    def number_of_holes(self, board):
        '''Number of holes in the board (empty sqquare with at least one block above it)'''
        holes = 0

        for col in zip(*board):
            i = 0
            while i < BOARD_HEIGHT and col[i] != MAP_BLOCK:
                i += 1
            holes += len([x for x in col[i + 1:] if x == MAP_EMPTY])

        return holes

    def bumpiness(self, board):
        '''Sum of the differences of heights between pair of columns'''
        total_bumpiness = 0
        max_bumpiness = 0
        min_ys = []

        for col in zip(*board):
            i = 0
            while i < BOARD_HEIGHT and col[i] != MAP_BLOCK:
                i += 1
            min_ys.append(i)

        for i in range(len(min_ys) - 1):
            bumpiness = abs(min_ys[i] - min_ys[i + 1])
            max_bumpiness = max(bumpiness, max_bumpiness)
            total_bumpiness += abs(min_ys[i] - min_ys[i + 1])

        return total_bumpiness, max_bumpiness

    def height(self, board):
        '''Sum and maximum height of the board'''
        sum_height = 0

        for col in zip(*board):
            i = BOARD_HEIGHT - 1
            while i < BOARD_HEIGHT and col[i] == MAP_EMPTY:
                i += 1
            height = BOARD_HEIGHT - i
            sum_height += height

        return sum_height

    def empty_columns(self, board):
        empty_columns = np.count_nonzero(np.all(board[..., :] == 0, axis=0) == 1)
        return empty_columns
