import streamlit as st
from pathlib import Path

st.set_page_config(page_title="ENIGMA 3D — SN63 Miner", page_icon="🔑", layout="wide")

st.markdown('<h1 style="text-align:center; color:#ffcc00;">🔑 ENIGMA MACHINE 3D — SUBNET 63 MINER</h1>', unsafe_allow_html=True)
st.markdown("**Agentic Miner with Reflection Loop + Miner Review Controls**")

# Session State
if "challenge" not in st.session_state:
    st.session_state.challenge = ""
if "current_plan" not in st.session_state:
    st.session_state.current_plan = ""
if "final_output" not in st.session_state:
    st.session_state.final_output = ""
if "trace_log" not in st.session_state:
    st.session_state.trace_log = []
if "debug_mode" not in st.session_state:
    st.session_state.debug_mode = False

st.subheader("1. Enter Challenge")
challenge = st.text_area("Main challenge", value=st.session_state.challenge, height=100)

col1, col2 = st.columns(2)
with col1:
    if st.button("Generate Plan with HyperAgent"):
        if challenge:
            st.session_state.challenge = challenge
            with st.spinner("Planning..."):
                try:
                    from agents.tools.hyperagent import run_hyperagent
                    result = run_hyperagent(task=f"Create detailed plan for: {challenge}", parallel_tasks=5)
                    st.session_state.current_plan = result.get("output", "")
                    st.success("Plan generated!")
                except Exception as e:
                    st.error(f"Error: {e}")

with col2:
    if st.button("🔬 Run Tool Study"):
        with st.spinner("Studying tools..."):
            from agents.tool_study import tool_study
            tool_study.study_all_tools()
            st.success("Tool Study completed!")

if st.session_state.current_plan:
    st.subheader("2. Approve Initial Plan")
    edited_plan = st.text_area("Edit Plan", value=st.session_state.current_plan, height=250)
    if st.button("✅ Approve Plan & Launch Chain"):
        st.session_state.current_plan = edited_plan
        st.success("Plan approved → Starting tool chain...")

        try:
            from agents.arbos_manager import ArbosManager
            arbos = ArbosManager()
            final_output, should_reloop = arbos.run(challenge)
            
            st.session_state.final_output = final_output
            st.success("Tool chain finished!")
        except Exception as e:
            st.error(f"Chain failed: {e}")

# === MINER REVIEW BEFORE SUBMISSION (Always Active) ===
if st.session_state.final_output:
    st.subheader("3. Final Miner Review Before Submission")
    reviewed = st.text_area("Final Output - Edit if needed", value=st.session_state.final_output, height=450)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Accept & Save for Submission", type="primary"):
            Path("goals/final_solution.md").write_text(reviewed)
            st.success("✅ Solution saved! Ready for subnet submission.")
            st.balloons()

    with col2:
        if st.button("🔄 Run Another Loop"):
            st.warning("Arbos will now run another full iteration.")

# Debug Mode
st.session_state.debug_mode = st.checkbox("Show Debug Trace", value=st.session_state.debug_mode)
if st.session_state.debug_mode and st.session_state.trace_log:
    st.subheader("Debug Trace")
    for line in st.session_state.trace_log:
        st.text(line)

st.caption("GOAL.md controls: miner_review_after_loop (per-loop review) | Final review is always enabled")
