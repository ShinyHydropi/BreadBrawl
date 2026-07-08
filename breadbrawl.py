from enum import Enum
from dataclasses import dataclass
import random

# Attack descriptions:
# Crust Crusher - Deals damage equal to the user's salt plus a small damage roll
# Leech Loaf - Deals damage equal to 70% of the user's salt plus a small damage roll; heals half the damage dealt
# Sandwich Trap - Deals 40% of the user's salt at the end of the next three turns; fails if trap is already active
# Oven Spring - Acts first; fails if used last turn; protects the user from all damage this turn
# Second Rise - Restores 25% of the user's max flour
# Instant Yeast - Doubles user's sugar for four turns; fails if the boost is already active
# Gluten Surge - Doubles user's salt for four turns; fails if the boost is already active
class Attack(Enum):
    CRUST_CRUSHER = 0
    LEECH_LOAF = 1
    SANDWICH_TRAP = 2
    OVEN_SPRING = 3
    SECOND_RISE = 4
    INSTANT_YEAST = 5
    GLUTEN_SURGE = 6

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
    trap_turns: int

    # Method to convert to tuples for observation from an agent
    def to_tuple(self):
        return self.hp, self.blocked, self.sprint_turns, self.power_up_turns, self.trap_turns

# Loaf class for creating bread loaves to battle with
# flour is your hp, salt is your attack, and sugar is your speed
# Your base stat spread is 35/10/10, and you can distribute 6 extra points among them
# For your move set, select 3 moves from the attacks enum
class Loaf:
    def __init__(self, flour: int, salt: int, sugar: int, attacks: list[Attack]):
        if not (0 <= flour + salt + sugar <= 6):
            raise ValueError("Extra points added to your stat spread must be between 0 and 6")
        if len(attacks) > 3 or len(attacks) == 0:
            raise ValueError("Your Loaf must have 1-3 attacks")
        self.flour = 35 + flour
        self.salt = 10 + salt
        self.sugar = 10 + sugar
        self.action_space = attacks
        self.attacks = set(attacks)

    # method to generate a random Loaf
    @classmethod
    def random_loaf(cls):
        # Method for generating a 3-tuple summing to 6 source: https://share.google/aimode/oDOuCVbR3pZ80r6Oc
        cuts = random.choices(range(0, 7), k=2)
        points: list[int] = sorted([0] + cuts + [6])
        flour, salt, sugar = (points[i+1] - points[i] for i in range(3))

        arr = list(Attack)
        d_move = random.sample(arr[:3], 1)[0]
        arr.remove(d_move)
        attacks = random.sample(arr, 2)
        attacks.append(d_move)
        return cls(flour, salt, sugar, attacks)

    def random_attack(self):
        return random.sample(self.action_space, 1)[0]

    def __copy__(self):
        return Loaf(self.flour - 35, self.salt - 10, self.sugar - 10, self.action_space)

    def __str__(self):
        return f"Loaf(Flour: {self.flour}, Salt: {self.salt}, Sugar: {self.sugar}, Attacks: {self.attacks})"

class BreadBrawl:
    def __init__(self, p1: Loaf, p2: Loaf|None = None):
        self.states = None
        if p2 is None:
            p2 = Loaf.random_loaf()
        self.players = {Player.P1: p1, Player.P2: p2}
        self.result = 3

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
        if self.result:
            return

        damage = 0
        heal = 0
        opp_block = 0 if self.states[user.opponent()].blocked == 2 else 1
        salt = self.players[user].salt
        if self.states[user].power_up_turns > 0:
            salt *= 2

        match attack:
            case Attack.OVEN_SPRING:
                self.states[user].blocked = 2 - self.states[user].blocked

            case Attack.CRUST_CRUSHER:
                damage = random.randrange(-2, 2) + salt

            case Attack.LEECH_LOAF:
                damage = random.randrange(-2, 2) + int(0.7 * salt)
                heal = (damage * opp_block) // 2

            case Attack.SECOND_RISE:
                heal = self.players[user].flour // 4

            case Attack.INSTANT_YEAST:
                if self.states[user].sprint_turns == 0:
                    self.states[user].sprint_turns = 5

            case Attack.GLUTEN_SURGE:
                if self.states[user].power_up_turns == 0:
                    self.states[user].power_up_turns = 5

            case Attack.SANDWICH_TRAP:
                if self.states[user.opponent()].trap_turns == 0:
                    self.states[user.opponent()].trap_turns = 4

        self.states[user.opponent()].hp = max(0, self.states[user.opponent()].hp - damage * opp_block)
        self.states[user].hp = min(self.players[user].flour, self.states[user].hp + heal)

    # Method for resetting the environment
    def reset(self):
        self.states = {Player.P1: PlayerState(self.players[Player.P1].flour, 0, 0, 0, 0), Player.P2: PlayerState(self.players[Player.P2].flour, 0, 0, 0, 0)}
        self.result = 0
        return self.states[Player.P1].to_tuple() + self.states[Player.P2].to_tuple()

    # Method for stepping a training environment
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
            raise ValueError(f"{p2att} not in {self.players[Player.P2].attacks}")
        if not (p1att in self.players[Player.P1].attacks):
            raise ValueError(f"{p1att} not in {self.players[Player.P1].attacks}")

        tiebreak = random.randint(0,1)
        for player, attack in actions:
            priority = -self.players[player].sugar
            if self.states[player].sprint_turns > 0:
                priority *= 2
            if attack == Attack.OVEN_SPRING:
                priority -= 100
            order.append((priority, tiebreak, player, attack))
            tiebreak = 1 - tiebreak

        order.sort()

        for _, _, player, attack in order:
            if not self.result:
                # Performs the attack if the battle has not ended
                self._perform_attack(attack, player)
                output_sequence.append((player, attack))

                # Checks if either player was knocked out
                if self.states[Player.P1].hp == 0:
                    self.result += 2
                if self.states[Player.P2].hp == 0:
                    self.result += 1

        # Decrements the turn counters and handles trap damage for both players
        if self.result == 0:
            for p in list(Player):
                if self.states[p].trap_turns:
                    damage = self.players[p.opponent()].salt
                    if self.states[p.opponent()].power_up_turns:
                        damage *= 2
                    self.states[p].hp = max(0, self.states[p].hp - damage)
                    self.states[p].trap_turns -= 1
                    if self.states[p].hp == 0:
                        self.result += 2 - p.value
                    output_sequence.append((p, None))
                self.states[p].blocked = max(0, self.states[p].blocked - 1)
                self.states[p].sprint_turns = max(0, self.states[p].sprint_turns - 1)
                self.states[p].power_up_turns = max(0, self.states[p].power_up_turns - 1)

        # Returns the current state, the result of the match if it has terminated, and the net change in hp after the turn
        return self.states[Player.P1].to_tuple() + self.states[Player.P2].to_tuple(), output_sequence, self.result, self.states[Player.P1].hp - i_hp_1 + i_hp_2 - self.states[Player.P2].hp
