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

    def __cmp__(self, other):
        return self.sugar - other.sugar

class BreadBrawl:
    def __init__(self, p1: Loaf, p2: Loaf):
        self.states = None
        if p2 is None:
            p2 = Loaf(2, 2, 2, random.sample(list(Attack), 4))
        self.players = {Player.p1: p1, Player.p2: p2}
        self.terminated = True

    def training_env(self, p1: Loaf):
        return self.__init__(p1, Loaf(2, 2, 2, random.sample(list(Attack), 4)))

    def duel_env(self, p1: Loaf, p2: Loaf):
        return self.__init__(p1, p2)

    @staticmethod
    def _perform_attack(attack: Attack, user: Player, user_stats: Loaf, state: dict[Player, PlayerState]):
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

    def reset(self):
        self.states = {Player.p1: PlayerState(self.players[Player.p1].flour, 0, 0, 0), Player.p2: PlayerState(self.players[Player.p2].flour, 0, 0, 0)}
        return self.states

    #def step_1p(self):

    def step_2p(self, p1att: Attack, p2att: Attack):
        if p2att is None:
            p2att = random.sample(list(self.players[Player.p2].attacks), 1)
        elif not (p2att in self.players[Player.p2]):
            raise ValueError("p2att not in player")
        if not (p1att in self.players[Player.p1]):
            raise ValueError("p1att not in player")

        self.states[Player.p1].blocked = 0 # Decrements blocked to begin the turn (since blocked indicates a block last turn and handles the effect of blocking)
        self.states[Player.p2].blocked = 0

        order = [Player.p1]
        if self.players[Player.p1].sugar > self.players[Player.p2].sugar:
            order.append(Player.p2)
        elif self.players[Player.p1].sugar < self.players[Player.p2].sugar:
            order.insert(0, Player.p2)
        else:
            order = [Player.p1]
            order.insert(random.randint(0,1), Player.p2)

        if p1att == Attack.block: # Performs any blocks before other attacks
            self._perform_attack(p1att, Player.p1, self.players[Player.p1], self.states)

        if p2att == Attack.block:
            self._perform_attack(p2att, Player.p2, self.players[Player.p2], self.states)

        attacks = {Player.p1: p1att, Player.p2: p2att}
        for p in order:
            self._perform_attack(attacks[p], p, self.players[p], self.states)