import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import Dense, Conv2D, BatchNormalization, Dropout, Flatten, Input
from Thiam2014 import GameControllerIdea as GameController, TetrisQLearningIdea as Tetris
from time import sleep
import sys
# Configuration paramaters for the whole setup
seed = 42
gamma = 0.95  # Discount factor for past rewards
epsilon = 1.0  # Epsilon greedy parameter
epsilon_min = 0.1  # Minimum epsilon greedy parameter
epsilon_max = 1.0  # Maximum epsilon greedy parameter
epsilon_interval = (
    epsilon_max - epsilon_min
)  # Rate at which to reduce chance of random action being taken

num_actions = 4

ACTIONS = {
    'Nothing': 0,
    'Right': 1,
    'Left': 2,
    'Rotate': 3
}

INPUT_SHAPE = (GameController.BOARD_HEIGHT, GameController.BOARD_WIDTH, 1)

print("Thiam2014")
sleep(1)


def create_q_model():
    # Network defined by the Deepmind paper
    model = keras.models.Sequential()
    model.add(Input(shape=INPUT_SHAPE, dtype="float32"))
    model.add(Conv2D(32, 1, activation="relu"))
    model.add(Conv2D(32, 1, activation="relu"))
    model.add(Conv2D(64, 1, activation="relu"))
    model.add(Conv2D(128, 1, activation="relu"))
    model.add(Conv2D(128, 1, activation="relu"))
    model.add(Flatten())
    model.add(Dropout(0.25))
    model.add(Dense(128, activation="relu"))
    model.add(Dropout(0.25))
    model.add(Dense(512, activation="relu"))
    model.add(Dense(num_actions, activation="linear"))

    return model


# The first model makes the predictions for Q-values which are used to
# make a action.
model = create_q_model()
# Build a target model for the prediction of future rewards.
# The weights of a target model get updated every 10000 steps thus when the
# loss between the Q-values is calculated the target Q-value is stable.
model_target = create_q_model()


# In the Deepmind paper they use RMSProp however then Adam optimizer
# improves training time
optimizer = keras.optimizers.Adam(learning_rate=0.000002, clipnorm=1.0)

# Experience replay buffers
action_history = []
state_history = []
state_next_history = []
rewards_history = []
done_history = []
episode_reward_history = []
running_reward = 0
episode_count = 1
frame_count = 0
# Number of frames to take random action and observe output
epsilon_random_frames = 1_000_000
# Number of frames for exploration
epsilon_greedy_frames = 360_000
# Maximum replay length
# Note: The Deepmind paper suggests 1000000 however this causes memory issues
max_memory_length = 100000
# Train the model after 4 actions
update_after_actions = 4
# How often to update the target network
update_target_network = 10000
# Using huber loss for stability
loss_function = keras.losses.Huber()
env = Tetris.Tetris()
UPDATE_AFTER_EPISODES = 100
BATCH_PERCENTAGE = 0.1
BATCH_EPISODES = int(UPDATE_AFTER_EPISODES * BATCH_PERCENTAGE)
previous_action = 0
total_lines_cleared = 0
e_greedy = 0
while True:  # Run until solved
    state = env.get_state()
    episode_reward = 0
    if episode_count % 10 == 0:
        print("Episode: " + str(episode_count))
        print('Total lines cleared: ' + str(total_lines_cleared))
    done = False
    action_history.append(list())
    state_history.append(list())
    state_next_history.append(list())
    rewards_history.append(list())
    done_history.append(list())

    while not done:
        # Use epsilon-greedy for exploration
        if e_greedy < epsilon_greedy_frames or epsilon > np.random.rand(1)[0]:
            # Take random action
            e_greedy += 1
            action = np.random.choice(num_actions)
        else:
            # Predict action Q-values
            # From environment state
            state_tensor = tf.convert_to_tensor(state)
            state_tensor = tf.expand_dims(state_tensor, 0)
            action_probs = model(state_tensor, training=False)
            # Take best action
            action = tf.argmax(action_probs[0]).numpy()

        # Decay probability of taking random action
        epsilon -= epsilon_interval / epsilon_random_frames
        epsilon = max(epsilon, epsilon_min)

        # Apply the sampled action in our environment
        state_next, reward, done = env.step(action, previous_action)
        state_next = np.array(state_next)

        episode_reward += reward

        # Save actions and states in replay buffer
        action_history[-1].append(action)
        state_history[-1].append(state)
        state_next_history[-1].append(state_next)
        rewards_history[-1].append(reward)
        done_history[-1].append(done)

        #done_history.append(done)
        state = state_next

        previous_action = action_history[-1][-1]

    # Update every fourth frame and once batch size is over 32
    if episode_count % UPDATE_AFTER_EPISODES == 0:

        # Get indices of samples for replay buffers
        indices = np.random.choice(range(len(action_history)), size=BATCH_EPISODES, replace=False)

        state_sample = np.array([np.array(episode_state)
                                .reshape(INPUT_SHAPE) for i in indices for episode_state in state_history[i]])
        print(state_sample.shape)
        #sys.exit()
        state_next_sample = np.array([np.array(episode_next_state)
                                     .reshape(INPUT_SHAPE) for i in indices for episode_next_state in state_history[i]])

        print("Indices:", indices)
        print("Number of sample states:", len(state_sample))

        rewards_sample = [reward for i in indices for reward in rewards_history[i]]
        action_sample = [action for i in indices for action in action_history[i]]
        done_sample = tf.convert_to_tensor(
            [float(history) for i in indices for history in done_history[i]]
        )

        # Build the updated Q-values for the sampled future states
        # Use the target model for stability
        future_rewards = model_target.predict(state_next_sample)
        # Q value = reward + discount factor * expected future reward
        updated_q_values = rewards_sample + gamma * tf.reduce_max(
            future_rewards, axis=1
        )

        # If final frame set the last value to -1
        updated_q_values = updated_q_values * (1 - done_sample) - done_sample

        # Create a mask so we only calculate loss on the updated Q-values
        masks = tf.one_hot(action_sample, num_actions)

        with tf.GradientTape() as tape:
            # Train the model on the states and updated Q-values
            q_values = model(state_sample)

            # Apply the masks to the Q-values to get the Q-value for action taken
            q_action = tf.reduce_sum(tf.multiply(q_values, masks), axis=1)
            # Calculate loss between new Q-value and old Q-value
            loss = loss_function(updated_q_values, q_action)

        # Backpropagation
        grads = tape.gradient(loss, model.trainable_variables)
        optimizer.apply_gradients(zip(grads, model.trainable_variables))

        # update the the target network with new weights
        model_target.set_weights(model.get_weights())
        # Log details
        template = "running reward: {:.2f} at episode {}"
        print(template.format(running_reward, episode_count))

        # Limit the state and reward history
        # if len(rewards_history) > max_memory_length:
        #     del rewards_history[:1]
        #     del state_history[:1]
        #     del state_next_history[:1]
        #     del action_history[:1]
        #     del done_history[:1]

    total_lines_cleared += env.gameController.lines
    env.gameController.state_initializer()
    # Update running reward to check condition for solving
    episode_reward_history.append(episode_reward)
    running_reward = np.mean(episode_reward_history)

    if len(episode_reward_history) == UPDATE_AFTER_EPISODES:
        episode_reward_history.clear()
        action_history.clear()
        state_history.clear()
        state_next_history.clear()
        rewards_history.clear()
        done_history.clear()

    episode_count += 1

    # if running_reward > 40:  # Condition to consider the task solved
    #     print("Solved at episode {}!".format(episode_count))
    #     break
