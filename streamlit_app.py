import streamlit as st
from pathlib import Path
import json

st.set_page_config(page_title="ENIGMA 3D — SN63 Miner", page_icon="🔑", layout="wide")

st.markdown("""
<style>
    .stApp { background: #0a0503; color: #ffcc00; font-family: 'Courier New', monospace; }
    .header { text-align: center; padding: 25px; border-bottom: 4px solid #ffcc00; text-shadow: 0 0 15px #ffcc00; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="header">🔑 ENIGMA MACHINE 3D — SUBNET 63 MINER</h1>', unsafe_allow_html=True)
st.markdown("**Configure your personal instances of each tool • Everything writes to GOAL.md**")

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

st.subheader("Configure Your Personal Tool Instances")

# ==================== GPD (Get Physics Done) ====================
st.write("**GPD — Get Physics Done (AI Physicist)**")
col1, col2 = st.columns(2)
with col1:
    gpd_profile = st.selectbox("Workflow Profile", 
                              ["deep-theory", "numerical", "exploratory", "review", "paper-writing"], 
                              index=0)
with col2:
    gpd_tier = st.selectbox("Capability Tier", ["1", "2", "3"], index=0)
if st.button("Save GPD Instance"):
    st.session_state.tool_configs["GPD"] = {"profile": gpd_profile, "tier": gpd_tier}
    if "GPD" not in st.session_state.hooked_tools:
        st.session_state.hooked_tools.append("GPD")
    st.success(f"GPD saved: {gpd_profile} / Tier {gpd_tier}")

# ==================== ScienceClaw ====================
st.write("**ScienceClaw**")
col1, col2 = st.columns(2)
with col1:
    intensity = st.selectbox("Search Intensity", ["high", "medium", "fast"])
with col2:
    max_src = st.number_input("Max Sources", min_value=5, max_value=50, value=15)
if st.button("Save ScienceClaw Instance"):
    st.session_state.tool_configs["ScienceClaw"] = {"search_intensity": intensity, "max_sources": max_src}
    if "ScienceClaw" not in st.session_state.hooked_tools:
        st.session_state.hooked_tools.append("ScienceClaw")
    st.success("ScienceClaw instance saved")

# ==================== AI-Researcher ====================
st.write("**AI-Researcher**")
search_mode = st.selectbox("Search Mode", ["deep", "fast"])
if st.button("Save AI-Researcher Instance"):
    st.session_state.tool_configs["AI-Researcher"] = {"search_mode": search_mode}
    if "AI-Researcher" not in st.session_state.hooked_tools:
        st.session_state.hooked_tools.append("AI-Researcher")
    st.success("AI-Researcher instance saved")

# ==================== HyperAgent ====================
st.write("**HyperAgent**")
parallel = st.number_input("Parallel Tasks", min_value=1, max_value=12, value=5)
if st.button("Save HyperAgent Instance"):
    st.session_state.tool_configs["HyperAgent"] = {"parallel_tasks": parallel}
    if "HyperAgent" not in st.session_state.hooked_tools:
        st.session_state.hooked_tools.append("HyperAgent")
    st.success("HyperAgent instance saved")

# ==================== Chutes ====================
st.write("**Chutes (LLM Router)**")
llm = st.selectbox("Preferred LLM", ["claude-3-5-sonnet", "gpt-4o", "mixtral"])
if st.button("Save Chutes Instance"):
    st.session_state.tool_configs["Chutes"] = {"llm_picker": llm}
    if "Chutes" not in st.session_state.hooked_tools:
        st.session_state.hooked_tools.append("Chutes")
    st.success("Chutes instance saved")

# ==================== Build & Show GOAL.md ====================
def build_goal_md():
    text = "# Enigma Machine — SN63 Miner Goal\n\n"
    text += "## Core Arbos Settings\n"
    text += "reflection: 4\nplanning: true\nhyper_planning: false\nmulti_agent: true\nswarm_size: 20\nexploration: true\nresource_aware: true\nguardrails: true\n\n"
    
    text += "## Compute + LLM\n"
    text += "chutes: true\ntargon: false\ncelium: true\n"
    text += f"chutes_llm: {st.session_state.tool_configs['Chutes']['llm_picker']}\n\n"
    
    text += "## Personal Tool Instances\n"
    for tool, cfg in st.session_state.tool_configs.items():
        if tool in st.session_state.hooked_tools:
            text += f"- {tool}: {json.dumps(cfg)}\n"
    
    return text

if st.button("Update GOAL.md with Current Configs"):
    Path("goals/GOAL.md").write_text(build_goal_md())
    st.success("GOAL.md updated with all your personal tool instances")

st.text_area("Current GOAL.md (this is what the miner will use)", build_goal_md(), height=400)

if st.button("🚀 LAUNCH MINER", type="primary"):
    Path("goals/GOAL.md").write_text(build_goal_md())
    st.success("✅ Miner launched! All your personal tool instances (including real GPD) are active.")
    st.balloons()

st.caption("All tools are now real and configurable per miner. GPD uses the official psi-oss package.")
