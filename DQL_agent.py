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
        return self.net(x)

    def select_action(self, state):
        state_t = torch.as_tensor(state, dtype=torch.float32)
        q_values = self.net(state_t)
        max_q = torch.argmax(q_values)
        action = self.loaf.action_space()[max_q.item()]

        return action

# Initialization of environment, network, and training buffers
agent = Loaf.random_loaf()
print(agent)
env = BreadBrawl.training_env(agent)

replay_buffer = deque(maxlen=BUFFER_SIZE)
reward_buffer = deque([0.0], maxlen=100)

episode_reward = 0.0

online_net = DQNetwork(agent,8, len(agent.action_space()))
target_net = DQNetwork(agent,8, len(agent.action_space()))

target_net.load_state_dict(online_net.state_dict())

optimizer = torch.optim.Adam(online_net.parameters(), lr=5e-4)

obs = env.reset()
for _ in range(MIN_REPLAY_SIZE):
    action = agent.random_attack()
    next_obs, _, done, reward = env.step_1p(action)
    action = agent.action_space().index(action)
    transition = (obs, action, done, reward, next_obs)
    replay_buffer.append(transition)
    obs = next_obs

    if done:
        obs = env.reset()

obs = env.reset()
for step in tqdm(range(EPISODES)):
    epsilon = np.interp(step, [0, EPSILON_DECAY], [EPSILON_START, EPSILON_END])

    if random.random() <= epsilon:
        action = agent.random_attack()
    else:
        action = online_net.select_action(obs)

    next_obs, _, done, reward = env.step_1p(action)
    action = agent.action_space().index(action)
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