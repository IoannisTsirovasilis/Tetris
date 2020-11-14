import pygame as pg
import numpy as np
import sys
import nlinker.GraphicsManagerIdea as GraphicsManager
from nlinker import GameControllerIdea as GameController
import time

SPEED_MULTIPLIER = 1000000
WIDTH = 1186
HEIGHT = 964
FPS = 60
INSTANT_DROP_SPEED = 1000 * SPEED_MULTIPLIER

ACTIONS = [(transform, rotation) for transform in range(0 - 5, GameController.BOARD_WIDTH - 5) for rotation in range(4)]

DEBUG_ACTIONS = ['Nothing', 'Right', 'Left', 'Rotate']

PIECE_ACTIONS = {
    0: { # O
        0: [-4, 4]
    },
    1: { # S
        0: [-4, 3],
        1: [-5, 3]
    },
    2: { # Z
        0: [-4, 3],
        1: [-5, 3]
    },
    3: { # T
        0: [-4, 3],
        1: [-5, 3],
        2: [-4, 3],
        3: [-5, 3]
    },
    4: { # I
        0: [-3, 3],
        1: [-4, 5]
    },
    5: { # L
        0: [-4, 3],
        1: [-5, 3],
        2: [-4, 3],
        3: [-5, 3]
    },
    6: { # J
        0: [-4, 3],
        1: [-5, 3],
        2: [-4, 3],
        3: [-5, 3]
    }
}


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

    def get_state(self, is_simulation):
        try:
            if is_simulation:
                lines = self.gameController.simulation_lines_to_erase
                return [lines,
                        self.gameController.number_of_holes(GameController.SIMULATE_BOARD),
                        self.gameController.bumpiness(GameController.SIMULATE_BOARD)[0],
                        self.gameController.height(GameController.SIMULATE_BOARD)]
            lines = self.gameController.previous_lines - self.gameController.lines
            return [lines,
                    self.gameController.number_of_holes(GameController.BOARD),
                    self.gameController.bumpiness(GameController.BOARD)[0],
                    self.gameController.height(GameController.BOARD)]
        except BaseException as e:
            print(e)

    def get_reward(self):
        reward = 1 + (self.gameController.lines - self.gameController.previous_lines) ** 2 * GameController.BOARD_WIDTH

        self.gameController.previous_lines = self.gameController.lines

        if self.game_over():
            reward -= 2

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
                self.gameController.current_piece = self.gameController.next_pieces[:][0]
                del self.gameController.next_pieces[0]
                self.next_piece = self.gameController.next_pieces[:][0]
                game_over = GameController.spawn_piece(self.gameController.current_piece)
                if game_over:
                    self.gameController.game_state = GameController.GAME_OVER_STATE
                self.pf = self.gameController.current_piece[:]
            else:
                if action is not None:
                    rotation = action[1]
                    transform = action[0]
                    if rotation != 0:
                        for r in range(rotation):
                            self.gameController.rotated = GameController.r_move(self.pf, self.index,
                                                                                self.gameController.rotated,
                                                                                GameController.BOARD,
                                                                                GameController.PIVOT,
                                                                                False)
                            self.update_screen()
                    if transform != 0:
                        for t in range(abs(transform)):
                            direction = int(transform / abs(transform))
                            GameController.h_move(direction, self.index, GameController.BOARD,
                                                  GameController.PIVOT, False)
                            self.update_screen()
                    #self.update_screen()
                    return self.step(None)

                if self.gameController.piece_falling:
                    self.gameController.piece_falling = self.gameController.v_move(self.index, GameController.BOARD,
                                                                                   GameController.PIVOT, False)
                    self.update_screen()
                    if not self.gameController.piece_falling:
                        reward += 1
                        reward += self.get_reward()
                    else:
                        return self.step(None)
        done = self.game_over()

        if done:
            reward += self.get_reward()

        return reward, done

    def get_next_states(self):
        '''Get all possible next states'''
        states = {}
        piece = self.gameController.current_piece
        piece_id = GameController.get_piece_id(piece)
        if piece_id == 0:
            rotations = [0]
        elif piece_id in [1, 2, 4]:
            rotations = [0, 1]
        else:
            rotations = [0, 1, 2, 3]

        action = [0, 0]
        # For all rotations
        for rotation in rotations:
            actions = PIECE_ACTIONS[piece_id][rotation]

            # For all positions
            for x in range(actions[0], actions[1] + 1):
                action[0] = x
                action[1] = rotation

                states[(action[0], action[1])] = self.simulate_step(action, True)

        return states

    def simulate_step(self, action, piece_falling):
        if action is not None:
            GameController.copy_env_to_simulation()
            rotation = action[1]
            transform = action[0]
            if rotation != 0:
                for r in range(rotation):
                    GameController.r_move(self.pf, self.index, False, GameController.SIMULATE_BOARD,
                                          GameController.SIMULATE_PIVOT, True)
            if transform != 0:
                for t in range(abs(transform)):
                    direction = int(transform / abs(transform))
                    GameController.h_move(direction, self.index, GameController.SIMULATE_BOARD,
                                          GameController.SIMULATE_PIVOT, True)
            return self.simulate_step(None, piece_falling)

        piece_falling = self.gameController.v_move(self.index, GameController.SIMULATE_BOARD,
                                                   GameController.SIMULATE_PIVOT, True)

        if not piece_falling:
            state = self.get_state(True)
        else:
            return self.simulate_step(None, piece_falling)

        return state

    def update_screen(self):
        self.gui.screen.fill(GraphicsManager.BLACK)
        self.gui.draw_game_ui(self.gameController, self.next_piece,
                              np.array_equal(self.next_piece, GameController.I))
        pg.display.update()
