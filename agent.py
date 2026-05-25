from BreadBrawl import BreadBrawl, Loaf, Attack, Player, PlayerState
import numpy as np
from tqdm import tqdm

class TDAgent:
    def __init__(self, loaf: Loaf, learning_rate: float = 0.001, discount_factor: float = 0.99, td_step: int = 1):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.td_step = td_step
        self.env = BreadBrawl.training_env(loaf)
        self.q_table = {(a,b,c,d,e,f,g,h): np.zeros(4)
                        for a in tqdm(range(32)) for b in range(2)
                        for c in range(4) for d in range(4)
                        for e in range(32) for f in range(2)
                        for g in range(4) for h in range(4)
                       }

if __name__ == "__main__":
    env = BreadBrawl.training_env(Loaf(2,2,2,{Attack.slash, Attack.block, Attack.power_up, Attack.sprint}))