from breadbrawl import Loaf
from dql_agent import DQNetwork
import torch
import pickle

# Replace the following line with your Loaf from dql_agent
# your_loaf = Loaf.random_loaf()
your_loaf = pickle.load(open("loaf.pkl", "rb"))

model = DQNetwork(your_loaf, 8, len(your_loaf.action_space))
model.load_state_dict(torch.load("model.pt"))
model.eval()

def loaf():
    return your_loaf

def agent(obs):
    return model.select_action(obs)