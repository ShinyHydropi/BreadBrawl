# Generated with Claude: https://claude.ai/share/4c6d934e-3398-430d-ad3d-22fb9b8d0d38

"""
Persistent battle scene component for BreadBrawl.

render_battle_scene() draws the *entire* battle display -- both loaves,
their names, base stats, HP bars, and active status effects (blocking,
sugar/salt boosts, sandwich trap) -- as a single HTML/CSS scene embedded via
st.iframe (raw HTML strings are auto-detected and rendered via an iframe's
srcdoc). It's meant to stay on screen for the whole battle:

  - Call it with animate=False for idle moments (initial state, "CPU is
    thinking...", or the final frame after the battle ends).
  - Call it with animate=True once per entry in BreadBrawl.step_2p's
    output_sequence to play that action out: the acting loaf lunges, the
    target shakes/flashes, a floating damage/heal number pops, and both HP
    bars drain/refill from their pre-step to post-step values.

Status badges (shield/boost/trap icons) are always drawn from the "after"
state passed in, so blocking, stat boosts, and active sandwich traps stay
visible throughout the fight, not just during the turn they were applied.
"""

import streamlit as st
from breadbrawl import Player


def _pct(value: int, maximum: int) -> float:
    maximum = max(1, maximum)
    return max(0.0, min(100.0, 100.0 * value / maximum))


def _status_badges(state):
    """Build a list of (icon, text) badges describing a player's active effects."""
    badges = []
    if state.blocked == 2:
        badges.append(("🛡️", "Blocking"))
    elif state.blocked == 1:
        badges.append(("🛡️", "Blocked"))
    if state.sprint_turns > 0:
        badges.append(("👟", f"Sugar x2 ({state.sprint_turns})"))
    if state.power_up_turns > 0:
        badges.append(("💪", f"Salt x2 ({state.power_up_turns})"))
    if state.trap_turns > 0:
        badges.append(("🕸️", f"Trapped ({state.trap_turns})"))
    return badges


def _badges_html(state, side):
    badges = _status_badges(state)
    if not badges:
        return ""
    pills = "".join(
        f'<span class="badge">{icon} {text}</span>' for icon, text in badges
    )
    return f'<div class="badges {side}">{pills}</div>'


def render_battle_scene(
    p1_name: str, p2_name: str,
    p1_loaf, p2_loaf,
    p1_before, p2_before,
    p1_after, p2_after,
    caption: str = "",
    attacker=None,
    is_environmental: bool = False,
    animate: bool = False,
    duration_ms: int = 1800,
    height: int = 380,
):
    """Render the full battle stage.

    p1_before/p2_before/p1_after/p2_after are PlayerState objects. When
    animate=False, pass the same state object for before and after (no
    HP change to animate) -- badges are drawn from the "after" state.
    """

    p1_max, p2_max = p1_loaf.flour, p2_loaf.flour
    p1_before_pct, p1_after_pct = _pct(p1_before.hp, p1_max), _pct(p1_after.hp, p1_max)
    p2_before_pct, p2_after_pct = _pct(p2_before.hp, p2_max), _pct(p2_after.hp, p2_max)

    d1 = p1_after.hp - p1_before.hp  # negative = damage, positive = heal, 0 = no change
    d2 = p2_after.hp - p2_before.hp

    attacker_is_p1 = attacker == Player.P1

    p1_classes = ["fighter", "p1"]
    p2_classes = ["fighter", "p2"]
    if animate and not is_environmental:
        if attacker_is_p1:
            p1_classes.append("lunge-right")
        else:
            p2_classes.append("lunge-left")
    if animate and d1 < 0:
        p1_classes.append("shake")
    if animate and d2 < 0:
        p2_classes.append("shake")

    def dmg_html(delta, side):
        if not animate or delta == 0:
            return ""
        sign = "+" if delta > 0 else ""
        cls = "float-heal" if delta > 0 else "float-dmg"
        return f'<div class="float-number {cls} {side}">{sign}{delta}</div>'

    show_flash = animate and (d1 < 0 or d2 < 0)
    sandwich_div = ""
    if animate and is_environmental:
        side = "left" if attacker_is_p1 else "right"
        sandwich_div = f'<div class="sandwich {side}">🥪</div>'

    p1_stat_line = f"⚔️{p1_loaf.salt} &nbsp; 👟{p1_loaf.sugar} &nbsp; ❤️{p1_loaf.flour}"
    p2_stat_line = f"⚔️{p2_loaf.salt} &nbsp; 👟{p2_loaf.sugar} &nbsp; ❤️{p2_loaf.flour}"

    html = f"""
    <div class="stage">
      <style>
        * {{ box-sizing: border-box; }}
        .stage {{
          position: relative;
          width: 100%;
          height: {height - 40}px;
          border-radius: 16px;
          background: linear-gradient(180deg, #2b2440 0%, #4b3a63 55%, #6b4f39 55%, #7a5c40 100%);
          overflow: hidden;
          font-family: 'Trebuchet MS', sans-serif;
        }}
        .caption {{
          position: absolute;
          top: 10px; left: 50%;
          transform: translateX(-50%);
          background: rgba(0,0,0,0.55);
          color: #fff;
          padding: 6px 18px;
          border-radius: 999px;
          font-size: 15px;
          font-weight: 600;
          white-space: nowrap;
          z-index: 5;
          min-height: 14px;
        }}
        .panels {{
          position: absolute;
          top: 46px; left: 4%; right: 4%;
          display: flex;
          justify-content: space-between;
          z-index: 5;
        }}
        .panel {{ width: 46%; }}
        .panel.right {{ text-align: right; }}
        .name-row {{ color: #fff; font-size: 16px; font-weight: 700; margin-bottom: 1px; }}
        .stat-row {{ color: #ffffffb0; font-size: 11px; margin-bottom: 4px; }}
        .hpbar-bg {{
          background: rgba(0,0,0,0.4);
          border: 2px solid rgba(255,255,255,0.2);
          border-radius: 8px;
          height: 14px;
          overflow: hidden;
        }}
        .hpbar-fill {{
          height: 100%;
          border-radius: 6px;
          transition: width {int(duration_ms * 0.4)}ms ease-out;
        }}
        .hpbar-fill.p1 {{ background: linear-gradient(90deg,#4fa8ff,#1e6fd9); }}
        .hpbar-fill.p2 {{ background: linear-gradient(90deg,#ff7a5c,#d9391e); margin-left: auto; }}
        .hp-text {{ color: #ffffffcc; font-size: 11px; margin-top: 2px; }}

        .badges {{
          margin-top: 6px;
          display: flex;
          flex-wrap: wrap;
          gap: 4px;
        }}
        .badges.right {{ justify-content: flex-end; }}
        .badge {{
          background: rgba(0,0,0,0.45);
          border: 1px solid rgba(255,255,255,0.25);
          color: #fff;
          font-size: 10px;
          font-weight: 600;
          padding: 2px 7px;
          border-radius: 999px;
          white-space: nowrap;
        }}

        .fighter {{
          position: absolute;
          bottom: 20px;
          font-size: 64px;
          line-height: 1;
        }}
        .fighter.p1 {{ left: 18%; filter: drop-shadow(0 0 8px rgba(79,168,255,0.5)); }}
        .fighter.p2 {{ right: 18%; filter: drop-shadow(0 0 8px rgba(255,122,92,0.5)); transform: scaleX(-1); }}

        @keyframes lungeRight {{
          0% {{ transform: translateX(0); }}
          40% {{ transform: translateX(70px); }}
          100% {{ transform: translateX(0); }}
        }}
        @keyframes lungeLeft {{
          0% {{ transform: scaleX(-1) translateX(0); }}
          40% {{ transform: scaleX(-1) translateX(70px); }}
          100% {{ transform: scaleX(-1) translateX(0); }}
        }}
        .fighter.p1.lunge-right {{ animation: lungeRight {int(duration_ms * 0.45)}ms ease-in-out 1; }}
        .fighter.p2.lunge-left {{ animation: lungeLeft {int(duration_ms * 0.45)}ms ease-in-out 1; }}

        @keyframes shakeP1 {{
          0%, 100% {{ transform: translateX(0); }}
          20% {{ transform: translateX(-8px) rotate(-4deg); }}
          40% {{ transform: translateX(8px) rotate(4deg); }}
          60% {{ transform: translateX(-6px) rotate(-3deg); }}
          80% {{ transform: translateX(6px) rotate(3deg); }}
        }}
        @keyframes shakeP2 {{
          0%, 100% {{ transform: scaleX(-1) translateX(0); }}
          20% {{ transform: scaleX(-1) translateX(-8px) rotate(4deg); }}
          40% {{ transform: scaleX(-1) translateX(8px) rotate(-4deg); }}
          60% {{ transform: scaleX(-1) translateX(-6px) rotate(3deg); }}
          80% {{ transform: scaleX(-1) translateX(6px) rotate(-3deg); }}
        }}
        .fighter.p1.shake {{ animation: shakeP1 {int(duration_ms * 0.35)}ms ease-in-out 1; animation-delay: {int(duration_ms * 0.4)}ms; }}
        .fighter.p2.shake {{ animation: shakeP2 {int(duration_ms * 0.35)}ms ease-in-out 1; animation-delay: {int(duration_ms * 0.4)}ms; }}

        .float-number {{
          position: absolute;
          bottom: 95px;
          font-size: 26px;
          font-weight: 800;
          opacity: 0;
          animation: floatUp {int(duration_ms * 0.7)}ms ease-out 1;
          animation-delay: {int(duration_ms * 0.35)}ms;
          animation-fill-mode: forwards;
          z-index: 6;
          text-shadow: 0 2px 4px rgba(0,0,0,0.6);
        }}
        .float-number.left {{ left: 20%; }}
        .float-number.right {{ right: 20%; }}
        .float-dmg {{ color: #ff5252; }}
        .float-heal {{ color: #66ff8f; }}
        @keyframes floatUp {{
          0% {{ opacity: 0; transform: translateY(10px) scale(0.8); }}
          20% {{ opacity: 1; transform: translateY(-10px) scale(1.15); }}
          100% {{ opacity: 0; transform: translateY(-60px) scale(1); }}
        }}

        .impact-flash {{
          position: absolute;
          top: 0; left: 0; right: 0; bottom: 0;
          background: #fff;
          opacity: 0;
          pointer-events: none;
          animation: flash {int(duration_ms * 0.15)}ms ease-out 1;
          animation-delay: {int(duration_ms * 0.4)}ms;
        }}
        @keyframes flash {{
          0% {{ opacity: 0; }}
          50% {{ opacity: 0.35; }}
          100% {{ opacity: 0; }}
        }}

        .sandwich {{
          position: absolute;
          top: -60px;
          font-size: 40px;
          animation: dropSandwich {int(duration_ms * 0.4)}ms ease-in 1;
          animation-fill-mode: forwards;
          z-index: 6;
        }}
        .sandwich.left {{ left: 20%; }}
        .sandwich.right {{ right: 20%; }}
        @keyframes dropSandwich {{
          0% {{ top: -60px; opacity: 1; }}
          100% {{ top: 55%; opacity: 1; }}
        }}
      </style>

      <div class="caption">{caption}</div>

      <div class="panels">
        <div class="panel left">
          <div class="name-row">{p1_name}</div>
          <div class="stat-row">{p1_stat_line}</div>
          <div class="hpbar-bg"><div class="hpbar-fill p1" id="hp1" style="width:{p1_before_pct}%;"></div></div>
          <div class="hp-text" id="hp1-text">HP: {p1_before.hp}/{p1_max}</div>
          {_badges_html(p1_after, "left")}
        </div>
        <div class="panel right">
          <div class="name-row">{p2_name}</div>
          <div class="stat-row">{p2_stat_line}</div>
          <div class="hpbar-bg"><div class="hpbar-fill p2" id="hp2" style="width:{p2_before_pct}%;"></div></div>
          <div class="hp-text" id="hp2-text">HP: {p2_before.hp}/{p2_max}</div>
          {_badges_html(p2_after, "right")}
        </div>
      </div>

      {sandwich_div}

      <div class="{' '.join(p1_classes)}">🍞</div>
      <div class="{' '.join(p2_classes)}">🍞</div>

      {'<div class="impact-flash"></div>' if show_flash else ''}

      {dmg_html(d1, 'left')}
      {dmg_html(d2, 'right')}
    </div>

    <script>
      setTimeout(function() {{
        var hp1 = document.getElementById('hp1');
        var hp2 = document.getElementById('hp2');
        var hp1t = document.getElementById('hp1-text');
        var hp2t = document.getElementById('hp2-text');
        if (hp1) hp1.style.width = '{p1_after_pct}%';
        if (hp2) hp2.style.width = '{p2_after_pct}%';
        if (hp1t) hp1t.textContent = 'HP: {p1_after.hp}/{p1_max}';
        if (hp2t) hp2t.textContent = 'HP: {p2_after.hp}/{p2_max}';
      }}, {int(duration_ms * 0.4)});
    </script>
    """

    st.iframe(html, height=height)