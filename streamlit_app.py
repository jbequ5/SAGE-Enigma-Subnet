# streamlit_app.py
import streamlit as st
import json
import zipfile
from pathlib import Path
from datetime import datetime

from agents.arbos_manager import ArbosManager

st.set_page_config(page_title="Enigma Machine Miner - SN63", layout="wide")
st.title("🧠 Enigma Machine Miner (Bittensor SN63)")
st.caption("Intelligent Planning Arbos + Dynamic Swarm + ToolHunter + Resource Aware")

if "arbos_manager" not in st.session_state:
    st.session_state.arbos_manager = ArbosManager()
manager = st.session_state.arbos_manager

# Sidebar
max_hours = manager.config.get("max_compute_hours", 3.8)
st.sidebar.metric("Max Compute Limit", f"{max_hours} hours")
st.sidebar.metric("Resource Aware", "Enabled" if manager.config.get("resource_aware") else "Disabled")
st.sidebar.metric("Guardrails", "Enabled" if manager.config.get("guardrails") else "Disabled")

challenge = st.text_area("SN63 Challenge Description", height=140, 
                        placeholder="Describe the hard problem...")

if st.button("🚀 Start Solving", type="primary") and challenge.strip():
    with st.spinner("Planning Arbos is thinking..."):
        high_level_plan = manager.plan_challenge(challenge)
        st.session_state.challenge = challenge
        st.session_state.high_level_plan = high_level_plan
        st.session_state.stage = "planning_approval"
        st.rerun()

# ====================== PLANNING APPROVAL ======================
if st.session_state.get("stage") == "planning_approval":
    plan = st.session_state.high_level_plan
    st.subheader("📋 High-Level Plan – Miner Approval")
    # (keep your existing approval UI code here - it remains unchanged)

# ====================== FINAL REVIEW ======================
if st.session_state.get("stage") == "final_review":
    solution = st.session_state.final_solution
    blueprint = st.session_state.get("blueprint", {})
    trace = st.session_state.get("trace_log", [])

    st.subheader("🔍 Final Miner Review")

    tab1, tab2, tab3, tab4 = st.tabs(["Solution", "ToolHunter Manual Actions", "Memory History", "Quality Gate"])

    with tab1:
        st.text_area("Final Synthesized Solution", solution, height=450)

    with tab2:
        st.markdown("### ⚠️ ToolHunter Manual Actions Needed")
        manual_actions = [entry for entry in trace if isinstance(entry, str) and "MANUAL REQUIRED" in entry.upper()]
        
        if manual_actions and manager.config.get("manual_tool_installs_allowed", True):
            st.warning("**Manual Tool Installation Required**")
            for action in manual_actions:
                st.error(action)
            st.info("Please install the recommended tools manually, then re-run the challenge if the improvement is significant.")
        elif manual_actions:
            st.info("ToolHunter found tools, but manual installs are disabled in config.")
        else:
            st.success("✅ No manual ToolHunter actions required.")

    with tab3:
        st.markdown("### Memory History (Re-loop Learning)")
        past = memory.query(st.session_state.challenge, n_results=8)
        if past:
            for i, p in enumerate(past, 1):
                st.write(f"**Attempt {i}:** {p[:300]}...")
        else:
            st.info("No previous attempts in memory.")

    with tab4:
        # Your existing quality gate code goes here
        pass

    miner_notes = st.text_area("Your Final Notes (optional)")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📦 Package for SN63 Submission", type="primary"):
            _package_submission(solution, blueprint, trace, miner_notes, st.session_state.challenge)
            st.success("Submission package created!")
            st.balloons()

# Package function (add at the bottom)
def _package_submission(solution: str, blueprint: dict, trace: list, notes: str, challenge: str):
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    sub_dir = Path("submissions") / f"sn63_{ts}"
    sub_dir.mkdir(parents=True, exist_ok=True)

    (sub_dir / "solution.md").write_text(solution)
    (sub_dir / "blueprint.json").write_text(json.dumps(blueprint, indent=2))
    (sub_dir / "trace.log").write_text("\n".join(str(t) for t in trace))
    (sub_dir / "miner_notes.txt").write_text(notes)
    (sub_dir / "challenge.txt").write_text(challenge)

    past = memory.query(challenge, n_results=8)
    (sub_dir / "memory_history.txt").write_text("\n\n".join(past))

    with zipfile.ZipFile(sub_dir / "submission_package.zip", "w") as z:
        for f in sub_dir.glob("*"):
            if f.is_file() and f.suffix != ".zip":
                z.write(f, f.name)

    print(f"✅ Package ready: {sub_dir}/submission_package.zip")
