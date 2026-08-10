# 🍞 BreadBrawl — Player Guide

Welcome to BreadBrawl — a cheeky, tactical turn-based loaf brawler. This guide explains the rules of BreadBrawl, what each move does, how turns resolve, and some tips to help you win.

---

## The Loaf
- Flour = determines HP (how much damage your loaf can take).
  - HP = 3 * Flour
- Salt = Attack power (how hard your moves hit).
- Sugar = Speed (who goes first).
- Attacks = a set of attacks your loaf can use (max 3 attacks).

> Every loaf starts with the base spread (10 Flour / 10 Salt / 10 Sugar).
> Additionally, you get up to 6 extra points to split among Flour, Salt, and Sugar however you like.
>
> Example allocations:
> - +6 Flour → 16 Flour / 10 Salt / 10 Sugar (a beefy tank).
> - +4 Salt, +2 Sugar → 10 Flour / 14 Salt / 12 Sugar (heavy hitter with some speed).
> - +6 Sugar → 10 Flour / 10 Salt / 16 Sugar (fast glass cannon).

---

## The Moves

1. Crust Crusher
   - Straightforward attack: deals damage roughly equal to your salt stat plus a small random tweak.
   - Good as a reliable baseline hit.

2. Leech Loaf
   - Damage = most of your salt (70% as strong as Crust Crusher) plus a small random tweak.
   - Heals you for a half of the damage you successfully deal.
   - If the target is fully protected, Leech Loaf deals no damage and heals nothing.

3. Sandwich Trap
   - Sets a trap on the enemy that hurts them at the end of the next 3 turns.
   - Each trap tick deals about 50% of the trap-setter's salt.
   - If your salt is boosted, trap ticks do even more damage.
   - You cannot place a trap if the opponent is already trapped or is currently fully protected.

4. Oven Spring
   - A defensive move that makes you immune to damage that turn.
   - It acts first — it will trigger before typical attacks.
   - It can't be reactivated if it was active last turn — trying to spam it back-to-back won’t keep renewing its protection.

5. Second Rise
   - A self-heal that restores 20% of your maximum HP instantly.
   - Good for clutch recovery.

6. Instant Yeast
   - Temporarily doubles your sugar (you act earlier) for the next 3 turns.
   - If it's already active, using it again does nothing.

7. Gluten Surge
   - Temporarily gives a 75% bonus your salt (massively increases damage) for the next 3 turns.
   - If it's already active, using it again does nothing.

---

## How a turn plays out
1. Both players simultaneously pick an attack to use.
2. The game decides who acts first using sugar and active speed boosts — Oven Spring always happens before other moves.
3. Actions happen in order. If a loaf's HP is reduced to zero, the fight ends immediately.
4. If both loafs survive each other's attacks, end-of-turn effects happen:
   - Sandwich Trap damage ticks (if present).
   - Protection and boost durations tick down.

If the fight reaches turn 50 with no knockouts, the match ends automatically and speed determines the winner.

---

## Status effects & interactions
- Full Protection (Oven Spring):
  - Negates incoming damage while active.
  - Cannot successfully activate twice in a row.

- Speed Boost (Instant Yeast):
  - Doubles your sugar.

- Power Boost (Gluten Surge):
  - Doubles your salt.
  - Traps and most damage take this into account, so timing Gluten Surge with a Sandwich Trap makes the trap much nastier.

- Sandwich Trap:
  - A lingering effect on the target — ticks at end of turns.
  - The slower loaf takes sandwich trap damage first if both loaves are trapped.

---

## Tips & tactics
- Combo idea: use Gluten Surge and Sandwich Trap — trap ticks will be amplified, making it a great delayed burst.
- Burst: if you want quick damage, pair high-salt attacks and a high speed stat.
- Stall: pair Sandwich Trap with a defensive move like Oven Spring or Second Rise and win ... eventually.
- Setup and strike: use Gluten Surge followed by a series of Crust Crushers to inflict maximal damage.
- Swiss army knife: for a set that has the best damage-dealing attack for every situation, put Crust Crusher, Leech Loaf, Sandwich Trap all on one set.

---

## Win conditions & draws
- You win by reducing the opponent’s Flour (HP) to zero.
- If both loafs hit zero in the same turn, it’s a double-knockout.
- After 50 turns, the match ends and the faster loaf wins.