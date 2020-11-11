import pygame as pg
import numpy as np
import sys
import DQN_40_Actions.GraphicsManagerIdea as GraphicsManager
from DQN_40_Actions import GameControllerIdea as GameController
import time

SPEED_MULTIPLIER = 1
WIDTH = 1186
HEIGHT = 964
FPS = 60
INSTANT_DROP_SPEED = 1000 * SPEED_MULTIPLIER

ACTIONS = [(transform, rotation) for transform in range(0 - 5, GameController.BOARD_WIDTH - 5) for rotation in range(4)]

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
        return GameController.BOARD[2:, :]

    def get_reward(self):
        if self.game_over():
            return -1

        reward = (self.gameController.lines - self.gameController.previous_lines) ** 2
        self.gameController.previous_lines = self.gameController.lines

        # holes = self.gameController.number_of_holes()
        # bumpiness = self.gameController.bumpiness()
        # height = self.gameController.height()
        # #empty_columns = self.gameController.empty_columns()
        #
        # reward += -0.51 * height + 0.76 * self.gameController.lines - 0.36 * holes - 0.18 * bumpiness[
        #     0]

        return reward

    def step(self, action):
        reward = 0
        state = None
        dt = self.clock.tick(self.gameController.fps)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
        if self.gameController.game_state == GameController.PLAYING_STATE:
            if len(self.gameController.next_pieces) <= 2:
                self.gameController.create_piece_sequence()
            if not self.gameController.piece_falling:
                self.gameController.piece_falling = True
                pts = self.gameController.next_pieces[:][0]
                del self.gameController.next_pieces[0]
                self.next_piece = self.gameController.next_pieces[:][0]
                game_over = GameController.spawn_piece(pts)
                if game_over:
                    self.gameController.game_state = GameController.GAME_OVER_STATE
                self.pf = pts[:]
            else:
                if action is not None:
                    rotation = ACTIONS[action][1]
                    transform = ACTIONS[action][0]
                    if rotation != 0:
                        for r in range(rotation):
                            self.gameController.rotated = GameController.r_move(self.pf, self.index,
                                                                                self.gameController.rotated)
                            self.update_screen()
                    if transform != 0:
                        for t in range(abs(transform)):
                            direction = int(transform / abs(transform))
                            GameController.h_move(direction, self.index)
                            self.update_screen()
                    return self.step(None)

                if self.gameController.piece_falling:
                    self.gameController.piece_falling = self.gameController.v_move(self.index)
                    self.update_screen()
                    if not self.gameController.piece_falling:
                        #reward += 1
                        state = self.get_state()
                        reward += self.get_reward()
                    else:
                        return self.step(None)
        done = self.game_over()

        if done:
            reward += self.get_reward()
        # This should be decided outside environment
        #if done:
        #    self.gameController.state_initializer()

        # if reward > 0:
        #     print('Reward for this action: ' + str(reward))
        return state, reward, done

    def update_screen(self):
        self.gui.screen.fill(GraphicsManager.BLACK)
        self.gui.draw_game_ui(self.gameController, self.next_piece,
                              np.array_equal(self.next_piece, GameController.I))
        pg.display.update()
