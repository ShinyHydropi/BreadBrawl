# Based on the DQN demonstrated in https://www.youtube.com/watch?v=NP8pXZdU-5U

import torch
import torch.nn as nn
import numpy as np
from collections import deque
import random

from breadbrawl import BreadBrawl, Loaf, Attack
from tqdm import tqdm

GAMMA = 0.99
BATCH_SIZE = 32
BUFFER_SIZE = 5000
MIN_REPLAY_SIZE = 100
EPSILON_START = 1.0
EPSILON_END = 0.02
EPSILON_DECAY = 1000
TARGET_UPDATE_FREQUENCY = 100
STEPS = 10000

class DQNetwork(nn.Module):
    def __init__(self, loaf, state_dim, n_actions, hidden=128):
        """
        DQNetwork is a Neural Network with four fully-connected layers and uses ReLU as the activation function
        for the middle layers (https://docs.pytorch.org/docs/2.12/generated/torch.nn.ReLU.html). nn.sequential
        is used to string together the inputs and outputs of each layer into one function that is the network.
        """
        super().__init__()
        self.loaf = loaf
        self.net = nn.Sequential(
            nn.Linear(state_dim, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, n_actions),
        )

    def forward(self, x):
        """
        forward(x) performs a forward pass through the network and returns the networks estimate of the Q-value
        for each action at the current state.
        """
        return self.net(x)

    def select_action(self, state):
        """
        select_action(state) is a helper function for forward(x) that takes a state and returns the action that
        a greedy policy would select. Essentially, it selects the action with the highest expected returns
        (Q-value).
        """
        state_t = torch.as_tensor(state, dtype=torch.float32)
        q_values = self.net(state_t)
        max_q = torch.argmax(q_values)
        action = self.loaf.action_space[max_q.item()]

        return action

if __name__ == "__main__":
    # Delete the following line
    your_loaf = Loaf.random_loaf()

    # Uncomment the following line and create your own Loaf with the Loaf constructor in breadbrawl.py
    # your_loaf = Loaf()

    # Example:
    # your_loaf = Loaf(flour=2, salt=3, sugar=1, attacks=[Attack.CRUST_CRUSHER, Attack.OVEN_SPRING, Attack.GLUTEN_SURGE, Attack.INSTANT_YEAST])

    """
    Some more objects we will need:
    env - The environment our agent is interacting with in order to train (in this case BreadBrawl)
    replay_buffer - This will store the 50,000 most recent episodes so we can collect many episodes before each
        iteration of improving our agent (This also lets us use past training data while discarding the data that
        is too old)
    reward_buffer - This keeps track of how well the agent is doing
    """
    env = BreadBrawl.training_env(your_loaf)
    replay_buffer = deque(maxlen=BUFFER_SIZE)
    reward_buffer = deque([0.0], maxlen=100)

    """
    With Deep-Q learning, we will use two networks, one to update every episode that represents our current best
    estimate of the Q-function, and one to keep fixed for many episodes at a time. This fixed network is used
    during policy evaluation as a stationary target for approximating the value of the next state.
    """
    online_net = DQNetwork(your_loaf, 10, len(your_loaf.action_space))
    target_net = DQNetwork(your_loaf, 10, len(your_loaf.action_space))
    target_net.load_state_dict(online_net.state_dict())

    """
    Optimizers in Pytorch handle network updates for us. Adam is very common and uses an adaptive learning rate.
    """
    optimizer = torch.optim.Adam(online_net.parameters(), lr=5e-4)

    """
    In this section, 1000 steps are played with the agent selecting only random actions. These episodes are used
    to fill the replay buffer with many episodes to sample from. Otherwise, we would be sampling the same early
    episodes many times.
    """
    obs = env.reset()
    for _ in range(MIN_REPLAY_SIZE):
        action = your_loaf.random_attack()
        next_obs, _, done, reward = env.step_1p(action)
        action = your_loaf.action_space.index(action)
        transition = (obs, action, done, reward, next_obs)
        replay_buffer.append(transition)
        obs = next_obs

        if done:
            obs = env.reset()

    """
    Below is where the actual training happens. Here are some important functions:
    env.reset() - Resets the environment for the next episode
    env.step_1p(action) - Changes the environment by the action the agent chose (The 1p means only one agent is
        selecting an action)
    your_loaf.action_space - Returns a list of all the attacks your_loaf can use
    """
    episode_reward = 0.0
    obs = env.reset()
    for step in tqdm(range(STEPS)):
        """
        At the beginning of each step (in this environment one step is one turn of the battle), the agent selects
        an action to take. In order to ensure we have a comprehensive approximation of our Q-function, the agent
        must explore many states. Once we have a better approximation of our Q-function, it is more important
        for the agent to visit actions that it knows are more valuable. To balance this tradeoff, our agent will
        select random actions with a probability epsilon (otherwise it selects the action with the highest value).
        Throughout our training epsilon will decay from 1.00 to 0.02.
        """
        epsilon = np.interp(step, [0, EPSILON_DECAY], [EPSILON_START, EPSILON_END])
        if random.random() <= epsilon:
            action = your_loaf.random_attack()
        else:
            action = online_net.select_action(obs)

        """
        Steps will continue to be added to the replay buffer. Once the buffer exceeds 50,000 steps the oldest ones
        are discarded.
        """
        next_obs, _, done, reward = env.step_1p(action)
        transition = (obs, your_loaf.action_space.index(action), done, reward, next_obs)
        replay_buffer.append(transition)
        obs = next_obs

        episode_reward += reward

        if done:
            obs = env.reset()

            """
            Here we are tracking how well the agent performed. Agent's HP - Opponent's HP is used as the reward
            signal for this environment. Feel free to try a different reward function using the info from the state.
            """
            reward_buffer.append(episode_reward)
            episode_reward = 0.0

        """
        After each step, the agent uses a sample of transitions (the action it took and its effect on the
        environment) from the replay buffer to improve the neural network's approximation of the Q-function.
        to train the network, the transitions are converted into tensors (arrays that can store gradients during
        computations)
        """
        transitions = random.sample(replay_buffer, BATCH_SIZE)

        obses = np.asarray([t[0] for t in transitions])
        actions = np.asarray([t[1] for t in transitions])
        rewards = np.asarray([t[3] for t in transitions])
        dones = np.asarray([t[2] for t in transitions])
        next_obses = np.asarray([t[4] for t in transitions])

        obses_t = torch.as_tensor(obses, dtype=torch.float32)
        actions_t = torch.as_tensor(actions, dtype=torch.int64).unsqueeze(-1)
        rewards_t = torch.as_tensor(rewards, dtype=torch.float32).unsqueeze(-1)
        dones_t = torch.as_tensor(dones, dtype=torch.int64).unsqueeze(-1)
        next_obses_t = torch.as_tensor(next_obses, dtype=torch.float32)

        """
        To evaluate the network's accuracy we compare the agent's approximation of the Q-value with the sum of the
        reward received and the value of the next state (multiplied by a discount factor of 0.99). This comparison
        is performed using L2 loss (mean squared error).
        """
        with torch.no_grad():
            target_q_values = target_net(next_obses_t)
            max_q = target_q_values.max(1, keepdim = True)[0]
            targets = rewards_t + (1 - done) * GAMMA * max_q

        q_values = online_net(obses_t)

        action_q_values = torch.gather(q_values, 1, actions_t)

        loss = nn.functional.mse_loss(action_q_values, targets)

        """
        With these three lines, the gradient from the previous update is cleared, a new gradient is computed, and
        the network is updated.
        """
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if step % TARGET_UPDATE_FREQUENCY == 0:
            target_net.load_state_dict(online_net.state_dict())
    print(f"Average reward per episode: {np.mean(reward_buffer)}")
    torch.save(online_net.state_dict(), "model.pt")

    import pickle

    with open("loaf.pkl", "wb") as f:
        pickle.dump(your_loaf, f)