import pygame as pg
import numpy as np
import sys
import GraphicsManager
import GameController

WIDTH = 1186
HEIGHT = 964
FPS = 60
INSTANT_DROP_SPEED = 1000


def main():
    pg.init()
    pg.font.init()
    gui = GraphicsManager.GraphicsManager(WIDTH, HEIGHT)
    gc = GameController.GameController(FPS)
    clock = pg.time.Clock()
    while True:
        # The time it takes for a frame to complete. It is used to make the game frame independent.
        dt = clock.tick(gc.fps)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
        if gc.game_state == GameController.PLAYING_STATE:
            gc.drop_counter += dt
            gc.move_counter += dt
            # Delay between player's side movement
            if gc.move_counter >= GameController.H_SPEED:
                gc.can_h_move = True
            if not pg.key.get_pressed()[pg.K_UP]:
                gc.can_rotate = True
            if len(gc.next_pieces) <= 2:
                gc.create_piece_sequence()
            if not gc.piece_falling:
                gc.rotated = False
                gc.piece_falling = True
                pts = gc.next_pieces[:][0]
                del gc.next_pieces[0]
                next_piece = gc.next_pieces[:][0]
                index = pts[pts > 0][0]
                game_over = GameController.spawn_piece(pts)
                if game_over:
                    gc.game_state = GameController.GAME_OVER_STATE
                pf = pts[:]
            else:
                if pg.key.get_pressed()[pg.K_DOWN]:
                    # THIS SHOULD BE CHANGED
                    gc.drop_counter = INSTANT_DROP_SPEED
                if pg.key.get_pressed()[pg.K_LEFT] and gc.move_counter >= GameController.H_SPEED and gc.can_h_move:
                    gc.can_h_move = False
                    gc.move_counter = 0
                    GameController.h_move(-1, index)
                if pg.key.get_pressed()[pg.K_RIGHT] and gc.move_counter >= GameController.H_SPEED and gc.can_h_move:
                    gc.can_h_move = False
                    gc.move_counter = 0
                    GameController.h_move(1, index)
                if pg.key.get_pressed()[pg.K_UP] and gc.can_rotate:
                    gc.can_rotate = False
                    gc.rotated = GameController.r_move(pf, index, gc.rotated)
                if gc.drop_counter >= gc.speed and gc.piece_falling:
                    gc.drop_counter = 0
                    gc.piece_falling = gc.v_move(index)
            gui.screen.fill(GraphicsManager.BLACK)
            gui.draw_game_ui(gc, next_piece, np.array_equal(next_piece, GameController.I))
        else:
            gc.state_initializer()
        pg.display.update()


if __name__ == "__main__":
    main()
