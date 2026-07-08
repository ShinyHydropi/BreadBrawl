import re
import sys
import importlib
import copy
import streamlit as st
import time
from breadbrawl import BreadBrawl, Loaf, Attack, Player

if len(sys.argv) > 3 or len(sys.argv) < 2:
    raise ValueError("Wrong number of arguments")

# Page configuration
st.set_page_config(page_title="BreadBrawl", layout="wide")
st.title("🍞 BreadBrawl RPG 🍞")

# Initialize session state
if "game" not in st.session_state:
    st.session_state.game = None
    st.session_state.game_started = False
    st.session_state.turn_active = False
    st.session_state.attack_sequence = []
    st.session_state.attack_index = 0
    st.session_state.move_log = []
    st.session_state.obs = ()
    p1_module = importlib.import_module(re.split(r'[.\\]', sys.argv[1])[2])
    st.session_state.model1 = p1_module.agent
    st.session_state.p1_loaf = copy.copy(p1_module.loaf())
    st.session_state.p2_loaf = Loaf.random_loaf()
    st.session_state.model2 = lambda x: st.session_state.p2_loaf.random_attack()
    if len(sys.argv) > 2:
        p2_module = importlib.import_module(re.split(r'[.\\]', sys.argv[2])[2])
        st.session_state.model2 = p2_module.agent
        st.session_state.p2_loaf = copy.copy(p2_module.loaf())


def init_game():
    st.session_state.game = BreadBrawl(st.session_state.p1_loaf, st.session_state.p2_loaf)
    st.session_state.game_started = True
    st.session_state.turn_active = False
    st.session_state.attack_sequence = []
    st.session_state.attack_index = 0
    st.session_state.move_log = []
    st.session_state.obs = st.session_state.game.reset()


def get_attack_emoji(attack: Attack) -> str:
    """Get emoji representation for attack types."""
    emoji_map = {
        Attack.OVEN_SPRING: "🛡️",
        Attack.CRUST_CRUSHER: "⚔️",
        Attack.LEECH_LOAF: "🩸",
        Attack.SECOND_RISE: "💚",
        Attack.INSTANT_YEAST: "👟",
        Attack.GLUTEN_SURGE: "💪",
    }
    return emoji_map.get(attack, "")


def get_attack_description(attack: Attack) -> str:
    """Get description for attack types."""
    descriptions = {
        Attack.OVEN_SPRING: "Oven Spring",
        Attack.CRUST_CRUSHER: "Crust Crusher",
        Attack.LEECH_LOAF: "Leech Loaf",
        Attack.SECOND_RISE: "Second Rise",
        Attack.INSTANT_YEAST: "Instant Yeast",
        Attack.GLUTEN_SURGE: "Gluten Surge",
    }
    return descriptions.get(attack, attack.name)


def display_loaf(player: Player, loaf: Loaf, state, col):
    """Display loaf character with stats."""
    with col:
        # st.subheader(f"Player {player.value + 1} - 🍞")
        if player == Player.P1:
            st.subheader(f"Your Loaf")
        else:
            st.subheader(f"CPU")

        # Display loaf art (simple text representation)
        st.markdown("""
        <div style='text-align: center; font-size: 48px;'>
        🍞
        </div>
        """, unsafe_allow_html=True)

        # Display stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Salt (Attack)", loaf.salt)
        with col2:
            st.metric("Sugar (Speed)", loaf.sugar)
        with col3:
            st.metric("Flour (Hit Points)", loaf.flour)

        # Health progress bar
        current_hp = state.hp
        max_hp = loaf.flour
        health_percentage = current_hp / max_hp
        st.progress(health_percentage, text=f"HP: {current_hp}/{max_hp}")

        # Active effects
        effects = []
        if state.sprint_turns > 0:
            effects.append(f"💨 Sprint ({state.sprint_turns})")
        if state.power_up_turns > 0:
            effects.append(f"⭐ Power-Up ({state.power_up_turns})")
        if state.blocked > 0:
            effects.append("🛡️ Blocked")

        if effects:
            st.info(" | ".join(effects))


def display_move_log(col, hold):
    """Display the move log in a sidebar."""
    with col:
        hold.empty()
        if st.session_state.move_log:
            # Display moves in reverse order (most recent at top)
            log_text = "\n".join(reversed(st.session_state.move_log))
            hold.text_area("Battle History", value=log_text, height=600, disabled=True)
        else:
            hold.info("No moves yet...")


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

                # Show all attacks with 2-second display and wait for disappearance
                for player, attack in st.session_state.attack_sequence:
                    player_num = player.value + 1
                    emoji = get_attack_emoji(attack)
                    desc = get_attack_description(attack)

                    if player_num == 1:
                        with animation_placeholder.container():
                            st.info(f"🔵 Player {player_num}: {emoji} {desc}")
                    else:
                        with animation_placeholder.container():
                            st.warning(f"🔴 Player {player_num}: {emoji} {desc}")

                    time.sleep(2)
                    animation_placeholder.empty()
                    time.sleep(0.3)

                # Add moves to log
                for player, attack in st.session_state.attack_sequence:
                    player_num = player.value + 1
                    emoji = get_attack_emoji(attack)
                    desc = get_attack_description(attack)
                    st.session_state.move_log.append(f"P{player_num}: {emoji} {desc}")
                    display_move_log(log_col, log_holder)

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
                # Execute turn
                time.sleep(2)
                st.session_state.obs, move_sequence, _, _ = game.step_2p(
                    st.session_state.model1(st.session_state.obs),
                    st.session_state.model2(st.session_state.obs)
                )

                # move_sequence is a list of (Player, Attack) tuples in resolution order
                st.session_state.attack_sequence = move_sequence
                st.session_state.turn_active = True

                st.rerun()


if __name__ == "__main__":
    main()
