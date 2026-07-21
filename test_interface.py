# Generated using Copilot https://github.com/copilot/share/0a470230-4bc0-8842-b943-4a478003691e

import streamlit as st
import time
from breadbrawl import BreadBrawl, Loaf, Attack, Player
from agent_arena import display_loaf, display_move_log, get_attack_emoji, get_attack_description

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
            # Create two columns for players
            left_col, right_col = st.columns(2)

            display_loaf(Player.P1, p1_loaf, p1_state, left_col)
            display_loaf(Player.P2, p2_loaf, p2_state, right_col)

            st.markdown("---")

            if st.session_state.turn_active:
                # Display attack sequence animation
                st.subheader("⚔️ Battle Animation")
                animation_placeholder = st.empty()
                st.session_state.move_log.append(f"Turn {st.session_state.game.turn}")

                # Show all attacks with 2-second display and wait for disappearance
                for player, attack in st.session_state.attack_sequence:
                    player_num = player.value + 1
                    if attack:
                        emoji = get_attack_emoji(attack)
                        desc = get_attack_description(attack)
                    else:
                        emoji = "🥪"
                        desc = f"P{player_num} was hurt by the sandwich"

                    if player_num == 1:
                        with animation_placeholder.container():
                            st.info(f"🔵 Player {player_num}: {emoji} {desc}")
                    else:
                        with animation_placeholder.container():
                            st.warning(f"🔴 Player {player_num}: {emoji} {desc}")

                    st.session_state.move_log.append(f"P{player_num}: {emoji} {desc}")
                    display_move_log(log_col, log_holder)

                    time.sleep(2)
                    animation_placeholder.empty()
                    time.sleep(0.3)

                if game.result:
                    # Battle ended - show win screen
                    st.markdown("---")
                    if game.result == 1:
                        st.success("🎉 **Player 1 Wins!** 🎉", icon="✨")
                    else:
                        st.error("🎉 **Player 2 Wins!** 🎉", icon="☠️")

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
                # Player 1 move selection
                st.subheader("⚔️ Choose Your Move (Player 1)")

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

                    # Execute turn
                    _, move_sequence, _, _ = game.step_2p(p1_choice, p2_choice)

                    # move_sequence is a list of (Player, Attack) tuples in resolution order
                    st.session_state.attack_sequence = move_sequence
                    st.session_state.turn_active = True

                    st.rerun()

if __name__ == "__main__":
    main()
