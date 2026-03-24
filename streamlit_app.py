import streamlit as st
from pathlib import Path
import json

st.set_page_config(page_title="ENIGMA 3D — SN63 Miner", page_icon="🔑", layout="wide")

st.markdown('<h1 style="text-align:center; color:#ffcc00;">🔑 ENIGMA MACHINE 3D — SUBNET 63 MINER</h1>', unsafe_allow_html=True)
st.markdown("**Sequential Tool Chain with Human-in-the-Loop Planning**")

# Session State
if "hooked_tools" not in st.session_state:
    st.session_state.hooked_tools = []
if "tool_configs" not in st.session_state:
    st.session_state.tool_configs = {
        "ScienceClaw": {"search_intensity": "high", "max_sources": 15},
        "GPD": {"profile": "deep-theory", "tier": "1"},
        "AI-Researcher": {"search_mode": "deep"},
        "AutoResearch": {"depth": "medium", "iterations": 3},
        "HyperAgent": {"parallel_tasks": 5},
        "Chutes": {"llm_picker": "claude-3-5-sonnet"}
    }
if "challenge" not in st.session_state:
    st.session_state.challenge = ""
if "current_plan" not in st.session_state:
    st.session_state.current_plan = ""

st.subheader("1. Enter the Challenge")
challenge = st.text_area("What is the main challenge/task for today's miner?", 
                        value=st.session_state.challenge, height=120)

if st.button("Generate Detailed Plan with HyperAgent"):
    if not challenge:
        st.error("Please enter a challenge.")
    else:
        st.session_state.challenge = challenge
        with st.spinner("HyperAgent is creating a structured plan..."):
            try:
                from agents.tools.hyperagent import run as run_hyperagent
                cfg = st.session_state.tool_configs.get("HyperAgent", {})
                plan_task = f"""Create a detailed execution plan for: {challenge}

Output format:
1. Overall Strategy
2. Tool Sequence (AI-Researcher → AutoResearch → GPD → ScienceClaw)
3. Specific Prompt for each tool
4. Expected Output

Build tools cumulatively — each prompt should use results from previous tools."""
                result = run_hyperagent(task=plan_task, parallel_tasks=cfg.get("parallel_tasks", 5))
                st.session_state.current_plan = result.get("output", "No plan generated.")
                st.success("Plan generated! Review below.")
            except Exception as e:
                st.error(f"HyperAgent failed: {e}")

if st.session_state.current_plan:
    st.subheader("2. Review & Edit HyperAgent Plan")
    edited_plan = st.text_area("HyperAgent Plan (edit if needed)", 
                              value=st.session_state.current_plan, height=350)
    if st.button("✅ Approve Plan & Run Tool Chain"):
        st.session_state.current_plan = edited_plan
        st.success("Plan approved. Tool chain will now run sequentially.")

# Tool Configuration
st.subheader("3. Configure Your Personal Tool Instances")

# AutoResearch Config
st.write("**AutoResearch (karpathy)**")
col1, col2 = st.columns(2)
with col1:
    depth = st.selectbox("Depth", ["shallow", "medium", "deep"], index=1)
with col2:
    iterations = st.number_input("Iterations", min_value=1, max_value=8, value=3)
if st.button("Save AutoResearch Instance"):
    st.session_state.tool_configs["AutoResearch"] = {"depth": depth, "iterations": iterations}
    if "AutoResearch" not in st.session_state.hooked_tools:
        st.session_state.hooked_tools.append("AutoResearch")
    st.success("AutoResearch instance saved")

# GPD Config
st.write("**GPD (Get Physics Done)**")
col_g1, col_g2 = st.columns(2)
with col_g1:
    profile = st.selectbox("Workflow Profile", ["deep-theory", "numerical", "exploratory", "review", "paper-writing"])
with col_g2:
    tier = st.selectbox("Capability Tier", ["1", "2", "3"])
if st.button("Save GPD Instance"):
    st.session_state.tool_configs["GPD"] = {"profile": profile, "tier": tier}
    if "GPD" not in st.session_state.hooked_tools:
        st.session_state.hooked_tools.append("GPD")
    st.success("GPD saved")

# Other tools can be added similarly

def build_goal_md():
    text = "# Enigma Machine — SN63 Miner Goal\n\n"
    text += f"## Challenge\n{st.session_state.challenge}\n\n"
    text += f"## Approved HyperAgent Plan\n{st.session_state.current_plan}\n\n"
    text += "## Core Arbos Settings\nreflection: 4\nplanning: true\nhyper_planning: true\nmulti_agent: true\nswarm_size: 20\nexploration: true\nresource_aware: true\nguardrails: true\n\n"
    text += "## Personal Tool Instances\n"
    for tool, cfg in st.session_state.tool_configs.items():
        if tool in st.session_state.hooked_tools:
            text += f"- {tool}: {json.dumps(cfg)}\n"
    return text

if st.button("Update GOAL.md"):
    Path("goals/GOAL.md").write_text(build_goal_md())
    st.success("GOAL.md updated")

st.text_area("Current GOAL.md", build_goal_md(), height=400)

if st.button("🚀 LAUNCH MINER", type="primary"):
    Path("goals/GOAL.md").write_text(build_goal_md())
    st.success("Miner launched with sequential tool chain and human-approved plan!")
    st.balloons()
