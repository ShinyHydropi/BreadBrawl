from enum import Enum
from dataclasses import dataclass
import random

class Attack(Enum):
    block = 0
    slash = 1
    drain = 2
    heal = 3
    sprint = 4
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

class Loaf:
    def __init__(self, flour: int, salt: int, sugar: int, attacks: set[Attack]):
        if not (0 <= flour + salt + sugar <= 6):
            raise ValueError("stat spread must be between 0 and 6")
        self.flour = 25 + flour
        self.salt = 10 + salt
        self.sugar = 10 + sugar
        self.attacks = attacks

def perform_attack(attack: Attack, user: Player, user_stats: Loaf, state: dict[Player, PlayerState]):
        match attack:
            case Attack.block:
                state[user].blocked = 1

            case Attack.slash:
                state[user.opponent()].hp -= (1 - state[user.opponent()].blocked) * (random.randrange(-2, 2) + user_stats.salt)
                if state[user.opponent()].hp < 0:
                    state[user.opponent()].hp = 0

            case Attack.drain:
                damage = min(state[user.opponent()].hp, (1 - state[user.opponent()].blocked) * (random.randrange(-2, 2) + int(0.6 * user_stats.salt)))
                state[user.opponent()].hp -= damage
                state[user].hp += damage

            case Attack.heal:
                state[user].hp = min(state[user].hp + user_stats.flour >> 2, user_stats.flour)

            case Attack.sprint:
                state[user].sprint = 4

            case Attack.power_up:
                state[user].power_up = 4

class BreadBrawl:
    def __init__(self, p1: Loaf, p2: Loaf | None = None):
        self.states = None
        if p2 is None:
            p2 = Loaf(2, 2, 2, random.sample(list(Attack), 4))
        self.players = [p1, p2]
        self.terminated = True

    def reset(self):
        self.states = {Player.p1: PlayerState(self.players[Player.p1.value].flour, 0, 0, 0), Player.p2: PlayerState(self.players[Player.p2.value].flour, 0, 0, 0)}
        return self.states

