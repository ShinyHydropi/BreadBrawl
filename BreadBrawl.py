from enum import Enum
from dataclasses import dataclass
import random

# Attack descriptions:
# Block - Acts first; fails if used last turn; protects the user from all damage this turn
# Slash - Deals damage equal to the user's salt plus a small damage roll
# Drain - Deals damage equal to 0.6x the user's salt plus a small damage roll and heals the damage dealt
# Heal - Restores half the user's max flour
# Sprint - Doubles user's sugar for three turns
# Power-Up - Doubles user's Salt for three turns
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

    # Returns the opposing players enum
    def opponent(self):
        return Player(1 - self.value)

# dataclass for handling the in-battle state of each player
@dataclass
class PlayerState:
    hp: int
    blocked: int
    sprint: int
    power_up: int

# Loaf class for creating bread loaves to battle with
# flour is your hp, salt is your attack, and sugar is your speed
# Your base stat spread is 25/10/10, and you can distribute 6 extra points among them
# For your move set, select 4 moves from the attacks enum
class Loaf:
    def __init__(self, flour: int, salt: int, sugar: int, attacks: set[Attack]):
        if not (0 <= flour + salt + sugar <= 6):
            raise ValueError("Extra points added to your stat spread must be between 0 and 6")
        if len(attacks) > 4:
            raise ValueError("Your Loaf can have no more than 4 attacks")
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

    # Constructor for training an agent
    def training_env(self, p1: Loaf):
        return self.__init__(p1, Loaf(2, 2, 2, random.sample(list(Attack), 4)))

    # Constructor for battling agents
    def duel_env(self, p1: Loaf, p2: Loaf):
        return self.__init__(p1, p2)

    # Method for handling the effects of attacks
    def _perform_attack(self, attack: Attack, user: Player):
        if not self.terminated:
            match attack:
                case Attack.block:
                    self.states[user].blocked = 1

                case Attack.slash:
                    self.states[user.opponent()].hp -= (1 - self.states[user.opponent()].blocked) * (random.randrange(-2, 2) + (2 if self.states[user].power_up else 1) * self.players[user].salt)
                    if self.states[user.opponent()].hp < 0:
                        self.states[user.opponent()].hp = 0

                case Attack.drain:
                    damage = min(self.states[user.opponent()].hp, (1 - self.states[user.opponent()].blocked) * (random.randrange(-2, 2) + int((2 if self.states[user].power_up else 1) * 0.6 * self.players[user].salt)))
                    self.states[user.opponent()].hp -= damage
                    self.states[user].hp += damage

                case Attack.heal:
                    self.states[user].hp = min(self.states[user].hp + self.players[user].flour >> 2, self.players[user].flour)

                case Attack.sprint:
                    self.states[user].sprint = 4

                case Attack.power_up:
                    self.states[user].power_up = 4

    # Method for resetting the environment
    def reset(self):
        self.states = {Player.p1: PlayerState(self.players[Player.p1].flour, 0, 0, 0), Player.p2: PlayerState(self.players[Player.p2].flour, 0, 0, 0)}
        self.terminated = False
        return self.states

    #def step_1p(self):

    # Method for stepping the environment by performing the attacks selected by each agent
    def step_2p(self, p1att: Attack, p2att: Attack):
        if p2att is None:
            p2att = random.sample(list(self.players[Player.p2].attacks), 1)
        elif not (p2att in self.players[Player.p2]):
            raise ValueError("p2att not in player")
        if not (p1att in self.players[Player.p1]):
            raise ValueError("p1att not in player")

        self.states[Player.p1].blocked = 0 # Decrements blocked to begin the turn (since blocked indicates a block last turn and handles the effect of blocking)
        self.states[Player.p2].blocked = 0

        if p1att == Attack.block: # Performs any blocks before other attacks
            self._perform_attack(p1att, Player.p1)

        if p2att == Attack.block:
            self._perform_attack(p2att, Player.p2)

        # Handles remaining sequence of attacks
        if self.states[Player.p1].blocked == 0 and self.states[Player.p2].blocked == 0:
            if self.players[Player.p1].sugar * (2 if self.states[Player.p1].sprint else 1) > self.players[Player.p2].flour * (2 if self.states[Player.p1].sprint else 1):
                self._perform_attack(p1att, Player.p1)
                self._perform_attack(p2att, Player.p2)
            elif self.players[Player.p1].sugar * (2 if self.states[Player.p1].sprint else 1) < self.players[Player.p2].flour * (2 if self.states[Player.p1].sprint else 1):
                self._perform_attack(p2att, Player.p2)
                self._perform_attack(p1att, Player.p1)
            else:
                if random.randint(0, 1):
                    self._perform_attack(p1att, Player.p1)
                    self._perform_attack(p2att, Player.p2)
                else:
                    self._perform_attack(p2att, Player.p2)
                    self._perform_attack(p1att, Player.p1)
        elif self.states[Player.p1].blocked == 0:
            self._perform_attack(p1att, Player.p1)
        elif self.states[Player.p2].blocked == 0:
            self._perform_attack(p2att, Player.p2)

        # Decrements the sprint and power_up turn counters for both players
        self.states[Player.p1].sprint = max(0, self.states[Player.p1].sprint - 1)
        self.states[Player.p2].sprint = max(0, self.states[Player.p2].sprint - 1)
        self.states[Player.p1].power_up = max(0, self.states[Player.p1].power_up - 1)
        self.states[Player.p2].power_up = max(0, self.states[Player.p2].power_up - 1)

        # Checks if either player was knocked out
        if self.states[Player.p1].hp == 0 or self.states[Player.p2].hp == 0:
            self.terminated = True

        return self.states, self.terminated