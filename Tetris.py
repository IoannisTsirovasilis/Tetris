import time

import pygame as pg
import numpy as np
import sys
import random

pg.mixer.pre_init(44100, -16, 2, 2048)
pg.mixer.init()
pg.init()
pg.font.init()
SOUNDS_PATH = "C:/Users/Giannis/Desktop/block-rotate/"
BLACK = [77, 77, 77]
PURPLE = [255, 0, 255]
BLUE = [128, 191, 255]
ORANGE = [255, 165, 0]
YELLOW = [204, 204, 0]
CYAN = [0, 255, 255]
RED = [255, 0, 0]
GREEN = [0, 153, 51]
WHITE = [255, 255, 255]
next_pieces = []
I = np.array([[1, 1, 1, 1]])
J = np.array([[2, 2, 2], [0, 0, 2]])
L = np.array([[3, 3, 3], [3, 0, 0]])
O = np.array([[4, 4], [4, 4]])
S = np.array([[0, 5, 5], [5, 5, 0]])
T = np.array([[6, 6, 6], [0, 6, 0]])
Z = np.array([[7, 7, 0], [0, 7, 7]])

# Clock-Wise Rotation Matrix
R = np.array([[0, 1], [-1, 0]])
FRAMERATE = 30
pivot_i = None

PIECES = [I, J, L, O, S, T, Z]
random.seed()
game_speed = 100
SIZE = WIDTH, HEIGHT = 1186, 964  # (20x10) with 2px between cells
score = 0
lines = 0
level = 9
lines_multipliers = [40, 100, 300, 1200]
# 1 hidden row
board = np.array([[0 for j in range(10)] for i in range(22)])
piece_falling = False

screen = pg.display.set_mode(SIZE)
screen.fill((0, 0, 0))
piece = []
color = BLACK
pg.time.set_timer(pg.USEREVENT + 1, game_speed)


def get_piece_color(index):
    if index == 0:
        return BLACK
    elif abs(index) == 1:
        return CYAN
    elif abs(index) == 2:
        return BLUE
    elif abs(index) == 3:
        return ORANGE
    elif abs(index) == 4:
        return YELLOW
    elif abs(index) == 5:
        return GREEN
    elif abs(index) == 6:
        return PURPLE
    else:
        return RED


def get_piece_indices(board):
    # Get indices of current piece in row, column format
    r, c = np.where(board > 0)
    # Stack rows and columns
    indices = np.vstack((r, c))
    return indices


def check_collision(board):
    indices = get_piece_indices(board)
    for j in range(4):
        if board[indices[0][j] + 1][indices[1][j]] < 0:
            return False
    return True


def check_side_collision(board, direction):
    indices = get_piece_indices(board)
    for j in range(4):
        if indices[1][j] + direction < 0 or indices[1][j] + direction > 9:
            return False
        if board[indices[0][j]][indices[1][j] + direction] < 0:
            return False
    return True


def update_board(board, index):
    global lines
    global score
    indices = get_piece_indices(board)
    for j in range(4):
        board[indices[0][j]][indices[1][j]] = -index
    temp = np.all(board, axis=1)
    line_counter = 0
    for i in range(temp.shape[0]):
        if temp[i]:
            line_counter += 1
            board[i] = 0
            for r in reversed(range(i + 1)):
                if r > 0:
                    board[r] = np.copy(board[r - 1])
    if line_counter == 4:
        pg.mixer.Channel(2).play(pg.mixer.Sound(SOUNDS_PATH + "line-removal4.wav"))
    elif line_counter > 0:
        pg.mixer.Channel(2).play(pg.mixer.Sound(SOUNDS_PATH + "line-remove.wav"))
    else:
        pg.mixer.Channel(2).play(pg.mixer.Sound(SOUNDS_PATH + "force-hit.wav"))
    lines += line_counter
    if line_counter > 0:
        score = 999999 if score + (level + 1) * lines_multipliers[line_counter - 1] > 999999 else score + (level + 1) * lines_multipliers[line_counter - 1]
        font = pg.font.SysFont('Comic Sans MS', 30)
        score_label = font.render("SCORE", False, WHITE)
        pg.draw.rect(screen, BLACK, pg.Rect((WIDTH - 346, 300), (175, 100)))
        screen.blit(score_label, (WIDTH - 311, 305))
        score_count = font.render(str.zfill(str(score), 6), False, WHITE)
        screen.blit(score_count, (WIDTH - 311, 355))


def drop_piece(board, index):
    global pivot_i
    try:
        if check_collision(board):
            indices = get_piece_indices(board)
            for j in range(4):
                board[indices[0][j]][indices[1][j]] = 0
            for j in range(4):
                board[indices[0][j] + 1][indices[1][j]] = index
            pivot_i[0] += 1
            return True
        else:
            update_board(board, index)
            return False
    except IndexError:
        update_board(board, index)
        return False


def move_piece(board, direction):
    try:
        if check_side_collision(board, direction):
            for i in reversed(range(len(board))):
                if direction == -1:
                    for j in range(10):
                        if board[i][j] > 0:
                            board[i][j + direction], board[i][j] = board[i][j], 0
                elif direction == 1:
                    for j in reversed(range(10)):
                        if board[i][j] > 0:
                            board[i][j + direction], board[i][j] = board[i][j], 0
            pivot_i[1] += direction
    except IndexError:
        return


def spawn_piece(piece):
    global board
    global pivot_i
    pivot_i = [2, 5]
    if np.array_equal(piece, I):
        if not np.array_equal(board[2:3, 3:7][board[2:3, 3:7] < 0], []):
            board[2:3, 3:7] = np.copy(piece)
            game_over()
        board[2:3, 3:7] = np.copy(piece)
    elif any(np.array_equal(piece, block) for block in [J, L, S, Z, T]):
        if not np.array_equal(board[2:4, 4:7][board[2:4, 4:7] < 0], []):
            board[2:4, 4:7] = np.copy(piece)
            game_over()
        board[2:4, 4:7] = np.copy(piece)
    else:
        if not np.array_equal( board[2:4, 4:6][board[2:4, 4:6] < 0], []):
            board[2:4, 4:6] = np.copy(piece)
            game_over()
        board[2:4, 4:6] = np.copy(piece)


def game_over():
    pg.mixer.Channel(0).play(pg.mixer.Sound(SOUNDS_PATH + "game-over.wav"))
    action = False
    while not action:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            if pg.key.get_pressed()[pg.K_SPACE]:
                return menu()
            if pg.key.get_pressed()[pg.K_ESCAPE]:
                sys.exit()
        for i in range(22):
            for j in range(10):
                if i in [0, 1]:
                    pg.draw.rect(screen, (0, 0, 0),
                                 pg.Rect((2 * (j + 12) + 35 * (j + 11), 2 * (i + 3) + 35 * (i + 2)), (35, 35)))
                else:
                    pg.draw.rect(screen, get_piece_color(board[i][j]),
                                 pg.Rect((2 * (j + 12) + 35 * (j + 11), 2 * (i + 3) + 35 * (i + 2)), (35, 35)))
        pg.display.update()


def rotate_piece(piece, index, rotated):
    pg.mixer.Channel(1).play(pg.mixer.Sound(SOUNDS_PATH + "block-rotate.wav"))
    if np.array_equal(piece, O):
        return
    global board
    global R
    global pivot_i
    ind = get_piece_indices(board)
    print(pivot_i)
    if any(np.array_equal(piece, p) for p in [I, S, Z]):
        if not rotated:
            try:
                for j in range(4):
                    if -ind[1][j] + pivot_i[1] + pivot_i[0] < 0 or -ind[1][j] + pivot_i[1] + pivot_i[0] > 21 or ind[0][
                        j] - pivot_i[0] + pivot_i[1] < 0 or ind[0][j] - pivot_i[0] + pivot_i[1] > 9:
                        return False
                    if board[-ind[1][j] + pivot_i[1] + pivot_i[0]][ind[0][j] - pivot_i[0] + pivot_i[1]] < 0:
                        return False
            except IndexError:
                return False
            for j in range(4):
                if ind[0][j] != pivot_i[0] or ind[1][j] != pivot_i[1]:
                    board[ind[0][j]][ind[1][j]] = 0
            for j in range(4):
                if ind[0][j] != pivot_i[0] or ind[1][j] != pivot_i[1]:
                    board[-ind[1][j] + pivot_i[1] + pivot_i[0]][ind[0][j] - pivot_i[0] + pivot_i[1]] = index
            return True
    try:
        for j in range(4):
            if ind[1][j] - pivot_i[1] + pivot_i[0] < 0 or ind[1][j] - pivot_i[1] + pivot_i[0] > 21 or -ind[0][j] + \
                    pivot_i[0] + pivot_i[1] < 0 or -ind[0][j] + pivot_i[0] + pivot_i[1] > 9:
                return True
            if board[ind[1][j] - pivot_i[1] + pivot_i[0]][-ind[0][j] + pivot_i[0] + pivot_i[1]] < 0:
                return True
        for j in range(4):
            if ind[0][j] != pivot_i[0] or ind[1][j] != pivot_i[1]:
                board[ind[0][j]][ind[1][j]] = 0
    except IndexError:
        return True
    for j in range(4):
        if ind[0][j] != pivot_i[0] or ind[1][j] != pivot_i[1]:
            board[ind[1][j] - pivot_i[1] + pivot_i[0]][-ind[0][j] + pivot_i[0] + pivot_i[1]] = index
    return False


def menu():
    global screen
    pg.mixer.Channel(0).play(pg.mixer.Sound(SOUNDS_PATH + "theme.wav"), -1)
    screen.fill((0, 0, 0))
    font = pg.font.SysFont('Comic Sans MS', 30)
    play = font.render('Play', False, WHITE)
    quit = font.render('Quit', False, WHITE)
    action = False
    while not action:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            if pg.mouse.get_pressed()[0]:
                mouse = pg.mouse.get_pos()
                if WIDTH // 2 - 90 < mouse[0] < WIDTH // 2 + 90 and HEIGHT // 2 - 115 < mouse[1] < HEIGHT // 2 - 35:
                    action = True
                    game()
                if WIDTH // 2 - 90 < mouse[0] < WIDTH // 2 + 90 and HEIGHT // 2 + 35 < mouse[1] < HEIGHT // 2 + 115:
                    sys.exit()
        pg.draw.rect(screen, BLACK, pg.Rect((WIDTH // 2 - 90, HEIGHT // 2 - 115), (180, 80)))
        screen.blit(play, (WIDTH // 2 - 30, HEIGHT // 2 - 100))
        pg.draw.rect(screen, BLACK, pg.Rect((WIDTH // 2 - 90, HEIGHT // 2 + 35), (180, 80)))
        screen.blit(quit, (WIDTH // 2 - 30, HEIGHT // 2 + 50))
        t = [(1, 4), (1, 5), (1, 6), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5)]
        e = [(1, 8), (1, 9), (1, 10), (2, 8), (3, 8), (4, 8), (4, 9), (4, 10), (5, 8), (6, 8), (7, 8), (7, 9), (7, 10)]
        t2 = [(1, 12), (1, 13), (1, 14), (2, 13), (3, 13), (4, 13), (5, 13), (6, 13), (7, 13)]
        r = [(1, 16), (1, 17), (1, 18), (1, 19), (1, 20), (2, 16), (2, 20), (3, 16), (3, 19), (4, 16), (4, 17), (4, 18),
             (5, 16), (5, 19), (6, 16), (6, 20), (7, 16), (7, 21)]
        i = [(1, 23), (2, 23), (3, 23), (4, 23), (5, 23), (6, 23), (7, 23)]
        s = [(1, 25), (1, 26), (1, 27), (2, 25), (2, 27), (3, 25), (4, 25), (4, 26), (4, 27), (5, 27), (6, 25), (6, 27),
             (7, 25), (7, 26), (7, 27)]
        logo = [(t, RED), (e, ORANGE), (t2, YELLOW), (r, GREEN), (i, CYAN), (s, PURPLE)]
        for letter in logo:
            for l in letter[0]:
                pg.draw.rect(screen, letter[1],
                             pg.Rect((2 * (l[1] + 1) + 35 * l[1], 2 * (l[0] + 1) + 35 * l[0]), (35, 35)))
        pg.display.update()


def game():
    global screen
    global piece_falling
    global next_pieces
    global board
    global score
    global lines
    global level
    global lines_multipliers
    score = 0
    lines = 0
    level = 9
    lines_multipliers = [40, 100, 300, 1200]
    screen.fill((0, 0, 0))
    font = pg.font.SysFont('Comic Sans MS', 30)
    score_label = font.render("SCORE", False, WHITE)
    pg.draw.rect(screen, BLACK, pg.Rect((WIDTH - 346, 300), (175, 100)))
    screen.blit(score_label, (WIDTH - 311, 305))
    score_count = font.render(str.zfill(str(score), 6), False, WHITE)
    screen.blit(score_count, (WIDTH - 311, 355))
    board = np.array([[0 for j in range(10)] for i in range(22)])
    next_pieces.append(np.copy(PIECES[random.randint(0, len(PIECES) - 1)]))
    index = 0
    clock = pg.time.Clock()
    rotate_counter = 0
    up_pressed = True
    rotated = False
    move_counter = 0
    left_right_pressed = True
    game_started = False
    piece_falling = False
    next_piece = np.reshape(np.array([]), (0, 0))
    while True:
        if len(next_pieces) <= 2:
            for i in range(500):
                next_pieces.append(np.copy(PIECES[random.randint(0, len(PIECES) - 1)]))
        move_counter += 1
        rotate_counter += 1
        clock.tick(FRAMERATE)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            if game_started:
                if event.type == (pg.USEREVENT + 1):
                    piece_falling = drop_piece(board, index)
                if left_right_pressed:
                    if pg.key.get_pressed()[pg.K_LEFT]:
                        left_right_pressed = False
                        move_piece(board, -1)
                    if pg.key.get_pressed()[pg.K_RIGHT]:
                        left_right_pressed = False
                        move_piece(board, 1)
                if up_pressed:
                    if pg.key.get_pressed()[pg.K_UP]:
                        up_pressed = False
                        rotated = rotate_piece(piece, index, rotated)

        if move_counter >= FRAMERATE // 10:
            move_counter = 0
            left_right_pressed = True
        if rotate_counter >= FRAMERATE // 3:
            rotate_counter = 0
            up_pressed = True
        if not piece_falling:
            piece_falling = True

            # Take a copy of the spawning piece
            piece_to_spawn = next_pieces[:][0]
            del next_pieces[0]
            next_piece = next_pieces[:][0]
            index = piece_to_spawn[piece_to_spawn > 0][0]
            spawn_piece(piece_to_spawn)
            piece = piece_to_spawn[:]
        if not game_started:
            game_started = True
        for i in range(22):
            for j in range(10):
                if i in [0, 1]:
                    pg.draw.rect(screen, (0, 0, 0),
                                 pg.Rect((2 * (j + 12) + 35 * (j + 11), 2 * (i + 3) + 35 * (i + 2)), (35, 35)))
                else:
                    pg.draw.rect(screen, get_piece_color(board[i][j]),
                                 pg.Rect((2 * (j + 12) + 35 * (j + 11), 2 * (i + 3) + 35 * (i + 2)), (35, 35)))
        for i in range(5):
            for j in range(5):
                pg.draw.rect(screen, BLACK,
                             pg.Rect((35 * (j + 24), 35 * (i + 13)), (35, 35)))
        next_piece_label = font.render("NEXT", False, WHITE)
        screen.blit(next_piece_label, (WIDTH - 298, 455))
        for i in range(next_piece.shape[0]):
            for j in range(next_piece.shape[1]):
                if np.array_equal(next_piece, I):
                    pg.draw.rect(screen, get_piece_color(next_piece[i][j]) if next_piece[i][j] > 0 else BLACK,
                                 pg.Rect((2 * (j + 27) + 30 * (j + 27), 2 * (i + 18) + 30 * (i + 17)), (30, 30)))
                else:
                    pg.draw.rect(screen, get_piece_color(next_piece[i][j]) if next_piece[i][j] > 0 else BLACK,
                                 pg.Rect((2 * (j + 28) + 30 * (j + 28), 2 * (i + 18) + 30 * (i + 17)), (30, 30)))

        pg.display.update()


def main():
    menu()


if __name__ == "__main__":
    main()
