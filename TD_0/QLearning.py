from collections import deque

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import Dense, Conv2D, BatchNormalization, Dropout, Flatten, Input
from TD_0 import GameController as GameController, TetrisQLearning as Tetris
from time import sleep
import random
from statistics import mean
import sys

# Configuration paramaters for the whole setup
seed = 42
gamma = 0.95  # Discount factor for past rewards
epsilon = 1.0  # Epsilon greedy parameter
epsilon_min = 0  # Minimum epsilon greedy parameter

epsilon_stop_steps = 10_000
epsilon_decay = (epsilon - epsilon_min) / epsilon_stop_steps
log_every = 50
max_steps_per_episode = 1_000_000
mem_size = 10
memory = deque(maxlen=mem_size)
ACTIONS = [(transform, rotation) for transform in range(0 - 5, GameController.BOARD_WIDTH - 5) for rotation in range(4)]

INPUT_SHAPE = 4

print("SARSA")
sleep(1)


def create_q_model():
    # Network defined by the Deepmind paper
    model = keras.models.Sequential()
    model.add(Input(shape=INPUT_SHAPE, dtype="float32"))
    model.add(Dense(32, activation="relu"))
    model.add(Dense(32, activation="relu"))
    model.add(Dense(1, activation="linear"))
    model.compile(loss='mse', optimizer='adam')
    return model


def get_best_state(states):
    '''Returns the best state for a given collection of states'''
    max_value = None
    best_state = None

    if epsilon >= np.random.rand(1)[0]:
        # Take random action
        return random.choice(list(states))
    else:
        for s in states:
            value = predict_value(np.reshape(s, [1, INPUT_SHAPE]))
            if not max_value or value > max_value:
                max_value = value
                best_state = s

    return best_state


def predict_value(state):
    """Predicts the score for a certain state"""
    return model.predict(state)


def add_to_memory(current_state, next_state, reward, done):
    """Adds a play to the replay memory buffer"""
    memory.append((current_state, next_state, reward, done))


def train(state, next_state, reward, done):
    """Trains the agent"""

    qs = model.predict(np.reshape(state, [1, INPUT_SHAPE]))[0]
    next_qs = model.predict(np.reshape(next_state, [1, INPUT_SHAPE]))[0]

    if not done:
        new_q = reward + gamma * next_qs - qs
    else:
        new_q = reward

    x = [state]
    y = [new_q]

    # Fit the model to the given values
    model.fit(np.array(x), np.array(y), batch_size=1, epochs=1, verbose=0)


# The first model makes the predictions for Q-values which are used to
# make a action.
model = create_q_model()

# Experience replay buffers
episode_reward_history = []
episode_count = 1

env = Tetris.Tetris()
total_lines_cleared = 0
action_count = 0
APPROACH = 'TD_0'
TAG = 1

singles = []
doubles = []
triples = []
tetrises = []

with open('{}/reports/report_{}.csv'.format(APPROACH, TAG), 'w') as f:
    print('Created')
    f.write('Episode,Single,Double,Triple,Tetris,Total,Score\n')
try:
    while True:  # Run until solved
        episode_reward = 0
        single = 0
        double = 0
        triple = 0
        tetris = 0
        episode_lines_cleared = 0
        if episode_count % 10 == 0:
            print("Episode: " + str(episode_count))
            print('Total lines cleared: ' + str(total_lines_cleared))
        env.step(None)
        current_state = env.get_state(False)
        possible_next_states = env.get_next_states()
        best_state = get_best_state(possible_next_states.values())
        best_action = None
        for action, state in possible_next_states.items():
            if state == best_state:
                best_action = action
                break
        for timestep in range(1, max_steps_per_episode):

            if best_state[0] == 4:
                tetris += 1
            elif best_state[0] == 3:
                triple += 1
            elif best_state[0] == 2:
                double += 1
            elif best_state[0] == 1:
                single += 1

            reward, done = env.step(best_action)

            action_count += 1

            episode_reward += reward

            add_to_memory(current_state, possible_next_states[best_action], reward, done)

            env.step(None)
            next_state = env.get_state(False)
            possible_next_states = env.get_next_states()
            best_state = get_best_state(possible_next_states.values())
            best_action = None
            for action, state in possible_next_states.items():
                if state == best_state:
                    best_action = action
                    break

            train(current_state, next_state, reward, done)
            current_state = next_state
            if epsilon > epsilon_min:
                epsilon -= epsilon_decay
            if done:
                episode_lines_cleared = env.gameController.lines
                total_lines_cleared += episode_lines_cleared
                env.gameController.state_initializer()
                break

        episode_reward_history.append(episode_reward)
        singles.append(single)
        doubles.append(double)
        triples.append(triple)
        tetrises.append(tetris)
        # Update every fourth frame and once batch size is over 32


        # Logs
        if log_every and episode_count and episode_count % log_every == 0:
            avg_score = mean(episode_reward_history[-log_every:])
            min_score = min(episode_reward_history[-log_every:])
            max_score = max(episode_reward_history[-log_every:])
            avg_singles = mean(singles[-log_every:])
            avg_doubles = mean(doubles[-log_every:])
            avg_triples = mean(triples[-log_every:])
            avg_tetrises = mean(tetrises[-log_every:])
            avg_total = mean(singles[-log_every:]) + 2 * mean(doubles[-log_every:]) \
                        + 3 * mean(triples[-log_every:]) + 4 * mean(tetrises[-log_every:])

            # Update running reward to check condition for solving
            with open('{}/reports/report_{}.csv'.format(APPROACH, TAG), 'a') as f:
                f.write('{},{},{},{},{},{},{}\n'.format(episode_count, avg_singles,
                                                        avg_doubles, avg_triples,
                                                        avg_tetrises, avg_total, avg_score))
        episode_count += 1
except SystemExit:
    model.save('{}/models/_{}'.format(APPROACH, TAG))

