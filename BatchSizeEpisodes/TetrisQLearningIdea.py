import pygame as pg
import numpy as np
import sys
import BatchSizeEpisodes.GraphicsManagerIdea as GraphicsManager
from BatchSizeEpisodes import GameControllerIdea as GameController
import time

SPEED_MULTIPLIER = 10000000
WIDTH = 1186
HEIGHT = 964
FPS = 200
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
        self.index = GameController.MAP_BLOCK_FALLING
        self.pf = None
        self.next_piece = None

    def game_over(self):
        return self.gameController.game_state == GameController.GAME_OVER_STATE

    def get_state(self):
        return GameController.BOARD

    def get_reward(self):
        if self.game_over():
            return -1

        reward = (self.gameController.lines - self.gameController.previous_lines) ** 2 + 4
        self.gameController.previous_lines = self.gameController.lines

        holes = self.gameController.number_of_holes()
        bumpiness = self.gameController.bumpiness()
        height = self.gameController.height()
        #empty_columns = self.gameController.empty_columns()

        reward += -0.51 * height + 0.76 * self.gameController.lines - 0.36 * holes - 0.18 * bumpiness[
            0]

        return reward

    def step(self, action, previous_action):
        reward = 0
        state = None
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
                self.gameController.rotated = False
                self.gameController.piece_falling = True
                pts = self.gameController.next_pieces[:][0]
                del self.gameController.next_pieces[0]
                self.next_piece = self.gameController.next_pieces[:][0]
                game_over = GameController.spawn_piece(pts)
                if game_over:
                    self.gameController.game_state = GameController.GAME_OVER_STATE
                self.pf = pts[:]
            else:
                if action == ACTIONS['Left'] and self.gameController.move_counter >= GameController.H_SPEED and self.gameController.can_h_move:
                    self.gameController.can_h_move = False
                    self.gameController.move_counter = 0
                    moved = GameController.h_move(-1, self.index)
                if action == ACTIONS['Right'] and self.gameController.move_counter >= GameController.H_SPEED and self.gameController.can_h_move:
                    self.gameController.can_h_move = False
                    self.gameController.move_counter = 0
                    moved = GameController.h_move(1, self.index)
                if action == ACTIONS['Rotate'] and self.gameController.can_rotate:
                    self.gameController.can_rotate = False
                    rotated = self.gameController.rotated = GameController.r_move(self.pf, self.index, self.gameController.rotated)
                if self.gameController.drop_counter >= self.gameController.speed and self.gameController.piece_falling:
                    self.gameController.drop_counter = 0
                    self.gameController.piece_falling = self.gameController.v_move(self.index)
                    if not self.gameController.piece_falling:
                        state = self.get_state()
                        reward += self.get_reward()
            self.gui.screen.fill(GraphicsManager.BLACK)
            self.gui.draw_game_ui(self.gameController, self.next_piece, np.array_equal(self.next_piece, GameController.I))
        pg.display.update()
        done = self.game_over()
        # This should be decided outside environment
        #if done:
        #    self.gameController.state_initializer()

        # if reward > 0:
        #     print('Reward for this action: ' + str(reward))
        return state, reward, done
