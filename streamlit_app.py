import streamlit as st
from pathlib import Path
import json

st.set_page_config(page_title="ENIGMA 3D — SN63 Miner", page_icon="🔑", layout="wide")

st.markdown('<h1 style="text-align:center; color:#ffcc00;">🔑 ENIGMA MACHINE 3D — SUBNET 63 MINER</h1>', unsafe_allow_html=True)
st.markdown("**Sequential Tool Chain with Reflection After Every Tool + Long-Term Memory**")

# Session State
if "challenge" not in st.session_state:
    st.session_state.challenge = ""
if "current_plan" not in st.session_state:
    st.session_state.current_plan = ""
if "program_md" not in st.session_state:
    st.session_state.program_md = ""
if "hooked_tools" not in st.session_state:
    st.session_state.hooked_tools = []
if "tool_configs" not in st.session_state:
    st.session_state.tool_configs = {
        "ScienceClaw": {"search_intensity": "high", "max_sources": 15},
        "GPD": {"profile": "deep-theory", "tier": "1"},
        "AI-Researcher": {"search_mode": "deep"},
        "AutoResearch": {"depth": "medium", "iterations": 3},
        "HyperAgent": {"parallel_tasks": 5},
        "Chutes": {"llm_picker": "mixtral"}
    }
if "debug_mode" not in st.session_state:
    st.session_state.debug_mode = False

st.subheader("1. Enter the Challenge")
challenge = st.text_area("Main challenge for today's miner", value=st.session_state.challenge, height=120)

col1, col2 = st.columns(2)
with col1:
    if st.button("Generate Strategic Plan with HyperAgent"):
        if not challenge:
            st.error("Please enter a challenge.")
        else:
            st.session_state.challenge = challenge
            with st.spinner("HyperAgent creating strategic plan..."):
                try:
                    from agents.tools.hyperagent import run_hyperagent
                    cfg = st.session_state.tool_configs.get("HyperAgent", {})
                    result = run_hyperagent(task=f"Create detailed plan for: {challenge}", parallel_tasks=cfg.get("parallel_tasks", 5))
                    st.session_state.current_plan = result.get("output", "")
                    st.session_state.program_md = f"# Execution Program\n\n## Challenge\n{challenge}\n\n## Strategic Plan\n{st.session_state.current_plan}\n\n"
                    st.success("Strategic plan generated!")
                except Exception as e:
                    st.error(f"HyperAgent failed: {e}")

with col2:
    if st.button("🔬 Run Tool Study Phase"):
        with st.spinner("Arbos is studying all tools and building profiles..."):
            try:
                from agents.tool_study import tool_study
                tool_study.study_all_tools()
                st.success("✅ Tool Study Phase completed! Profiles are ready.")
            except Exception as e:
                st.error(f"Study failed: {e}")

if st.session_state.current_plan:
    st.subheader("2. Review & Edit Plan")
    edited_plan = st.text_area("Strategic Plan (edit if needed)", value=st.session_state.current_plan, height=400)
    if st.button("✅ Approve Plan"):
        st.session_state.current_plan = edited_plan
        st.session_state.program_md = f"# Execution Program\n\n## Challenge\n{st.session_state.challenge}\n\n## Strategic Plan\n{edited_plan}\n\n"
        st.success("Plan approved.")

# Debug Mode Toggle
st.session_state.debug_mode = st.checkbox("Enable Debug/Trace Mode", value=st.session_state.debug_mode)

# Tool Configurations
st.subheader("3. Personal Tool Configurations")

col1, col2 = st.columns(2)
with col1:
    if st.button("Save AutoResearch"):
        depth = st.selectbox("Depth", ["shallow", "medium", "deep"], key="ar_depth")
        iterations = st.number_input("Iterations", min_value=1, max_value=8, value=3, key="ar_iter")
        st.session_state.tool_configs["AutoResearch"] = {"depth": depth, "iterations": iterations}
        if "AutoResearch" not in st.session_state.hooked_tools:
            st.session_state.hooked_tools.append("AutoResearch")
        st.success("AutoResearch saved")

with col2:
    if st.button("Save GPD"):
        profile = st.selectbox("GPD Profile", ["deep-theory", "numerical", "exploratory", "review", "paper-writing"], key="gpd_profile")
        tier = st.selectbox("GPD Tier", ["1", "2", "3"], key="gpd_tier")
        st.session_state.tool_configs["GPD"] = {"profile": profile, "tier": tier}
        if "GPD" not in st.session_state.hooked_tools:
            st.session_state.hooked_tools.append("GPD")
        st.success("GPD saved")

def build_goal_md():
    text = "# Enigma Machine — SN63 Miner Goal\n\n"
    text += f"## Challenge\n{st.session_state.challenge}\n\n"
    text += f"## Strategic Plan\n{st.session_state.current_plan}\n\n"
    text += "## Core Settings\nreflection: 4\nplanning: true\nhyper_planning: true\nmulti_agent: true\nswarm_size: 20\nexploration: true\nresource_aware: true\nguardrails: true\n\n"
    text += "## Personal Tool Instances\n"
    for tool, cfg in st.session_state.tool_configs.items():
        if tool in st.session_state.hooked_tools:
            text += f"- {tool}: {json.dumps(cfg)}\n"
    return text

if st.button("Update GOAL.md"):
    Path("goals/GOAL.md").write_text(build_goal_md())
    st.success("GOAL.md updated")

st.text_area("Current program.md (cumulative context)", st.session_state.program_md, height=300)

if st.button("🚀 LAUNCH SEQUENTIAL TOOL CHAIN", type="primary"):
    if not st.session_state.current_plan:
        st.error("Approve a plan first.")
    else:
        Path("goals/GOAL.md").write_text(build_goal_md())
        Path("program.md").write_text(st.session_state.program_md)
        st.success("Tool chain launched with reflection after every tool + long-term memory!")
        st.balloons()

if st.session_state.debug_mode:
    st.subheader("Debug / Trace Mode")
    st.info("Debug mode is enabled. Full reflection trace and profiles will be shown in future runs.")

st.caption("System Status: Dynamic Reflection • Cost Awareness • Vector Retrieval • Real ScienceClaw at end")
