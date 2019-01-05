import time
import pygame as pg
import numpy as np
import sys
import random
from SoundManager import SoundManager
from MainMenuUI import MainMenuUI
from GameUI import GameUI
from GameController import GameController

def main():
    pg.init()
    pg.font.init()
    WIDTH = 1186
    HEIGHT = 964
    sm = SoundManager("C:/Users/Giannis/Desktop/block-rotate/")
    mui = MainMenuUI(WIDTH, HEIGHT)
    gui = GameUI(WIDTH, HEIGHT)
    gc = GameController(30, 9)
    # 0 is Main Menu, 1 is Playing, 2 is Game Over
    game_state = 0
    up_pressed = True
    rotated = False
    rotate_counter = 0
    move_counter = 0
    left_right_pressed = True
    game_started = False
    piece_falling = False
    next_pieces = [np.copy(gc.PIECES[random.randint(0, len(gc.PIECES) - 1)])]
    next_piece = np.reshape(np.array([]), (0, 0))
    index = 0
    pg.time.set_timer(pg.USEREVENT + 1, gc.speed)
    clock = pg.time.Clock()
    theme_playing = False
    game_over_sound_played = False
    while True:
        if len(next_pieces) <= 2:
            for i in range(7):
                next_pieces.append(np.copy(gc.PIECES[random.randint(0, len(gc.PIECES) - 1)]))
        move_counter += 1
        rotate_counter += 1
        clock.tick(gc.FPS)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            if game_state == 2:
                if pg.key.get_pressed()[pg.K_SPACE]:
                    game_state = 1
                    gui.screen.fill(gui.BLACK)
                    gc.board = np.array([[0 for j in range (10)] for i in range(22)])
                    piece_falling = False
                    sm.play_sound("theme.wav", 0, -1)
                    game_over_sound_played = False
                    gc.score = 0
                    next_pieces = [np.copy(gc.PIECES[random.randint(0, len(gc.PIECES) - 1)])]
                    if len(next_pieces) <= 2:
                        for i in range(7):
                            next_pieces.append(np.copy(gc.PIECES[random.randint(0, len(gc.PIECES) - 1)]))
                if pg.key.get_pressed()[pg.K_ESCAPE]:
                    game_state = 0
                    gc.board = np.array([[0 for j in range(10)] for i in range(22)])
                    piece_falling = False
                    sm.play_sound("theme.wav", 0, -1)
                    game_over_sound_played = False
                    gc.score = 0
                    next_pieces = [np.copy(gc.PIECES[random.randint(0, len(gc.PIECES) - 1)])]
                    if len(next_pieces) <= 2:
                        for i in range(7):
                            next_pieces.append(np.copy(gc.PIECES[random.randint(0, len(gc.PIECES) - 1)]))
            if game_state == 0:
                if pg.mouse.get_pressed()[0]:
                    mouse = pg.mouse.get_pos()
                    if WIDTH // 2 - 90 < mouse[0] < WIDTH // 2 + 90 and HEIGHT // 2 - 115 < mouse[1] < HEIGHT // 2 - 35:
                        game_state = 1
                    if WIDTH // 2 - 90 < mouse[0] < WIDTH // 2 + 90 and HEIGHT // 2 + 35 < mouse[1] < HEIGHT // 2 + 115:
                        sys.exit()
            if game_state == 1:
                if not piece_falling:
                    piece_falling = True
                    pts = next_pieces[:][0]
                    del next_pieces[0]
                    next_piece = next_pieces[:][0]
                    index = pts[pts > 0][0]
                    game_over = gc.spawn_piece(pts)
                    if game_over:
                        game_state = 2
                    pf = pts[:]
                else:
                    if left_right_pressed:
                        if pg.key.get_pressed()[pg.K_LEFT]:
                            left_right_pressed = False
                            gc.h_move(-1, index)
                        if pg.key.get_pressed()[pg.K_RIGHT]:
                            left_right_pressed = False
                            gc.h_move(1, index)
                    if up_pressed:
                        if pg.key.get_pressed()[pg.K_UP]:
                            up_pressed = False
                            rotated = gc.r_move(pf, index, rotated)
                    if event.type == (pg.USEREVENT + 1) and piece_falling:
                        piece_falling = gc.v_move(index, sm)
                    if move_counter >= gc.FPS // 10:
                        move_counter = 0
                        left_right_pressed = True
                    if rotate_counter >= gc.FPS // 3:
                        rotate_counter = 0
                        up_pressed = True
            if game_state == 0:
                if not theme_playing:
                    theme_playing = True
                    sm.play_sound("theme.wav", 0, -1)
                mui.screen.fill(mui.BLACK)
                mui.draw_main_menu()
            elif game_state == 1:
                gui.screen.fill(gui.BLACK)
                gui.draw_game_ui(gc, next_piece, np.array_equal(next_piece, gc.I))
            else:
                gui.screen.fill(gui.BLACK)
                gui.draw_game_ui(gc, next_piece, np.array_equal(next_piece, gc.I))
                if not game_over_sound_played:
                    game_over_sound_played = gc.game_over(sm)
            pg.display.update()



if __name__ == "__main__":
    main()
