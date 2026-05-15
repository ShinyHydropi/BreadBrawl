from enum import Enum
from dataclasses import dataclass
import random

class Attack(Enum):
    slash = 0
    drain = 1
    heal = 2
    sprint = 3
    block = 4
    power_up = 5

class Player(Enum):
    p1 = 0
    p2 = 1

    def opponent(self):
        return Player(1 - self.value)

@dataclass
class PlayerState:
    hp: int
    blocked: int
    sprint: int
    power_up: int

@dataclass
class EnvState:
    p1: PlayerState
    p2: PlayerState

class Loaf:
    def __init__(self, flour: int, salt: int, sugar: int, attacks: set[Attack]):
        if not (0 <= flour + salt + sugar <= 6):
            raise ValueError("stat spread must be between 0 and 6")
        self.flour = 25 + flour
        self.salt = 10 + salt
        self.sugar = 10 + sugar
        self.attacks = attacks

class BreadBrawl:
    def __init__(self, p1: Loaf, p2: Loaf | None = None):
        self.states = None
        if p2 is None:
            p2 = Loaf(2, 2, 2, random.sample(list(Attack), 4))
        self.players = [p1, p2]
        self.terminated = True

    def reset(self):
        self.states = EnvState(PlayerState(self.players[Player.p1.value].flour, 0, 0, 0), PlayerState(self.players[Player.p2.value].flour, 0, 0, 0))
