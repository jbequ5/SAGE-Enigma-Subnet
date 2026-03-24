import streamlit as st
from pathlib import Path
import json

# Import the 3D component (if you're using the custom one) or just use the HTML for now
# For simplicity, we'll use the HTML demo embedded for now

st.set_page_config(page_title="ENIGMA 3D — SN63 Miner", page_icon="🔑", layout="wide")

st.markdown("""
<style>
    .stApp { background: #0a0503; color: #ffcc00; font-family: 'Courier New', monospace; }
    .header { text-align: center; padding: 20px; border-bottom: 4px solid #ffcc00; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="header">🔑 ENIGMA MACHINE 3D — SUBNET 63 MINER</h1>', unsafe_allow_html=True)

# Session State
if "hooked_tools" not in st.session_state:
    st.session_state.hooked_tools = []
if "tool_configs" not in st.session_state:
    st.session_state.tool_configs = {
        "ScienceClaw": {"search_intensity": "high", "max_sources": 15},
        "GPD": {"profile": "deep-theory", "tier": "1"},
        "AI-Researcher": {"search_mode": "deep"},
        "HyperAgent": {"parallel_tasks": 5},
        "Chutes": {"llm_picker": "claude-3-5-sonnet"}
    }
if "goal_md" not in st.session_state:
    st.session_state.goal_md = ""

# 3D Scene (your current HTML demo can be embedded here later)
st.markdown("### 3D Bunker Interface")
st.info("Click tools in the 3D scene to configure your personal instances (demo)")

# Tool Config (simplified for now - you can embed the full HTML if you want)
col1, col2 = st.columns(2)

with col1:
    tool = st.selectbox("Select Tool to Configure", ["ScienceClaw", "GPD", "AI-Researcher", "HyperAgent", "Chutes"])
    if tool == "GPD":
        profile = st.selectbox("Workflow Profile", ["deep-theory", "numerical", "exploratory", "review", "paper-writing"], index=0)
        tier = st.selectbox("Capability Tier", ["1", "2", "3"], index=0)
        if st.button("Save GPD Config"):
            st.session_state.tool_configs["GPD"] = {"profile": profile, "tier": tier}
            st.success(f"GPD saved: {profile} / Tier {tier}")

with col2:
    if st.button("Show Current GOAL.md"):
        update_goal_md()
        st.text_area("Current GOAL.md", st.session_state.goal_md, height=400)

def update_goal_md():
    text = "# Enigma Machine — SN63 Miner Goal\n\n"
    text += "## Core Arbos Settings\n"
    text += "reflection: 4\nplanning: true\nhyper_planning: false\nmulti_agent: true\nswarm_size: 20\nexploration: true\nresource_aware: true\nguardrails: true\n\n"
    text += "## Compute + LLM\n"
    text += "chutes: true\ntargon: false\ncelium: true\n"
    text += f"chutes_llm: {st.session_state.tool_configs['Chutes']['llm_picker']}\n\n"
    text += "## Personal Tool Instances\n"
    
    for tool, cfg in st.session_state.tool_configs.items():
        if tool in st.session_state.hooked_tools or tool == "GPD":
            text += f"- {tool}: {json.dumps(cfg)}\n"
    
    st.session_state.goal_md = text

if st.button("Update GOAL.md with Current Configs"):
    update_goal_md()
    st.success("GOAL.md updated!")

if st.button("🚀 LAUNCH MINER"):
    update_goal_md()
    Path("goals/GOAL.md").write_text(st.session_state.goal_md)
    st.success("Miner launched with your personal tool instances!")
    st.balloons()

st.caption("Real Get Physics Done is now integrated. GPD profile and tier are passed to arbos_manager.py")
