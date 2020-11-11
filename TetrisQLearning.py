import pygame as pg
import numpy as np
import sys
import GraphicsManager
import GameController
import time

SPEED_MULTIPLIER = 10000000
WIDTH = 1186
HEIGHT = 964
FPS = 60
INSTANT_DROP_SPEED = 1000 * SPEED_MULTIPLIER
ACTIONS = {
    'Nothing': 0,
    'Right': 1,
    'Left': 2,
    'Rotate': 3
}

DEBUG_ACTIONS = ['Nothing', 'Right', 'Left', 'Rotate']


class Tetris:
    def __init__(self):
        pg.init()
        pg.font.init()
        self.gui = GraphicsManager.GraphicsManager(WIDTH, HEIGHT)
        self.gameController = GameController.GameController(FPS)
        self.clock = pg.time.Clock()
        self.previous_score = self.gameController.score
        self.index = 0
        self.pf = None
        self.next_piece = None

    def game_over(self):
        return self.gameController.game_state == GameController.GAME_OVER_STATE

    def get_state(self):
        return GameController.BOARD[2:, :]

    def get_reward(self):
        if self.game_over():
            return -1

        reward = (self.gameController.lines - self.gameController.previous_lines) ** 2
        self.gameController.previous_lines = self.gameController.lines

        self.previous_score = self.gameController.score

        holes = self.gameController.number_of_holes()
        bumpiness = self.gameController.bumpiness()
        height = self.gameController.height()
        empty_columns = self.gameController.empty_columns()

        reward += -0.51 * height + 0.76 * self.gameController.lines - 0.36 * holes - 0.18 * bumpiness[0]
        reward -= 0.8 * empty_columns
        return reward

    def step(self, action):
        print(GameController.BOARD)
        time.sleep(0.1)
        reward = 0
        dt = self.clock.tick(self.gameController.fps)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
        if self.gameController.game_state == GameController.PLAYING_STATE:
            self.gameController.drop_counter += dt * SPEED_MULTIPLIER
            self.gameController.move_counter += dt * SPEED_MULTIPLIER
            # Delay between player's side movement
            if self.gameController.move_counter >= GameController.H_SPEED:
                self.gameController.can_h_move = True
            if not pg.key.get_pressed()[pg.K_UP]:
                self.gameController.can_rotate = True
            if len(self.gameController.next_pieces) <= 2:
                self.gameController.create_piece_sequence()
            if not self.gameController.piece_falling:
                #reward += 1
                self.gameController.rotated = False
                self.gameController.piece_falling = True
                pts = self.gameController.next_pieces[:][0]
                del self.gameController.next_pieces[0]
                self.next_piece = self.gameController.next_pieces[:][0]
                self.index = pts[pts > 0][0]
                game_over = GameController.spawn_piece(pts)
                if game_over:
                    self.gameController.game_state = GameController.GAME_OVER_STATE
                self.pf = pts[:]
            else:
                #print('Action taken: ' + DEBUG_ACTIONS[action])
                if action == ACTIONS['Left'] and self.gameController.move_counter >= GameController.H_SPEED and self.gameController.can_h_move:
                    self.gameController.can_h_move = False
                    self.gameController.move_counter = 0
                    moved = GameController.h_move(-1, self.index)
                    if not moved:
                        reward -= 0.05
                if action == ACTIONS['Right'] and self.gameController.move_counter >= GameController.H_SPEED and self.gameController.can_h_move:
                    self.gameController.can_h_move = False
                    self.gameController.move_counter = 0
                    moved = GameController.h_move(1, self.index)
                    if not moved:
                        reward -= 0.05
                if action == ACTIONS['Rotate'] and self.gameController.can_rotate:
                    self.gameController.can_rotate = False
                    rotated = self.gameController.rotated = GameController.r_move(self.pf, self.index, self.gameController.rotated)
                    if not rotated:
                        reward -= 0.05
                if self.gameController.drop_counter >= self.gameController.speed and self.gameController.piece_falling:
                    self.gameController.drop_counter = 0
                    self.gameController.piece_falling = self.gameController.v_move(self.index)
            self.gui.screen.fill(GraphicsManager.BLACK)
            self.gui.draw_game_ui(self.gameController, self.next_piece, np.array_equal(self.next_piece, GameController.I))
        pg.display.update()
        reward += self.get_reward()
        state = self.get_state()
        done = self.game_over()
        if done:
            self.gameController.state_initializer()
        # if reward > 0:
        #     print('Reward for this action: ' + str(reward))
        return state, reward, done


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
