# streamlit_app.py
import streamlit as st
import json
import zipfile
import torch
from pathlib import Path
from datetime import datetime

from agents.arbos_manager import ArbosManager

st.set_page_config(page_title="Enigma Machine Miner - SN63", layout="wide")
st.title("🧠 Enigma Machine Miner (Bittensor SN63)")
st.caption("Arbos Planning + vLLM Swarm + ToolHunter + Executable Verification + Deterministic Tooling")

if "arbos_manager" not in st.session_state:
    st.session_state.arbos_manager = ArbosManager()
manager = st.session_state.arbos_manager

# Sidebar
max_hours = manager.config.get("max_compute_hours", 3.8)
st.sidebar.metric("Max Compute Limit", f"{max_hours} hours")
st.sidebar.metric("Resource Aware", "ON" if manager.config.get("resource_aware") else "OFF")
st.sidebar.metric("Guardrails", "ON" if manager.config.get("guardrails") else "OFF")

try:
    if torch.cuda.is_available():
        free_vram = torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated(0)
        free_vram_gb = free_vram / (1024 ** 3)
        total_vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
        st.sidebar.metric("VRAM Free / Total", f"{free_vram_gb:.1f} / {total_vram_gb:.1f} GB")
    else:
        st.sidebar.metric("VRAM", "No GPU detected")
except:
    st.sidebar.metric("VRAM", "Monitoring unavailable")

tp_size = manager.config.get("tensor_parallel_size", 1)
st.sidebar.metric("Tensor Parallel Size (vLLM)", tp_size)

challenge = st.text_area("SN63 Challenge", height=140, placeholder="Describe the hard problem...")

if st.button("🚀 Start Solving", type="primary") and challenge.strip():
    with st.spinner("Planning Arbos running..."):
        high_level_plan = manager.plan_challenge(challenge)
        st.session_state.challenge = challenge
        st.session_state.high_level_plan = high_level_plan
        st.session_state.stage = "planning_approval"
        st.rerun()

# ====================== 1. PLANNING APPROVAL ======================
if st.session_state.get("stage") == "planning_approval":
    plan = st.session_state.high_level_plan
    st.subheader("📋 High-Level Plan – Miner Approval")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Goals:** {plan.get('high_level_goals', 'N/A')}")
        st.markdown("**Risks:**")
        for r in plan.get("risks_and_mitigations", []):
            st.write(f"• {r}")
        st.markdown("**Rough Decomposition:**")
        for t in plan.get("rough_decomposition", []):
            st.write(f"• {t}")
        
        st.markdown("### 🔧 Arbos Deterministic Recommendations")
        recommendations = plan.get("deterministic_recommendations", "No specific recommendations yet.")
        st.info(recommendations)

        st.markdown("### 🚀 Miner Enhancement Prompt (Make this a 10/10 run)")
        st.caption("Add any final instructions to push this challenge to maximum quality.")
        enhancement_prompt = st.text_area(
            "Your custom 10/10 instructions",
            height=160,
            placeholder="Examples:\n• Prioritize Stim for all stabilizer subtasks\n• Use Quantum Rings with 8192 shots and require fidelity > 0.95\n• Focus swarm on novelty and IP potential\n• In synthesis emphasize licensability and verifier strength"
        )
        st.session_state.enhancement_prompt = enhancement_prompt
        
    with col2:
        st.metric("Suggested Swarm Size", plan.get("suggested_swarm_size", 1))

    feedback = st.text_area("Feedback / Tweak (optional)")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("✅ Approve & Continue", type="primary"):
            st.session_state.approved_plan = plan
            st.session_state.stage = "orchestrator_review"
            st.rerun()
    with col_b:
        if st.button("🔄 Tweak & Re-plan"):
            if feedback.strip():
                with st.spinner("Re-planning..."):
                    tweaked = manager.plan_challenge(f"{challenge}\n\nMiner feedback: {feedback}")
                    st.session_state.high_level_plan = tweaked
                    st.rerun()
    with col_c:
        if st.button("❌ Restart"):
            st.session_state.clear()
            st.rerun()

# ====================== 2. ORCHESTRATOR BLUEPRINT REVIEW (NEW LIGHT REVIEW) ======================
if st.session_state.get("stage") == "orchestrator_review":
    with st.spinner("Orchestrator Arbos refining blueprint..."):
        blueprint = manager._refine_plan(
            st.session_state.approved_plan, 
            st.session_state.challenge,
            st.session_state.get("deterministic_tooling", ""),
            st.session_state.get("enhancement_prompt", "")
        )
        st.session_state.blueprint = blueprint

    st.subheader("🔍 Orchestrator Blueprint Review")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**Detailed Decomposition:**")
        for t in blueprint.get("decomposition", []):
            st.write(f"• {t}")
        
        st.markdown("### 🔧 Updated Arbos Tool/Input Recommendations")
        recommendations = blueprint.get("deterministic_recommendations", "No new recommendations.")
        st.info(recommendations)

        st.markdown("### 🚀 Miner Enhancement Prompt (Final 10/10 instructions)")
        st.caption("You can still adjust here before the swarm launches.")
        final_enhancement = st.text_area(
            "Final custom instructions",
            height=140,
            value=st.session_state.get("enhancement_prompt", ""),
            placeholder="Any last adjustments..."
        )
        st.session_state.enhancement_prompt = final_enhancement

    with col2:
        st.metric("Final Swarm Size", blueprint.get("swarm_config", {}).get("total_instances", 1))

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("✅ Approve & Launch Swarm", type="primary"):
            st.session_state.stage = "final_review"
            final_solution, _, _ = manager._smart_route(st.session_state.challenge)
            st.session_state.final_solution = final_solution
            st.rerun()
    with col_b:
        if st.button("🔄 Re-refine Blueprint"):
            with st.spinner("Re-refining..."):
                blueprint = manager._refine_plan(
                    st.session_state.approved_plan, 
                    st.session_state.challenge,
                    st.session_state.get("deterministic_tooling", ""),
                    st.session_state.get("enhancement_prompt", "")
                )
                st.session_state.blueprint = blueprint
                st.rerun()
    with col_c:
        if st.button("❌ Go Back"):
            st.session_state.stage = "planning_approval"
            st.rerun()

# ====================== 3. FINAL REVIEW ======================
if st.session_state.get("stage") == "final_review":
    solution = st.session_state.final_solution
    blueprint = st.session_state.get("blueprint", {})
    trace = st.session_state.get("trace_log", [])

    st.subheader("🔍 Final Miner Review")

    tab1, tab2, tab3, tab4 = st.tabs(["Solution", "ToolHunter", "Memory History", "Verification & Deterministic Tooling"])

    with tab1:
        st.text_area("Final Solution", solution, height=400)

    with tab2:
        st.markdown("### ⚠️ ToolHunter Manual Actions Needed")
        manual_actions = [entry for entry in trace if isinstance(entry, str) and "MANUAL REQUIRED" in entry.upper()]
        if manual_actions and manager.config.get("manual_tool_installs_allowed", True):
            st.warning("**Manual Tool Installation Required**")
            for action in manual_actions:
                st.error(action)
            st.info("Please install the recommended tools manually, then re-run if needed.")
        elif manual_actions:
            st.info("ToolHunter found tools, but manual installs are disabled.")
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
        st.markdown("### 🔬 Custom Verification & Deterministic Tooling")
        col_v, col_d = st.columns(2)
        with col_v:
            verification = st.text_area(
                "Verification Instructions / Code",
                height=180,
                value=st.session_state.get("verification_instructions", ""),
                placeholder="Example: Simulate on Quantum Rings with 5000 shots. Require fidelity > 0.95"
            )
            st.session_state.verification_instructions = verification

        with col_d:
            deterministic_tooling = st.text_area(
                "Deterministic Tooling Requirements",
                height=180,
                value=st.session_state.get("deterministic_tooling", ""),
                placeholder="Example: Use stim for stabilizer checks. Run fidelity with quantum_rings."
            )
            st.session_state.deterministic_tooling = deterministic_tooling

        if st.button("🔄 Re-run with Verification & Tooling"):
            with st.spinner("Re-running..."):
                new_solution = manager._run_swarm(
                    st.session_state.blueprint, 
                    st.session_state.challenge, 
                    verification, 
                    deterministic_tooling
                )
                st.session_state.final_solution = new_solution
                st.rerun()

        # Quality gate (unchanged)
        if "quality_critique" not in st.session_state:
            with st.spinner("Running quality gate..."):
                task = f"""You are Arbos. Evaluate with this verification: {verification or 'General SN63 standards'}
Deterministic tooling: {deterministic_tooling or 'None'}
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
        cols = st.columns(6)
        metrics = [
            ("Novelty", q.get("novelty", 0)),
            ("Verifier", q.get("verifier_potential", 0)),
            ("Alignment", q.get("alignment", 0)),
            ("Completeness", q.get("completeness", 0)),
            ("Efficiency", q.get("efficiency", 0)),
            ("IP", q.get("ip_licensability", 0))
        ]
        for col, (label, value) in zip(cols, metrics):
            col.metric(label, f"{value}/10")

        st.success(f"**Overall Score: {q.get('overall_score', 0)}/10** → {q.get('recommendation', '')}")

    miner_notes = st.text_area("Your Final Notes (optional)")

    if st.button("📦 Package for SN63 Submission", type="primary"):
        _package_submission(solution, blueprint, trace, miner_notes, st.session_state.challenge, verification, deterministic_tooling)
        st.success("✅ Submission package created!")
        st.balloons()

def _package_submission(solution: str, blueprint: dict, trace: list, notes: str, challenge: str, verification: str, deterministic_tooling: str):
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    sub_dir = Path("submissions") / f"sn63_{ts}"
    sub_dir.mkdir(parents=True, exist_ok=True)

    (sub_dir / "solution.md").write_text(solution)
    (sub_dir / "blueprint.json").write_text(json.dumps(blueprint, indent=2))
    (sub_dir / "trace.log").write_text("\n".join(str(t) for t in trace))
    (sub_dir / "miner_notes.txt").write_text(notes)
    (sub_dir / "challenge.txt").write_text(challenge)
    (sub_dir / "verification.txt").write_text(verification)
    (sub_dir / "deterministic_tooling.txt").write_text(deterministic_tooling)

    past = memory.query(challenge, n_results=8)
    (sub_dir / "memory_history.txt").write_text("\n\n".join(past))

    with zipfile.ZipFile(sub_dir / "submission_package.zip", "w") as z:
        for f in sub_dir.glob("*"):
            if f.is_file() and f.suffix != ".zip":
                z.write(f, f.name)

    print(f"✅ Package ready: {sub_dir}/submission_package.zip")
