import streamlit as st
from BreadBrawl import BreadBrawl, Loaf, Attack, Player

# Page configuration
st.set_page_config(page_title="BreadBrawl", layout="wide")
st.title("🍞 BreadBrawl RPG 🍞")

# Initialize session state
if "game" not in st.session_state:
    st.session_state.game = None
    st.session_state.p1_loaf = None
    st.session_state.p2_loaf = None
    st.session_state.game_started = False

def init_game():
    """Initialize a new game with random loaves."""
    st.session_state.p1_loaf = Loaf.random_loaf()
    st.session_state.p2_loaf = Loaf.random_loaf()
    st.session_state.game = BreadBrawl(st.session_state.p1_loaf, st.session_state.p2_loaf)
    st.session_state.game.reset()
    st.session_state.game_started = True

def get_attack_emoji(attack: Attack) -> str:
    """Get emoji representation for attack types."""
    emoji_map = {
        Attack.block: "🛡️",
        Attack.slash: "⚔️",
        Attack.drain: "🩸",
        Attack.heal: "💚",
        Attack.sprint: "💨",
        Attack.power_up: "⭐",
    }
    return emoji_map.get(attack, "")

def get_attack_description(attack: Attack) -> str:
    """Get description for attack types."""
    descriptions = {
        Attack.block: "Block - Protect yourself from damage",
        Attack.slash: "Slash - Deal damage",
        Attack.drain: "Drain - Deal damage and heal",
        Attack.heal: "Heal - Restore health",
        Attack.sprint: "Sprint - Double speed for 3 turns",
        Attack.power_up: "Power-Up - Double attack for 3 turns",
    }
    return descriptions.get(attack, attack.name)

def display_loaf(player: Player, loaf: Loaf, state, col):
    """Display loaf character with stats."""
    with col:
        st.subheader(f"Player {player.value + 1} - 🍞")
        
        # Display loaf art (simple text representation)
        st.markdown("""
        <div style='text-align: center; font-size: 48px;'>
        🍞
        </div>
        """, unsafe_allow_html=True)
        
        # Display stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Attack", loaf.salt)
        with col2:
            st.metric("Speed", loaf.sugar)
        with col3:
            st.metric("Max HP", loaf.flour)
        
        # Health progress bar
        current_hp = state.hp
        max_hp = loaf.flour
        health_percentage = current_hp / max_hp
        st.progress(health_percentage, text=f"HP: {current_hp}/{max_hp}")
        
        # Active effects
        effects = []
        if state.sprint > 0:
            effects.append(f"💨 Sprint ({state.sprint})")
        if state.power_up > 0:
            effects.append(f"⭐ Power-Up ({state.power_up})")
        if state.blocked > 0:
            effects.append("🛡️ Blocked")
        
        if effects:
            st.info(" | ".join(effects))

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
        # Game screen
        game = st.session_state.game
        p1_loaf = st.session_state.p1_loaf
        p2_loaf = st.session_state.p2_loaf
        
        if game.terminated:
            # Battle ended
            p1_hp = game.states[Player.p1].hp
            p2_hp = game.states[Player.p2].hp
            
            st.markdown("---")
            if p1_hp > 0:
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
            # Active battle
            col1, col2 = st.columns(2)
            
            p1_state = game.states[Player.p1]
            p2_state = game.states[Player.p2]
            
            display_loaf(Player.p1, p1_loaf, p1_state, col1)
            display_loaf(Player.p2, p2_loaf, p2_state, col2)
            
            st.markdown("---")
            
            # Player 1 move selection
            st.subheader("⚔️ Choose Your Move (Player 1)")
            
            p1_attacks = p1_loaf.action_space()
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
                state_tuple, terminated, reward = game.step_2p(p1_choice, p2_choice)
                
                # Show what happened
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"You chose: {get_attack_emoji(p1_choice)} {get_attack_description(p1_choice)}")
                with col2:
                    st.warning(f"Opponent chose: {get_attack_emoji(p2_choice)} {get_attack_description(p2_choice)}")
                
                st.markdown("---")
                
                # Show updated stats
                st.subheader("📊 Battle Status")
                col1, col2 = st.columns(2)
                
                display_loaf(Player.p1, p1_loaf, game.states[Player.p1], col1)
                display_loaf(Player.p2, p2_loaf, game.states[Player.p2], col2)
                
                st.rerun()

if __name__ == "__main__":
    main()
