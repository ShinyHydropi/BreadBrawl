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

    def _perform_attack(self, attack: Attack, user: Player):
        match attack:
            case Attack.block:
                self.states[user].blocked = 1

            case Attack.slash:
                self.states[user.opponent()].hp -= (1 - self.states[user.opponent()].blocked) * (random.randrange(-2, 2) + self.players[user].salt)
                if self.states[user.opponent()].hp < 0:
                    self.states[user.opponent()].hp = 0

            case Attack.drain:
                damage = min(self.states[user.opponent()].hp, (1 - self.states[user.opponent()].blocked) * (random.randrange(-2, 2) + int(0.6 * self.players[user].salt)))
                self.states[user.opponent()].hp -= damage
                self.states[user].hp += damage

            case Attack.heal:
                self.states[user].hp = min(self.states[user].hp + self.players[user].flour >> 2, self.players[user].flour)

            case Attack.sprint:
                self.states[user].sprint = 4

            case Attack.power_up:
                self.states[user].power_up = 4

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
            order.insert(random.randint(0,1), Player.p2)

        if p1att == Attack.block: # Performs any blocks before other attacks
            self._perform_attack(p1att, Player.p1)

        if p2att == Attack.block:
            self._perform_attack(p2att, Player.p2)

        attacks = {Player.p1: p1att, Player.p2: p2att}
        for p in order:
            self._perform_attack(attacks[p], p)