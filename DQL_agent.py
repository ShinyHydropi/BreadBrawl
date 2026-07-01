# Based on the DQN demonstrated in https://www.youtube.com/watch?v=NP8pXZdU-5U

import torch
import torch.nn as nn
import numpy as np
from collections import deque
import random

from BreadBrawl import BreadBrawl, Loaf, Attack
from tqdm import tqdm

GAMMA = 0.99
BATCH_SIZE = 32
BUFFER_SIZE = 50000
MIN_REPLAY_SIZE = 1000
EPSILON_START = 1.0
EPSILON_END = 0.02
EPSILON_DECAY = 10000
TARGET_UPDATE_FREQUENCY = 1000
EPISODES = 100_000

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
        action = self.loaf.action_space()[max_q.item()]

        return action

# Replace the following line with one initializing your_loaf to be a Loaf with your choice of stats and moves
your_loaf = Loaf.random_loaf()

# Example:
# your_loaf = Loaf(flour=2, salt=3, sugar=1, attacks={Attack.SLASH, Attack.BLOCK, Attack.POWER_UP, Attack.SPRINT})

"""
Some more objects we will need:
env - The environment our agent is interacting with in order to train
replay_buffer - This will store the 50,000 most recent episodes so we can collect many episodes before each
    iteration of improving our agent (This also lets us use past training data while discarding the data that
    is too old)
reward_buffer - This keeps track of how well the agent is doing

"""

env = BreadBrawl.training_env(your_loaf)
replay_buffer = deque(maxlen=BUFFER_SIZE)
reward_buffer = deque([0.0], maxlen=100)

online_net = DQNetwork(your_loaf, 8, len(your_loaf.action_space()))
target_net = DQNetwork(your_loaf, 8, len(your_loaf.action_space()))

target_net.load_state_dict(online_net.state_dict())

optimizer = torch.optim.Adam(online_net.parameters(), lr=5e-4)

obs = env.reset()
for _ in range(MIN_REPLAY_SIZE):
    action = your_loaf.random_attack()
    next_obs, _, done, reward = env.step_1p(action)
    action = your_loaf.action_space().index(action)
    transition = (obs, action, done, reward, next_obs)
    replay_buffer.append(transition)
    obs = next_obs

    if done:
        obs = env.reset()

episode_reward = 0.0
obs = env.reset()
for step in tqdm(range(EPISODES)):
    epsilon = np.interp(step, [0, EPSILON_DECAY], [EPSILON_START, EPSILON_END])

    if random.random() <= epsilon:
        action = your_loaf.random_attack()
    else:
        action = online_net.select_action(obs)

    next_obs, _, done, reward = env.step_1p(action)
    action = your_loaf.action_space().index(action)
    transition = (obs, action, done, reward, next_obs)
    replay_buffer.append(transition)
    obs = next_obs

    episode_reward += reward

    if done:
        obs = env.reset()

        reward_buffer.append(episode_reward)
        episode_reward = 0.0

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

    target_q_values = target_net(next_obses_t)
    max_q = target_q_values.max(1, keepdim = True)[0]

    targets = rewards_t + (1 - done) * GAMMA * max_q

    q_values = online_net(obses_t)

    action_q_values = torch.gather(q_values, 1, actions_t)

    loss = nn.functional.smooth_l1_loss(action_q_values, targets)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if step % TARGET_UPDATE_FREQUENCY == 0:
        target_net.load_state_dict(online_net.state_dict())
    if step % 1000 == 0:
        print()
        print(step)
        print(np.mean(reward_buffer))