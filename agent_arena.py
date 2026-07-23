# Animation generated with Claude: https://claude.ai/share/4c6d934e-3398-430d-ad3d-22fb9b8d0d38

import re
import sys
import importlib.util
import copy
from dataclasses import replace
import streamlit as st
import time
from breadbrawl import BreadBrawl, Loaf, Attack, Player
from battle_animation import render_battle_scene

def path_to_module(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None:
        raise ImportError(f"Could not find module at {path}")
    custom_module = importlib.util.module_from_spec(spec)
    sys.modules[name] = custom_module
    spec.loader.exec_module(custom_module)
    return custom_module


def init_game():
    st.session_state.game = BreadBrawl(st.session_state.p1_loaf, st.session_state.p2_loaf)
    st.session_state.game_started = True
    st.session_state.turn_active = False
    st.session_state.attack_sequence = []
    st.session_state.attack_index = 0
    st.session_state.move_log = []
    st.session_state.obs = st.session_state.game.reset()
    st.session_state.turn_start_state = {
        Player.P1: replace(st.session_state.game.states[Player.P1]),
        Player.P2: replace(st.session_state.game.states[Player.P2]),
    }

emoji_map = {
    Attack.OVEN_SPRING: "🛡️",
    Attack.CRUST_CRUSHER: "⚔️",
    Attack.LEECH_LOAF: "🩸",
    Attack.SECOND_RISE: "💚",
    Attack.INSTANT_YEAST: "👟",
    Attack.GLUTEN_SURGE: "💪",
    Attack.SANDWICH_TRAP: "🕸️"
}
def get_attack_emoji(attack: Attack) -> str:
    """Get emoji representation for attack types."""
    return emoji_map.get(attack, "")

descriptions = {
    Attack.OVEN_SPRING: "Oven Spring",
    Attack.CRUST_CRUSHER: "Crust Crusher",
    Attack.LEECH_LOAF: "Leech Loaf",
    Attack.SECOND_RISE: "Second Rise",
    Attack.INSTANT_YEAST: "Instant Yeast",
    Attack.GLUTEN_SURGE: "Gluten Surge",
    Attack.SANDWICH_TRAP: "Sandwich Trap"
}
def get_attack_description(attack: Attack) -> str:
    """Get description for attack types."""
    return descriptions.get(attack, attack.name)


def display_move_log(col, hold):
    """Display the move log in a sidebar."""
    with col:
        hold.empty()
        if st.session_state.move_log:
            # Display moves in order (first at top)
            log_text = "\n".join(st.session_state.move_log)
            hold.text_area(f"Battle History", value=log_text, height=600, disabled=True)
        else:
            hold.info("No moves yet...")


def draw_idle_scene(stage, caption):
    """Render the battle stage at rest (no attack playing), reflecting live game state."""
    game = st.session_state.game
    p1_state = game.states[Player.P1]
    p2_state = game.states[Player.P2]
    with stage.container():
        render_battle_scene(
            p1_name=st.session_state.names[Player.P1],
            p2_name=st.session_state.names[Player.P2],
            p1_loaf=st.session_state.p1_loaf, p2_loaf=st.session_state.p2_loaf,
            p1_before=p1_state, p2_before=p2_state,
            p1_after=p1_state, p2_after=p2_state,
            caption=caption,
            animate=False,
        )


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
                    player_num = player.value + 1
                    is_environmental = attack is None
                    if is_environmental:
                        emoji, desc = "🥪", "was hurt by the Sandwich Trap"
                    else:
                        emoji = get_attack_emoji(attack)
                        desc = get_attack_description(attack)

                    if is_environmental:
                        caption = f"🥪 P{player_num} is caught in the Sandwich Trap!"
                    else:
                        caption = f"P{player_num}: {emoji} {desc}"

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

                    st.session_state.move_log.append(f"P{player_num}: {emoji} {desc}")
                    display_move_log(log_col, log_holder)

                    state_before = {Player.P1: p1_after, Player.P2: p2_after}

                    time.sleep(1.8)

                if game.result:
                    # Battle ended - hold the final state on screen and show the win banner
                    draw_idle_scene(battle_stage, "🏁 Battle over!")

                    st.markdown("---")
                    if game.result == 1:
                        st.success("🎉 **Player 1 Wins!** 🎉", icon="✨")
                    else:
                        st.error("🎉 **Player 2 Wins!** 🎉", icon="☠️")

                    st.markdown("---")

                    if st.button("🔄 New Battle", key="restart_btn", use_container_width=True):
                        st.session_state.game_started = False
                        st.session_state.game = None
                        st.rerun()
                else:
                    st.session_state.turn_active = False
                    st.session_state.attack_sequence = []
                    st.rerun()
            else:
                # Between turns: keep the stage visible while the next move is decided
                draw_idle_scene(battle_stage, f"Turn {game.turn + 1} — choosing moves...")

                time.sleep(2)
                st.session_state.turn_start_state = {
                    Player.P1: replace(p1_state),
                    Player.P2: replace(p2_state),
                }
                st.session_state.obs, move_sequence, _, _ = game.step_2p(
                    st.session_state.model1(st.session_state.obs(Player.P1)),
                    st.session_state.model2(st.session_state.obs(Player.P2)),
                )

                # move_sequence is a list of (Player, Attack, PlayerState, PlayerState) tuples
                # in resolution order
                st.session_state.attack_sequence = move_sequence
                st.session_state.turn_active = True

                st.rerun()


if __name__ == "__main__":
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
        st.session_state.names = {}
        st.session_state.turn_start_state = {}

        p1_module = path_to_module(sys.argv[1], "p1_module")
        st.session_state.model1 = p1_module.agent
        st.session_state.p1_loaf = copy.copy(p1_module.loaf())
        st.session_state.names[Player.P1] = re.split(r'[./\\]', sys.argv[1])[-2]

        st.session_state.p2_loaf = Loaf.random_loaf()
        st.session_state.model2 = lambda x: st.session_state.p2_loaf.random_attack()
        st.session_state.names[Player.P2] = "CPU"
        if len(sys.argv) > 2:
            p2_module = path_to_module(sys.argv[2], "p2_module")
            st.session_state.model2 = p2_module.agent
            st.session_state.p2_loaf = copy.copy(p2_module.loaf())
            st.session_state.names[Player.P2] = re.split(r'[./\\]', sys.argv[2])[-2]
    main()