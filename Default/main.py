from breadbrawl import Loaf
from dql_agent import DQNetwork
import torch
import json

with open("loaf.json", "r") as f:
    loaf_data = json.load(f)
    your_loaf = Loaf.deserialize(loaf_data)

model = DQNetwork(your_loaf, 10, len(your_loaf.action_space))
model.load_state_dict(torch.load("model.pt"))
model.eval()

def loaf():
    return your_loaf

def agent(obs):
    return model.select_action(obs)