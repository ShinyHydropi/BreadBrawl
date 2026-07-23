# Generated using Copilot https://github.com/copilot/share/0a470230-4bc0-8842-b943-4a478003691e

import streamlit as st
import time
from dataclasses import replace
from breadbrawl import BreadBrawl, Loaf, Player
from battle_animation import render_battle_scene
from agent_arena import display_move_log, get_attack_emoji, get_attack_description, draw_idle_scene

# Page configuration
st.set_page_config(page_title="BreadBrawl", layout="wide")
st.title("🍞 BreadBrawl RPG 🍞")

# Initialize session state
if "game" not in st.session_state:
    st.session_state.game = None
    st.session_state.p1_loaf = None
    st.session_state.p2_loaf = None
    st.session_state.game_started = False
    st.session_state.turn_active = False
    st.session_state.attack_sequence = []
    st.session_state.attack_index = 0
    st.session_state.move_log = []
    st.session_state.names = {}
    st.session_state.turn_start_state = {}

def init_game():
    """Initialize a new game with random loaves."""
    st.session_state.p1_loaf = Loaf.random_loaf()
    st.session_state.p2_loaf = Loaf.random_loaf()
    st.session_state.game = BreadBrawl(st.session_state.p1_loaf, st.session_state.p2_loaf)
    st.session_state.game.reset()
    st.session_state.game_started = True
    st.session_state.turn_active = False
    st.session_state.attack_sequence = []
    st.session_state.attack_index = 0
    st.session_state.move_log = []
    st.session_state.names = {Player.P1: "You", Player.P2: "CPU"}
    st.session_state.turn_start_state = {
        Player.P1: replace(st.session_state.game.states[Player.P1]),
        Player.P2: replace(st.session_state.game.states[Player.P2]),
    }

def main():
    if not st.session_state.game_started:
        # Start screen
        st.markdown("""
        ### Welcome to BreadBrawl! 
        A turn-based RPG where two loaves of bread battle for supremacy!
        """)

        if st.button("🍞 Start Battle 🍞", key="start_btn", use_container_width=True):
            init_game()
            st.rerun()
    else:
        # Game screen - create main content area and move log sidebar
        main_content, log_col = st.columns([2, 1])
        with log_col:
            st.subheader("📜 Move Log")
        log_holder = log_col.empty()

        game = st.session_state.game
        p1_loaf = st.session_state.p1_loaf
        p2_loaf = st.session_state.p2_loaf

        p1_state = game.states[Player.P1]
        p2_state = game.states[Player.P2]

        # Display move log on right side
        display_move_log(log_col, log_holder)

        with main_content:
            st.subheader("⚔️ Battle Arena")
            # Single persistent stage: stays on screen for the whole battle, showing
            # both loaves, HP, and active status effects (blocking/boosts/traps) at
            # all times, and playing each attack out in place when a turn resolves.
            battle_stage = st.empty()

            if st.session_state.turn_active:
                st.session_state.move_log.append(f"Turn {st.session_state.game.turn}")

                state_before = st.session_state.turn_start_state

                # Show each action in resolution order as an animated battle step
                for player, attack, p1_after, p2_after in st.session_state.attack_sequence:
                    is_environmental = attack is None
                    if is_environmental:
                        emoji, desc = "🥪", "was hurt by the Sandwich Trap"
                    else:
                        emoji = get_attack_emoji(attack)
                        desc = get_attack_description(attack)

                    if is_environmental:
                        caption = f"🥪 {st.session_state.names[player]} is caught in the Sandwich Trap!"
                    else:
                        caption = f"{st.session_state.names[player]}: {emoji} {desc}"

                    with battle_stage.container():
                        render_battle_scene(
                            p1_name=st.session_state.names[Player.P1],
                            p2_name=st.session_state.names[Player.P2],
                            p1_loaf=p1_loaf, p2_loaf=p2_loaf,
                            p1_before=state_before[Player.P1], p2_before=state_before[Player.P2],
                            p1_after=p1_after, p2_after=p2_after,
                            caption=caption,
                            attacker=player,
                            is_environmental=is_environmental,
                            animate=True,
                        )

                    st.session_state.move_log.append(f"{st.session_state.names[player]}: {emoji} {desc}")
                    display_move_log(log_col, log_holder)

                    state_before = {Player.P1: p1_after, Player.P2: p2_after}

                    time.sleep(1.8)
                st.session_state.move_log.append("")

                if game.result:
                    # Battle ended - hold the final state on screen and show the win banner
                    draw_idle_scene(battle_stage, "🏁 Battle over!")

                    st.markdown("---")
                    if game.result == 1:
                        st.success(f"🎉 **{st.session_state.names[Player.P1]} Win!** 🎉")
                    else:
                        st.error(f"🎉 **{st.session_state.names[Player.P2]} Wins!** 🎉")

                    st.markdown("---")

                    if st.button("🔄 New Battle", key="restart_btn", use_container_width=True):
                        st.session_state.game_started = False
                        st.session_state.game = None
                        st.session_state.p1_loaf = None
                        st.session_state.p2_loaf = None
                        st.rerun()
                else:
                    st.session_state.turn_active = False
                    st.session_state.attack_sequence = []
                    st.rerun()
            else:
                # Keep the stage visible while Player 1 picks a move
                draw_idle_scene(battle_stage, f"Turn {game.turn + 1} — choosing moves...")

                # Player 1 move selection
                st.subheader("⚔️ Choose Your Move")

                p1_attacks = p1_loaf.action_space
                attack_buttons = st.columns(len(p1_attacks))

                p1_choice = None
                for i, (button_col, attack) in enumerate(zip(attack_buttons, p1_attacks)):
                    with button_col:
                        emoji = get_attack_emoji(attack)
                        desc = get_attack_description(attack)
                        if st.button(f"{emoji}\n{desc}", key=f"attack_{attack.name}", use_container_width=True):
                            p1_choice = attack

                if p1_choice:
                    # Player 2 makes random choice
                    p2_choice = p2_loaf.random_attack()

                    # Snapshot HP/status before this turn's actions resolve, so the
                    # animation's first step has a correct starting point
                    st.session_state.turn_start_state = {
                        Player.P1: replace(p1_state),
                        Player.P2: replace(p2_state),
                    }

                    # Execute turn
                    _, move_sequence, _, _ = game.step_2p(p1_choice, p2_choice)

                    # move_sequence is a list of (Player, Attack, PlayerState, PlayerState)
                    # tuples in resolution order
                    st.session_state.attack_sequence = move_sequence
                    st.session_state.turn_active = True

                    st.rerun()

if __name__ == "__main__":
    main()