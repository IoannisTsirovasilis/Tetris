from collections import deque

import numpy as np
from tensorflow import keras
from tensorflow.keras.layers import Dense, Input
from MemoryBased import GameController as GameController, TetrisQLearning as Tetris
from time import sleep
import random
from statistics import mean
import sys

# Configuration paramaters for the whole setup
seed = 42
gamma = 0.95  # Discount factor for past rewards
epsilon = 1.0  # Epsilon greedy parameter
epsilon_min = 0  # Minimum epsilon greedy parameter
epsilon_max = 1.0  # Maximum epsilon greedy parameter
epsilon_interval = (
    epsilon_max - epsilon_min
)  # Rate at which to reduce chance of random action being taken

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

print("MemoryBased")
sleep(1)

def get_best_state(states):
    '''Returns the best state for a given collection of states'''
    max_value = None
    best_state = None

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
        next_qs = [x[0] for x in model.predict(next_states)]

        x = []
        y = []

        # Build xy structure to fit the model in batch (better performance)
        for i, (state, _, reward, done) in enumerate(batch):
            if not done:
                # Partial Q formula
                new_q = reward + gamma * next_qs[i]
            else:
                new_q = reward

            x.append(state)
            y.append(new_q)

        # Fit the model to the given values
        model.fit(np.array(x), np.array(y), batch_size=batch_size, epochs=epochs, verbose=0)


# The first model makes the predictions for Q-values which are used to
# make a action.
model = keras.models.load_model('models/b_1')

print(model.summary())
sleep(2)

episode_count = 1
# Using huber loss for stability
env = Tetris.Tetris()
total_lines_cleared = 0
episode_reward = 0
try:
    while True:  # Run until solved
        done = False
        episode_lines_cleared = 0
        if episode_count % 10 == 0:
            print("Episode: " + str(episode_count))
            print('Total lines cleared: ' + str(total_lines_cleared))
            print('Episode reward: ', )
        episode_reward = 0
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

            reward, done = env.step(best_action)

            episode_reward += reward

            current_state = possible_next_states[best_action]

            if done:
                episode_lines_cleared = env.gameController.lines
                total_lines_cleared += episode_lines_cleared
                env.gameController.state_initializer()
                break

        episode_count += 1
except SystemExit:
    print(0)


