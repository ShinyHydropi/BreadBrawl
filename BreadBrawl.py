from enum import Enum
from dataclasses import dataclass
import random

# Attack descriptions:
# Slash - Deals damage equal to the user's salt plus a small damage roll
# Block - Acts first; fails if used last turn; protects the user from all damage this turn
# Drain - Deals damage equal to 0.6x the user's salt plus a small damage roll and heals the damage dealt
# Heal - Restores half the user's max flour
# Sprint - Doubles user's sugar for three turns
# Power-Up - Doubles user's Salt for three turns
class Attack(Enum):
    SLASH = 0
    BLOCK = 1
    DRAIN = 2
    HEAL = 3
    SPRINT = 4
    POWER_UP = 5

class Player(Enum):
    P1 = 0
    P2 = 1

    # Returns the opposing players enum
    def opponent(self):
        return Player(1 - self.value)

# dataclass for handling the in-battle state of each player
@dataclass
class PlayerState:
    hp: int
    blocked: int
    sprint_turns: int
    power_up_turns: int

    # Method to convert to tuples for observation from an agent
    def to_tuple(self):
        return self.hp, self.blocked, self.sprint_turns, self.power_up_turns

# Loaf class for creating bread loaves to battle with
# flour is your hp, salt is your attack, and sugar is your speed
# Your base stat spread is 25/10/10, and you can distribute 6 extra points among them
# For your move set, select 4 moves from the attacks enum
class Loaf:
    def __init__(self, flour: int, salt: int, sugar: int, attacks: set[Attack]):
        if not (0 <= flour + salt + sugar <= 6):
            raise ValueError("Extra points added to your stat spread must be between 0 and 6")
        if len(attacks) > 4 or len(attacks) == 0:
            raise ValueError("Your Loaf must have 1-4 attacks")
        self.flour = 25 + flour
        self.salt = 10 + salt
        self.sugar = 10 + sugar
        self.attacks = attacks

    # method to generate a random Loaf
    @classmethod
    def random_loaf(cls):
        # Method for generating a 3-tuple summing to 6 source: https://share.google/aimode/oDOuCVbR3pZ80r6Oc
        cuts = random.choices(range(0, 7), k=2)
        points: list[int] = sorted([0] + cuts + [6])
        flour, salt, sugar = (points[i+1] - points[i] for i in range(3))

        return cls(flour, salt, sugar, set(random.sample(list(Attack)[1:], 3)) | {Attack.SLASH})

    def __cmp__(self, other):
        return self.sugar - other.sugar

    def random_attack(self):
        return random.sample(self.action_space(), 1)[0]

    def action_space(self):
        return list(self.attacks)

    def __str__(self):
        return f"Loaf(Flour: {self.flour}, Salt: {self.salt}, Sugar: {self.sugar}, Attacks: {self.attacks})"

class BreadBrawl:
    def __init__(self, p1: Loaf, p2: Loaf|None = None):
        self.states = None
        if p2 is None:
            p2 = Loaf.random_loaf()
        self.players = {Player.P1: p1, Player.P2: p2}
        self.terminated = True

    # Constructor for training an agent
    @classmethod
    def training_env(cls, p1: Loaf):
        return cls(p1, None)

    # Constructor for battling agents
    @classmethod
    def duel_env(cls, p1: Loaf, p2: Loaf):
        return cls(p1, p2)

    # Method for handling the effects of attacks
    def _perform_attack(self, attack: Attack, user: Player):
        if self.terminated:
            return

        damage = 0
        heal = 0
        opp_block = 0 if self.states[user.opponent()].blocked == 2 else 1
        salt = self.players[user].salt
        if self.states[user].power_up_turns > 0:
            salt *= 2

        match attack:
            case Attack.BLOCK:
                self.states[user].blocked = 2 - self.states[user].blocked

            case Attack.SLASH:
                damage = random.randrange(-2, 2) + salt
                # self.states[user.opponent()].hp -= (1 - self.states[user.opponent()].blocked) * (random.randrange(-2, 2) + (2 if self.states[user].power_up else 1) * self.players[user].salt)
                # if self.states[user.opponent()].hp < 0:
                #     self.states[user.opponent()].hp = 0

            case Attack.DRAIN:
                damage = random.randrange(-2, 2) + int(0.6 * salt)
                heal = damage * opp_block
                # damage = min(self.states[user.opponent()].hp, (1 - self.states[user.opponent()].blocked) * (random.randrange(-2, 2) + int((2 if self.states[user].power_up else 1) * 0.6 * self.players[user].salt)))
                # self.states[user.opponent()].hp -= damage
                # self.states[user].hp = min(self.states[user].hp + damage, self.players[user].flour)

            case Attack.HEAL:
                heal = self.players[user].flour // 2
                # self.states[user].hp = min(self.states[user].hp + self.players[user].flour // 2, self.players[user].flour)

            case Attack.SPRINT:
                self.states[user].sprint_turns = 4

            case Attack.POWER_UP:
                self.states[user].power_up_turns = 4

        self.states[user.opponent()].hp = max(0, self.states[user.opponent()].hp - damage * opp_block)
        self.states[user].hp = min(self.players[user].flour, self.states[user].hp + heal)

    # Method for resetting the environment
    def reset(self):
        self.states = {Player.P1: PlayerState(self.players[Player.P1].flour, 0, 0, 0), Player.P2: PlayerState(self.players[Player.P2].flour, 0, 0, 0)}
        self.terminated = False
        return self.states[Player.P1].to_tuple() + self.states[Player.P2].to_tuple()

    # Method for stepping a training environment (adversarial policies still needed)
    def step_1p(self, p1att: Attack):
        return self.step_2p(p1att, self.players[Player.P2].random_attack())

    # Method for stepping the environment by performing the attacks selected by each agent
    def step_2p(self, p1att: Attack, p2att: Attack):
        i_hp_1 = self.states[Player.P1].hp
        i_hp_2 = self.states[Player.P2].hp
        actions = [(Player.P1, p1att), (Player.P2, p2att)]
        order = []
        output_sequence = []

        if not (p2att in self.players[Player.P2].attacks):
            raise ValueError("p2att not in player")
        if not (p1att in self.players[Player.P1].attacks):
            raise ValueError("p1att not in player")

        tiebreak = random.randint(0,1)
        for player, attack in actions:
            priority = -self.players[player].sugar
            if self.states[player].sprint_turns > 0:
                priority *= 2
            if attack == Attack.BLOCK:
                priority -= 100
            order.append((priority, tiebreak, player, attack))
            tiebreak = 1 - tiebreak

        order.sort()

        for _, _, player, attack in order:
            if not self.terminated:
                # Performs the attack if the battle has not ended
                self._perform_attack(attack, player)
                output_sequence.append((player, attack))

                # Checks if either player was knocked out
                self.terminated = self.states[Player.P1].hp == 0 or self.states[Player.P2].hp == 0

        # Decrements the turn counters for both players
        for p in list(Player):
            self.states[p].blocked = max(0, self.states[p].blocked - 1)
            self.states[p].sprint_turns = max(0, self.states[p].sprint_turns - 1)
            self.states[p].power_up_turns = max(0, self.states[p].power_up_turns - 1)

        # Returns the current state, a termination conditional, and the net change in hp after the turn
        return self.states[Player.P1].to_tuple() + self.states[Player.P2].to_tuple(), output_sequence, self.terminated, self.states[Player.P1].hp - i_hp_1 + i_hp_2 - self.states[Player.P2].hp