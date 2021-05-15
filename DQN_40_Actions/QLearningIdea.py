import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import Dense, Conv2D, BatchNormalization, Dropout, Flatten, Input
from DQN_40_Actions import GameControllerIdea as GameController, TetrisQLearningIdea as Tetris
from time import sleep
import sys

# Configuration paramaters for the whole setup
seed = 42
gamma = 0.9  # Discount factor for past rewards
epsilon = 1.0  # Epsilon greedy parameter
epsilon_min = 0.1  # Minimum epsilon greedy parameter
epsilon_max = 1.0  # Maximum epsilon greedy parameter
epsilon_interval = (
    epsilon_max - epsilon_min
)  # Rate at which to reduce chance of random action being taken
batch_size = 32  # Size of batch taken from replay buffer
max_steps_per_episode = 10000

num_actions = 40

ACTIONS = [(transform, rotation) for transform in range(0 - 5, GameController.BOARD_WIDTH - 5) for rotation in range(4)]

INPUT_SHAPE = (GameController.BOARD_HEIGHT - 2, GameController.BOARD_WIDTH, 1)

print("40 Actions")
sleep(1)


def create_q_model():
    # Network defined by the Deepmind paper
    model = keras.models.Sequential()
    model.add(Input(shape=INPUT_SHAPE, dtype="float32"))
    model.add(Conv2D(32, 5, strides=(1, 1), activation="relu"))
    model.add(Conv2D(64, 3, strides=(1, 1), activation="relu"))
    model.add(Conv2D(64, 3, strides=(1, 1), activation="relu"))
    model.add(Flatten())
    model.add(Dense(512, activation="relu"))
    model.add(Dense(len(ACTIONS), activation="softmax"))

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
optimizer = keras.optimizers.Adam(learning_rate=0.000025, clipnorm=1.0)

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
epsilon_random_frames = 50000
# Number of frames for exploration
epsilon_greedy_frames = 1000000.0
# Maximum replay length
# Note: The Deepmind paper suggests 1000000 however this causes memory issues
max_memory_length = 100000
# Train the model after 4 actions
update_after_actions = 4
# How often to update the target network
update_target_network = 10_000
# Using huber loss for stability
loss_function = keras.losses.Huber()
env = Tetris.Tetris()
total_lines_cleared = 0
action_count = 0
APPROACH = 'DQN_40_Actions'
TAG = 3
with open('{}/reports/report_{}.csv'.format(APPROACH, TAG), 'w') as f:
    print('Created')
try:
    while True:  # Run until solved
        episode_reward = 0
        episde_lines_cleared = 0
        if episode_count % 10 == 0:
            print("Episode: " + str(episode_count))
            print('Total lines cleared: ' + str(total_lines_cleared))
        for timestep in range(1, max_steps_per_episode):
            env.step(None)
            state = env.get_state()
            # env.render(); Adding this line would show the attempts
            # of the agent in a pop up window.
            frame_count += 1

            # Use epsilon-greedy for exploration
            if action_count < epsilon_random_frames or epsilon > np.random.rand(1)[0]:
                # Take random action
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
            epsilon -= epsilon_interval / epsilon_greedy_frames
            epsilon = max(epsilon, epsilon_min)

            # Apply the sampled action in our environment
            state_next, reward, done = env.step(action)

            if state_next is None and not done:
                continue

            if done:
                episde_lines_cleared = env.gameController.lines
                total_lines_cleared += episde_lines_cleared
                env.gameController.state_initializer()
                break

            action_count += 1
            state_next = np.array(state_next)

            episode_reward += reward

            # Save actions and states in replay buffer
            action_history.append(action)
            state_history.append(state)
            state_next_history.append(state_next)
            done_history.append(done)
            rewards_history.append(reward)
            state = state_next

            # Update every fourth frame and once batch size is over 32
            if action_count % update_after_actions == 0 and len(done_history) > batch_size:

                # Get indices of samples for replay buffers
                indices = np.random.choice(range(len(done_history)), size=batch_size)

                # Using list comprehension to sample from replay buffer
                state_sample = np.array([np.array(state_history[i]).reshape(INPUT_SHAPE) for i in indices])
                state_next_sample = np.array([np.array(state_next_history[i]).reshape(INPUT_SHAPE) for i in indices])
                rewards_sample = [rewards_history[i] for i in indices]
                action_sample = [action_history[i] for i in indices]
                done_sample = tf.convert_to_tensor(
                    [float(done_history[i]) for i in indices]
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
                    print(q_values)
                    exit()

                    # Apply the masks to the Q-values to get the Q-value for action taken
                    q_action = tf.reduce_sum(tf.multiply(q_values, masks), axis=1)
                    # Calculate loss between new Q-value and old Q-value
                    loss = loss_function(updated_q_values, q_action)

                # Backpropagation
                grads = tape.gradient(loss, model.trainable_variables)
                optimizer.apply_gradients(zip(grads, model.trainable_variables))

            # Limit the state and reward history
            if len(rewards_history) > max_memory_length:
                del rewards_history[:1]
                del state_history[:1]
                del state_next_history[:1]
                del action_history[:1]
                del done_history[:1]

            if action_count % update_target_network == 0:
                # update the the target network with new weights
                model_target.set_weights(model.get_weights())
                # Log details
                template = "running reward: {:.2f} at episode {}, frame count {}"
                print(template.format(running_reward, episode_count, frame_count))

        # Update running reward to check condition for solving
        with open('{}/reports/report_{}.csv'.format(APPROACH, TAG), 'a') as f:
            f.write('{},{}\n'.format(episode_count, episde_lines_cleared))
        episode_reward_history.append(episode_reward)
        if len(episode_reward_history) > 100:
            del episode_reward_history[:1]
        running_reward = np.mean(episode_reward_history)

        episode_count += 1

        # if running_reward > 40:  # Condition to consider the task solved
        #     print("Solved at episode {}!".format(episode_count))
        #     break
except:
    model.save('{}/models/_{}'.format(APPROACH, TAG))
    model_target.save('{}/models/target_{}'.format(APPROACH, TAG))