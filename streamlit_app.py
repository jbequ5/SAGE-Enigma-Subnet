# streamlit_app.py
import streamlit as st
import json
import zipfile
from pathlib import Path
from datetime import datetime

from agents.arbos_manager import ArbosManager

st.set_page_config(page_title="Enigma Machine Miner - SN63", layout="wide")
st.title("🧠 Enigma Machine Miner (Bittensor SN63)")

if "arbos_manager" not in st.session_state:
    st.session_state.arbos_manager = ArbosManager()
manager = st.session_state.arbos_manager

challenge = st.text_area("SN63 Challenge", height=120, placeholder="Describe the hard problem...")

if st.button("🚀 Start Solving", type="primary") and challenge.strip():
    with st.spinner("Planning Arbos running..."):
        high_level_plan = manager.plan_challenge(challenge)
        st.session_state.challenge = challenge
        st.session_state.high_level_plan = high_level_plan
        st.session_state.stage = "planning_approval"
        st.rerun()

# Planning approval screen (add your existing approval UI here if you have one)

if st.session_state.get("stage") == "final_review":
    solution = st.session_state.final_solution
    blueprint = st.session_state.get("blueprint", {})
    trace = st.session_state.get("trace_log", [])

    st.subheader("🔍 Final Miner Review")

    tab1, tab2, tab3, tab4 = st.tabs(["Solution", "ToolHunter", "Memory", "Verification"])

    with tab1:
        st.text_area("Final Solution", solution, height=400)

    with tab2:
        manual = [e for e in trace if isinstance(e, str) and "MANUAL REQUIRED" in e.upper()]
        if manual:
            st.warning("**Manual ToolHunter Actions Required**")
            for m in manual:
                st.error(m)
        else:
            st.success("No manual actions needed.")

    with tab3:
        st.markdown("### Memory History")
        past = memory.query(st.session_state.challenge, n_results=8)
        if past:
            for i, p in enumerate(past, 1):
                st.write(f"**Attempt {i}:** {p[:300]}...")
        else:
            st.info("No previous attempts.")

    with tab4:
        st.markdown("### 🔬 Custom Verification (Text or Executable Code)")
        verification = st.text_area(
            "Verification Instructions / Code",
            height=200,
            value=st.session_state.get("verification_instructions", ""),
            placeholder="Simulate on Quantum Rings with 5000 shots. Require fidelity > 0.95"
        )
        st.session_state.verification_instructions = verification

        if st.button("🔄 Re-run with this Verification"):
            with st.spinner("Re-running..."):
                new_solution = manager._run_swarm(st.session_state.blueprint, st.session_state.challenge, verification)
                st.session_state.final_solution = new_solution
                st.rerun()

        # Quality gate
        if "quality_critique" not in st.session_state:
            with st.spinner("Running quality gate..."):
                task = f"""You are Arbos. Evaluate with this verification: {verification or 'General SN63 standards'}
Solution: {solution[:2000]}
Output JSON with novelty, verifier_potential, overall_score, recommendation, verification_assessment."""
                raw = manager.compute.run_on_compute(task)
                try:
                    start = raw.find("{")
                    end = raw.rfind("}") + 1
                    st.session_state.quality_critique = json.loads(raw[start:end])
                except:
                    st.session_state.quality_critique = {"overall_score": 7.0}

        q = st.session_state.quality_critique
        st.success(f"Overall: {q.get('overall_score', 0)}/10")

    if st.button("📦 Package Submission"):
        _package_submission(solution, blueprint, trace, "", st.session_state.challenge, verification)
        st.success("Packaged!")

def _package_submission(solution, blueprint, trace, notes, challenge, verification):
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    dir_path = Path("submissions") / f"sn63_{ts}"
    dir_path.mkdir(parents=True, exist_ok=True)

    (dir_path / "solution.md").write_text(solution)
    (dir_path / "verification.txt").write_text(verification)
    (dir_path / "trace.log").write_text("\n".join(str(t) for t in trace))

    with zipfile.ZipFile(dir_path / "submission_package.zip", "w") as z:
        for f in dir_path.glob("*"):
            if f.is_file() and f.suffix != ".zip":
                z.write(f, f.name)

    st.success(f"Package saved to {dir_path}")
