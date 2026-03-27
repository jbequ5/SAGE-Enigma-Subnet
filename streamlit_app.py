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
st.caption("Compute Setup → Two-Stage Review → Parallel Swarm → Verification")

if "arbos_manager" not in st.session_state:
    st.session_state.arbos_manager = ArbosManager()
manager = st.session_state.arbos_manager

# ====================== PRE-RUN TOOLHUNTER DISCOVERY ======================
st.sidebar.title("🛠️ ToolHunter Setup")
if st.sidebar.button("🔍 Pre-Run ToolHunter Discovery (using GOAL.md)"):
    with st.spinner("Analyzing GOAL.md and discovering relevant tools/models..."):
        goal_path = "goals/killer_base.md"
        try:
            with open(goal_path, "r") as f:
                goal_content = f.read()
        except Exception as e:
            st.error(f"Could not read GOAL.md: {e}")
            st.stop()

        discovered = manager.discover_from_goal(goal_content)
        
        if discovered:
            st.success(f"✅ Discovered and added {len(discovered)} relevant tools/models")
            st.info("Registry updated. ToolHunter will now use these during runs.")
        else:
            st.warning("No strong matches found.")
        st.rerun()

# ====================== STAGE 0: COMPUTE SETUP ======================
if "compute_source" not in st.session_state:
    st.subheader("🔌 Compute Setup")

    compute_option = st.radio(
        "Choose compute source:",
        options=[
            "Local GPU (if available)",
            "Chutes (decentralized GPUs - recommended if no local GPU)",
            "Already running (use existing endpoint)",
            "Custom / Hosted (RunPod, Vast, AWS, etc.)"
        ],
        index=1
    )

    endpoint = None

    if compute_option == "Chutes (decentralized GPUs - recommended if no local GPU)":
        st.markdown("### 🚀 Go to Chutes to rent compute")
        st.markdown("[Open Chutes Dashboard](https://chutes.ai)")
        endpoint = st.text_input("Chutes Endpoint URL", placeholder="https://your-chutes-endpoint.chutes.ai")

    elif compute_option == "Already running (use existing endpoint)":
        endpoint = st.text_input("Existing compute endpoint URL", placeholder="https://my-hosted-miner.com/api")

    elif compute_option == "Custom / Hosted (RunPod, Vast, AWS, etc.)":
        endpoint = st.text_input("Custom compute endpoint URL", placeholder="https://...")

    if st.button("Continue with this compute source", type="primary"):
        source_map = {
            "Local GPU (if available)": "local",
            "Chutes (decentralized GPUs - recommended if no local GPU)": "chutes",
            "Already running (use existing endpoint)": "already_running",
            "Custom / Hosted (RunPod, Vast, AWS, etc.)": "custom"
        }
        st.session_state.compute_source = source_map[compute_option]
        st.session_state.custom_endpoint = endpoint if endpoint and endpoint.strip() else None

        manager.compute.set_compute_source(st.session_state.compute_source, st.session_state.custom_endpoint)
        st.session_state.stage = "planning_approval"
        st.rerun()

    st.stop()

# ====================== STAGE 1: HIGH-LEVEL PLANNING APPROVAL ======================
if st.session_state.get("stage") == "planning_approval":
    if "challenge" not in st.session_state:
        st.session_state.challenge = st.text_area("SN63 Challenge", height=120, placeholder="Describe the hard problem...")

    with st.spinner("Planning Arbos running..."):
        plan = manager.plan_challenge(st.session_state.challenge)
        st.session_state.high_level_plan = plan

    st.subheader("📋 Stage 1: High-Level Plan – Strategic Review")

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
        st.info(plan.get("deterministic_recommendations", "No specific recommendations yet."))

        st.markdown("### 🚀 **Miner Enhancement Prompt (10/10 Instructions)**")
        st.caption("**Required / Highly Recommended** — Tell Arbos your strategy, model preferences, tool priorities, novelty focus, etc.")
        enhancement_prompt = st.text_area(
            "Your strategic instructions",
            height=160,
            placeholder="Examples:\n• Maximize novelty and IP potential\n• Use TheBloke/Llama-3-70B-Instruct for synthesis\n• Prioritize symbolic tools and verifier strength\n• Focus on Quantum Rings fidelity"
        )
        st.session_state.enhancement_prompt = enhancement_prompt

    with col2:
        st.metric("Suggested Swarm Size", plan.get("suggested_swarm_size", 1))

    feedback = st.text_area("Feedback / Tweak (optional)")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("✅ Approve High-Level Plan & Continue", type="primary"):
            st.session_state.approved_plan = plan
            st.session_state.stage = "orchestrator_review"
            st.rerun()
    with col_b:
        if st.button("🔄 Re-plan"):
            if feedback.strip():
                with st.spinner("Re-planning..."):
                    tweaked = manager.plan_challenge(f"{st.session_state.challenge}\n\nMiner feedback: {feedback}")
                    st.session_state.high_level_plan = tweaked
                    st.rerun()
    with col_c:
        if st.button("❌ Restart"):
            st.session_state.clear()
            st.rerun()

# ====================== STAGE 2: ORCHESTRATOR BLUEPRINT REVIEW ======================
if st.session_state.get("stage") == "orchestrator_review":
    with st.spinner("Orchestrator Arbos creating detailed blueprint..."):
        blueprint = manager._refine_plan(
            st.session_state.approved_plan, 
            st.session_state.challenge,
            st.session_state.get("deterministic_tooling", ""),
            st.session_state.get("enhancement_prompt", "")
        )
        st.session_state.blueprint = blueprint

    st.subheader("📋 Stage 2: Orchestrator Blueprint – Tactical Review")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**Detailed Decomposition:**")
        for t in blueprint.get("decomposition", []):
            st.write(f"• {t}")
        
        st.markdown("### 🔧 Updated Tool Recommendations")
        st.info(blueprint.get("deterministic_recommendations", "No new recommendations."))

        st.markdown("### 🚀 **Final Miner Enhancement Prompt**")
        st.caption("**Last chance** to add model requests, tool priorities, or strategic adjustments.")
        final_enhancement = st.text_area(
            "Final instructions",
            height=140,
            value=st.session_state.get("enhancement_prompt", ""),
            placeholder="Any last tactical adjustments or model requests..."
        )
        st.session_state.enhancement_prompt = final_enhancement

    with col2:
        st.metric("Final Swarm Size", blueprint.get("swarm_config", {}).get("total_instances", 1))

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("✅ Approve Blueprint & Launch Swarm", type="primary"):
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
        if st.button("❌ Go Back to High-Level Plan"):
            st.session_state.stage = "planning_approval"
            st.rerun()

# ====================== FINAL REVIEW ======================
if st.session_state.get("stage") == "final_review":
    solution = st.session_state.final_solution
    blueprint = st.session_state.get("blueprint", {})
    trace = st.session_state.get("trace_log", [])

    st.subheader("🔍 Final Miner Review")

    tab1, tab2, tab3, tab4 = st.tabs(["Solution", "ToolHunter", "Memory History", "Verification & Deterministic Tooling"])

    with tab1:
        st.text_area("Final Solution", solution, height=400)

    with tab2:
        st.markdown("### ⚠️ ToolHunter Results & Manual Actions")
        manual_actions = [entry for entry in trace if isinstance(entry, str) and ("MANUAL REQUIRED" in entry.upper() or "ToolHunter found" in entry)]
        
        if manual_actions:
            st.warning("**ToolHunter Recommendations Found**")
            for action in manual_actions:
                st.info(action)
                if "found specialized" in action.lower() or "model:" in action.lower():
                    if st.button("🔄 Apply Recommended Model/Tool", key=action[:50]):
                        st.session_state.deterministic_tooling = action
                        st.success("✅ Recommendation copied to Deterministic Tooling field. You can now re-run.")
                        st.rerun()
        else:
            st.success("✅ No ToolHunter actions required.")

    with tab3:
        st.markdown("### Memory History (Re-loop Learning)")
        past = memory.query(st.session_state.challenge, n_results=8)
        if past:
            for i, p in enumerate(past, 1):
                st.write(f"**Attempt {i}:** {p[:300]}...")
        else:
            st.info("No previous attempts in memory.")

    with tab4:
        st.markdown("### 🔬 **Verification & Deterministic Tooling**")
        st.caption("**Important:** Provide any custom verification code or tool requirements here.")

        col_v, col_d = st.columns(2)
        with col_v:
            st.markdown("**Verification Instructions / Code**")
            verification = st.text_area(
                "",
                height=180,
                value=st.session_state.get("verification_instructions", ""),
                placeholder="Example: Simulate on Quantum Rings with 5000 shots. Require fidelity > 0.95"
            )
            st.session_state.verification_instructions = verification

        with col_d:
            st.markdown("**Deterministic Tooling Requirements**")
            deterministic_tooling = st.text_area(
                "",
                height=180,
                value=st.session_state.get("deterministic_tooling", ""),
                placeholder="Example: Use stim for stabilizer checks. Prefer symbolic fallbacks. Use TheBloke/Llama-3-70B-Instruct for synthesis."
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

        # Quality gate
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
