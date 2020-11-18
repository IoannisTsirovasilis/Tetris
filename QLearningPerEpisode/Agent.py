from collections import deque

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import Dense, Conv2D, BatchNormalization, Dropout, Flatten, Input
from nlinker import GameController as GameController, TetrisQLearning as Tetris
from time import sleep
import random
from statistics import mean
import sys

# Configuration paramaters for the whole setup
seed = 42
gamma = 0.95  # Discount factor for past rewards
epsilon = 1.0  # Epsilon greedy parameter
epsilon_min = 0  # Minimum epsilon greedy parameter
epsilon_stop_episode = 1500
epsilon_decay = (epsilon - epsilon_min) / epsilon_stop_episode
log_every = 50
batch_size = 512
epochs = 1
mem_size = 20_000
memory = deque(maxlen=mem_size)
replay_start_size = 2000
ACTIONS = [(transform, rotation) for transform in range(0 - 5, GameController.BOARD_WIDTH - 5) for rotation in range(4)]

INPUT_SHAPE = 4

print("QlearningPerEpisode")
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


def train(batch_size=32, epochs=3):
    """Trains the agent"""
    n = len(memory)

    if n >= replay_start_size and n >= batch_size:

        batch = random.sample(memory, batch_size)

        # Get the expected score for the next states, in batch (better performance)
        next_states = np.array([x[1] for x in batch])
        states = np.array([x[0] for x in batch])
        qs = [x[0] for x in model.predict(states)]
        next_qs = [x[0] for x in model.predict(next_states)]

        x = []
        y = []

        # Build xy structure to fit the model in batch (better performance)
        for i, (state, _, reward, done) in enumerate(batch):
            if not done:
                # Partial Q formula
                new_q = reward + gamma * next_qs[i] - qs[i]
            else:
                new_q = reward

            x.append(state)
            y.append(new_q)

        # Fit the model to the given values
        model.fit(np.array(x), np.array(y), batch_size=batch_size, epochs=epochs, verbose=0)


# The first model makes the predictions for Q-values which are used to
# make a action.
model = create_q_model()

# Experience replay buffers
episode_reward_history = []
running_reward = 0
episode_count = 1

env = Tetris.Tetris()
total_lines_cleared = 0
action_count = 0
TAG = 1
update_after_episodes = 1

singles = []
doubles = []
triples = []
tetrises = []

with open('reports/report_{}.csv'.format(TAG), 'w') as f:
    print('Created')
    f.write('Episode,Single,Double,Triple,Tetris,Total,Score\n')
try:
    while True:  # Run until solved
        done = False
        episode_reward = 0
        single = 0
        double = 0
        triple = 0
        tetris = 0
        episode_lines_cleared = 0
        if episode_count % 10 == 0:
            print("Episode: " + str(episode_count))
            print('Total lines cleared: ' + str(total_lines_cleared))
        while not done:
            env.step(None)
            current_state = env.get_state(False)
            possible_next_states = env.get_next_states()
            best_state = get_best_state(possible_next_states.values())

            best_action = None
            for action, state in possible_next_states.items():
                if state == best_state:
                    best_action = action
                    break
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

            current_state = possible_next_states[best_action]

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
        if episode_count % update_after_episodes == 0:
            train(batch_size, epochs)

            if epsilon > epsilon_min:
                epsilon -= epsilon_decay

        # Logs
        if log_every and episode_count and episode_count % log_every == 0:
            avg_score = mean(episode_reward_history[-log_every:])
            min_score = min(episode_reward_history[-log_every:])
            max_score = max(episode_reward_history[-log_every:])
            avg_singles = mean(singles[-log_every:])
            avg_doubles = mean(doubles[-log_every:])
            avg_triples = mean(triples[-log_every:])
            avg_tetrises = mean(tetrises[-log_every:])
            avg_total = mean(singles[-log_every:] + 2 * doubles[-log_every:]
                             + 3 * triples[-log_every:] + 4 * tetrises[-log_every:])

            # Update running reward to check condition for solving
            with open('reports/report_{}.csv'.format(TAG), 'a') as f:
                f.write('{},{},{},{},{},{},{}\n'.format(episode_count, avg_singles,
                                                        avg_doubles, avg_triples,
                                                        avg_tetrises, avg_total, avg_score))
        episode_count += 1
except:
    model.save('models/_{}'.format(TAG))


