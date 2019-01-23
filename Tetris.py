import pygame as pg
import numpy as np
import sys
from SoundManager import SoundManager
from MainMenuUI import MainMenuUI
from SettingsUI import SettingsUI
from GameUI import GameUI
from GameController import GameController


def main():
    WIDTH = 1186
    HEIGHT = 964
    sm = SoundManager("sounds/")
    pg.init()
    pg.font.init()
    mui = MainMenuUI(WIDTH, HEIGHT)
    sui = SettingsUI(WIDTH, HEIGHT)
    gui = GameUI(WIDTH, HEIGHT)
    gc = GameController(60)
    clock = pg.time.Clock()
    while True:
        dt = clock.tick(gc.FPS)
        gc.drop_counter += dt
        gc.move_counter += dt
        if gc.move_counter >= gc.h_speed:
            gc.can_h_move = True
        if not pg.key.get_pressed()[pg.K_UP]:
            gc.can_rotate = True
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
        if gc.game_state == 0:
            if gc.starting_level != 0:
                gc.starting_level = 0
                gc.set_speed(gc.starting_level)
            if pg.mouse.get_pressed()[0]:
                mouse = pg.mouse.get_pos()
                if WIDTH // 2 - 90 < mouse[0] < WIDTH // 2 + 90 and HEIGHT // 2 - 115 < mouse[1] < HEIGHT // 2 - 35:
                    gc.game_state = 1
                if WIDTH // 2 - 90 < mouse[0] < WIDTH // 2 + 90 and HEIGHT // 2 + 35 < mouse[1] < HEIGHT // 2 + 115:
                    sys.exit()
            if not gc.theme_playing:
                gc.theme_playing = True
                gc.track = "track1.wav"
                sm.play_sound(gc.track, 0, -1)
            mui.draw_main_menu()
        elif gc.game_state == 1:
            if pg.mouse.get_pressed()[0]:
                mouse = pg.mouse.get_pos()
                if WIDTH // 2 - 90 < mouse[0] < WIDTH // 2 + 90 and HEIGHT // 2 + 300 < mouse[1] < HEIGHT // 2 + 380:
                    gc.game_state = 2
                    gc.level = gc.starting_level
                if WIDTH // 2 - 275 < mouse[0] < WIDTH // 2 - 125:
                    for i in range(3):
                        dy = (i+1)*70
                        if HEIGHT // 2 - 148 + dy < mouse[1] < HEIGHT // 2 - 148 + 50 + dy:
                            gc.track = "track" + str(i+1) + ".wav"
                            sm.play_sound(gc.track, 0, -1)
                if WIDTH // 2 + 240 < mouse[0] < WIDTH // 2 + 290:
                    for i in range(5):
                        dy = 50*(i+1)
                        if HEIGHT // 2 - 140 + dy < mouse[1] < HEIGHT // 2 - 140 + 50 + dy:
                            gc.starting_level = 2*i
                            gc.set_speed(gc.starting_level)
                if WIDTH // 2 + 290 < mouse[0] < WIDTH // 2 + 340:
                    for i in range(5):
                        dy = 50*(i+1)
                        if HEIGHT // 2 - 140 + dy < mouse[1] < HEIGHT // 2 - 140 + 50 + dy:
                            gc.starting_level = 2*i+1
                            gc.set_speed(gc.starting_level)
            sui.draw_settings(gc.starting_level)
        elif gc.game_state == 2:
            if len(gc.next_pieces) <= 2:
                gc.create_piece_sequence()
            if not gc.piece_falling:
                gc.piece_falling = True
                pts = gc.next_pieces[:][0]
                del gc.next_pieces[0]
                next_piece = gc.next_pieces[:][0]
                index = pts[pts > 0][0]
                game_over = gc.spawn_piece(pts)
                if game_over:
                    gc.game_state = 3
                pf = pts[:]
            else:
                if pg.key.get_pressed()[pg.K_DOWN]:
                    gc.drop_counter *= 3
                if pg.key.get_pressed()[pg.K_LEFT] and gc.move_counter >= gc.h_speed and gc.can_h_move:
                    gc.can_h_move = False
                    gc.move_counter = 0
                    if gc.h_move(-1, index):
                        sm.play_sound("piece-move.wav", 1, 0)
                if pg.key.get_pressed()[pg.K_RIGHT] and gc.move_counter >= gc.h_speed and gc.can_h_move:
                    gc.can_h_move = False
                    gc.move_counter = 0
                    if gc.h_move(1, index):
                        sm.play_sound("piece-move.wav", 1, 0)
                if pg.key.get_pressed()[pg.K_UP] and gc.can_rotate:
                    gc.can_rotate = False
                    sm.play_sound("piece-rotate.wav", 3, 0)
                    gc.rotated = gc.r_move(pf, index, gc.rotated)
                if gc.drop_counter >= gc.speed and gc.piece_falling:
                    gc.drop_counter = 0
                    gc.piece_falling = gc.v_move(index, sm)
            gui.screen.fill(gui.BLACK)
            gui.draw_game_ui(gc, next_piece, np.array_equal(next_piece, gc.I))
        elif gc.game_state == 3:
            if not gc.game_over_sound_played:
                gc.game_over_sound_played = gc.game_over(sm)
            if pg.key.get_pressed()[pg.K_SPACE]:
                gc.state_initializer(2, gui)
                sm.play_sound(gc.track, 0, -1)
            if pg.key.get_pressed()[pg.K_ESCAPE]:
                gc.state_initializer(0, gui)
                sm.play_sound(gc.track, 0, -1)
        pg.display.update()


if __name__ == "__main__":
    main()
