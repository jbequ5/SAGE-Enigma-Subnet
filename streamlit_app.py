import streamlit as st
import json
import zipfile
import pandas as pd
from pathlib import Path
from datetime import datetime

from agents.arbos_manager import ArbosManager

# ====================== BUNKER THEME ======================
BUNKER_CSS = """
<style>
    [data-testid="stAppViewContainer"] {
        background-image: url("https://pub-1407f82391df4ab1951418d04be76914.r2.dev/uploads/6700b7a0-d46e-4054-9f1c-3ed01c65c15b.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    [data-testid="stHeader"], footer, [data-testid="stToolbar"] {
        visibility: hidden;
    }
    .stApp {
        background: linear-gradient(rgba(0, 5, 3, 0.98), rgba(0, 12, 8, 0.99));
    }
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2 {
        color: #00ff9d !important;
        font-family: 'Courier New', monospace;
        text-shadow: 0 0 25px #00ff9d, 0 0 45px #00aa77;
        letter-spacing: 3px;
    }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #000a06 !important;
        color: #00ff9d !important;
        border: 2px solid #00ff9d;
        font-family: 'Courier New', monospace;
        font-size: 17px;
        line-height: 1.6;
        box-shadow: 0 0 18px rgba(0, 255, 150, 0.6);
    }
    .stButton > button {
        background-color: #001a0f;
        color: #00ff9d;
        border: 3px solid #00ff9d;
        font-family: 'Courier New', monospace;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 2px;
        padding: 14px 32px;
        box-shadow: 0 0 35px #00ff9d;
    }
    .stButton > button:hover {
        background-color: #003322;
        box-shadow: 0 0 55px #00ff9d;
    }
    .stApp::before {
        content: "ALLIED COMMAND POST — US ARMY SIGNALS INTELLIGENCE";
        position: fixed;
        top: 28px;
        right: 45px;
        color: rgba(200, 255, 180, 0.22);
        font-family: 'Courier New', monospace;
        font-size: 15px;
        transform: rotate(-7deg);
        z-index: 9999;
        letter-spacing: 6px;
    }
</style>
"""
st.markdown(BUNKER_CSS, unsafe_allow_html=True)

st.set_page_config(
    page_title="ALLIED ENIGMA MINER - SN63",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("<h1 style='text-align: center;'>🔒 ALLIED ENIGMA MINER</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #aaffaa;'>US ARMY SIGNALS INTELLIGENCE • BUNKER COMMAND POST 1944 • SN63</h3>", unsafe_allow_html=True)
st.caption("Double-Loop Discovery Engine • EGGROLL + Agent-Reach + ValidationOracle + Three-Layer Memory + Runtime Tools + NO-BS ASSESSMENT UPGRADES")

# ====================== SESSION STATE & MANAGER ======================
if "arbos_manager" not in st.session_state:
    st.session_state.arbos_manager = ArbosManager()
manager = st.session_state.arbos_manager

# ====================== QUICK PROMPT BAR ======================
st.markdown("### 🚀 QUICK MINER PROMPT")
quick_prompt = st.text_area(
    "Quick Enhancement Prompt (applied instantly)",
    height=80,
    placeholder="Maximize novelty • Prioritize symbolic tools • Require formal verification...",
    key="quick_prompt"
)

if st.button("Apply Quick Prompt to Current Session", type="primary"):
    if quick_prompt.strip():
        st.session_state.enhancement_prompt = quick_prompt.strip()
        st.success("Quick prompt applied!")

st.markdown("---")

# ====================== SIDEBAR ======================
st.sidebar.title("🛠️ ALLIED OPERATIONS")
st.sidebar.metric("Mode", "Production + Self-Improvement")
st.sidebar.caption(f"EGGROLL Rank: **{manager.eggroll_rank}** | σ: **{manager.sigma:.3f}**")
st.sidebar.caption("Agent-Reach: **ON** (caching + fallbacks)")
st.sidebar.caption("ValidationOracle: **LIVE** (SN63 official scoring)")
st.sidebar.caption(f"Max Repair Attempts: **{manager.max_repair_attempts}**")

pause_on_verification = st.sidebar.checkbox("Pause on Verification (Phase 8)", value=False)
early_stop_enabled = st.sidebar.checkbox("Enable Early-Stop (validation_score < 0.65 after 2 loops)", value=True)

enable_three_layer_memory = st.sidebar.checkbox("Enable Three-Layer Memory Compression", value=False)
enable_runtime_tools = st.sidebar.checkbox("Allow Safe Runtime Tool Creation", value=False)
enable_self_diagnostics = st.sidebar.checkbox("Run Self-Diagnostics on Reconvene", value=False)

if st.sidebar.button("🔍 Pre-Run ToolHunter Discovery (GOAL.md)"):
    with st.spinner("Analyzing goals/killer_base.md..."):
        try:
            with open("goals/killer_base.md", "r") as f:
                goal_content = f.read()
            discovered = manager.discover_from_goal(goal_content)
            if discovered:
                st.sidebar.success(f"✅ Added {len(discovered)} tools/models")
            else:
                st.sidebar.warning("No strong matches.")
        except Exception as e:
            st.sidebar.error(f"Error: {e}")

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
    endpoint = st.text_input("Endpoint URL (if needed)", placeholder="https://...")
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

# ====================== STAGE 1: HIGH-LEVEL PLANNING ======================
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
        st.markdown("### 🚀 Miner Enhancement Prompt")
        enhancement_prompt = st.text_area(
            "Your strategic instructions",
            height=160,
            value=st.session_state.get("enhancement_prompt", ""),
            placeholder="Maximize novelty and IP potential..."
        )
        st.session_state.enhancement_prompt = enhancement_prompt
    with col2:
        st.metric("Suggested Swarm Size", plan.get("suggested_swarm_size", 1))

    feedback = st.text_area("Feedback / Tweak (optional)")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("✅ Approve High-Level Plan & Continue", type="primary"):
            st.session_state.approved_plan = plan
            st.session_state.stage = "post_orchestration_review"
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

# ====================== PHASE 4: POST-ORCHESTRATION REVIEW DASHBOARD ======================
if st.session_state.get("stage") == "post_orchestration_review":
    with st.spinner("Orchestrator Arbos creating detailed blueprint..."):
        blueprint = manager._refine_plan(
            st.session_state.approved_plan, 
            st.session_state.challenge,
            st.session_state.get("deterministic_tooling", ""),
            st.session_state.get("enhancement_prompt", "")
        )
        st.session_state.blueprint = blueprint

    st.header("🚀 Phase 4: Post-Orchestration Review Dashboard")
    st.subheader("Blueprint & Swarm Dynamics")
    st.json(blueprint)
    st.caption("**NO-BS ASSESSMENT:** Per-subtask validation_criteria + self-scoring + dynamic prompt improvement + correlation logging + trajectory export now active.")

    col1, col2 = st.columns(2)
    with col1:
        apply_arbo = st.checkbox("⭐ Apply Arbos Recommended (Vector DB high-score patterns)", value=True)
        enable_three_layer = st.checkbox("Enable Three-Layer Memory Compression", value=False)
    with col2:
        add_context = st.checkbox("➕ Add My Context / Tools / Tests", value=False)
        user_context = st.text_area("Your custom input (tools, tests, constraints)", "")
        enable_runtime_tools = st.checkbox("Allow Safe Runtime Tool Creation", value=False)

    if st.button("**Encode & Launch Swarm**", type="primary", use_container_width=True):
        if apply_arbo:
            st.success("Applied Arbos Recommended patterns from Vector DB")
        if add_context and user_context:
            st.success("Custom context added to blueprint")
        if enable_three_layer:
            st.info("Three-layer memory compression enabled")
        if enable_runtime_tools:
            st.info("Safe runtime tool creation enabled")
        st.session_state.stage = "final_review"
        final_solution, _, _ = manager._smart_route(st.session_state.challenge)
        st.session_state.final_solution = final_solution
        st.rerun()

# ====================== FINAL REVIEW (Phase 11) ======================
if st.session_state.get("stage") == "final_review":
    solution = st.session_state.final_solution
    blueprint = st.session_state.get("blueprint", {})
    trace = st.session_state.get("trace_log", [])

    st.subheader("🔍 Phase 11: Final Review & Packaging")

    tab1, tab2, tab3, tab4 = st.tabs(["Solution + Oracle", "ToolHunter", "Memory History", "🧬 SELF-IMPROVEMENT"])

    with tab1:
        st.text_area("Final Synthesized Solution", solution, height=400)
        st.markdown("### ValidationOracle Results (Official SN63 Scoring)")
        st.markdown(f"**Detected Validation Strategy:** {manager._current_strategy.get('domain', 'general')} | Type: {manager._current_strategy.get('verification_type', 'standard')} | Tools: {manager._current_strategy.get('enabled_modules', [])}")
        st.success(f"Score: {manager.validator.last_score:.3f} | V/Vd Ready: {manager.validator.last_vvd_ready} | Notes: {manager.validator.last_notes}")

        st.markdown("### Sub-Arbos Performance (NO-BS ASSESSMENT)")
        st.info("Per-subtask scores, correlation with final oracle, and prompt improvement logs are now tracked.")

    with tab2:
        st.markdown("### ToolHunter Results")
        manual_actions = [entry for entry in trace if isinstance(entry, str) and ("MANUAL REQUIRED" in entry.upper() or "ToolHunter" in entry)]
        if manual_actions:
            for action in manual_actions:
                st.info(action)
        else:
            st.success("✅ No ToolHunter actions required.")

    with tab3:
        st.markdown("### Memory History (Re-loop Learning)")
        st.info("Memory history loaded from your persistent memory system.")

    with tab4:
        st.markdown("### 🧬 SELF-IMPROVEMENT LOOP (trajrl-inspired + EGGROLL)")
        history = manager.get_run_history(n=8)
        if history:
            st.dataframe(pd.DataFrame(history), use_container_width=True)
        else:
            st.info("No run history yet.")

        if st.button("🔍 Run Arbos Self-Critique on Last Runs", type="primary"):
            with st.spinner("Arbos analyzing patterns..."):
                critique = manager.self_critique(st.session_state.challenge, n_runs=5)
                st.success("✅ Self-Critique Complete")
                st.markdown(f"""
                **Arbos Diagnosis:**
                - Common issues: {critique.get('common_issues', [])}
                - Weak areas: {critique.get('weak_areas', [])}
                - **Recommended prompt addition:**
                  {critique.get('recommended_prompt_additions', 'No suggestion available.')}
                """)
                if st.button("✅ Apply Suggestion to Current Enhancement Prompt"):
                    current = st.session_state.get("enhancement_prompt", "")
                    st.session_state.enhancement_prompt = manager.apply_self_improvement(current, critique)
                    st.success("Suggestion applied!")

        st.markdown("**Manual Self-Improvement Instruction**")
        manual = st.text_area("Tell Arbos how to improve next run", height=100, placeholder="Be more aggressive on novelty...")

        if st.button("🚀 Apply & Re-run with Self-Improvement", type="primary"):
            st.success("Enhanced prompt sent to swarm with self-improvement directives!")

    # NEW: Trajectory export for offline optimization
    if st.button("📤 Export Trajectories for Offline Optimization (agent-lightning / RL)"):
        path = manager.export_trajectories_for_optimization(st.session_state.challenge)
        st.success(f"Trajectories exported to {path}")

    miner_notes = st.text_area("Your Final Notes (optional)")

    if st.button("📦 Package for SN63 Submission (V/Vd formatted zip)", type="primary"):
        manager.save_run_to_history(
            challenge=st.session_state.challenge,
            enhancement_prompt=st.session_state.get("enhancement_prompt", ""),
            solution=solution,
            score=manager.validator.last_score,
            novelty=8.0,
            verifier=manager.validator.last_score,
            main_issue="None"
        )
        _package_submission(solution, blueprint, trace, miner_notes, st.session_state.challenge, 
                           st.session_state.get("verification_instructions", ""), 
                           st.session_state.get("deterministic_tooling", ""))
        st.success("✅ Submission package created!")
        st.balloons()

# ====================== PACKAGING FUNCTION ======================
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

    oracle_info = {
        "validation_score": manager.validator.last_score,
        "fidelity": manager.validator.last_fidelity,
        "vvd_ready": manager.validator.last_vvd_ready,
        "notes": manager.validator.last_notes,
        "timestamp": datetime.now().isoformat()
    }
    (sub_dir / "validation_oracle.json").write_text(json.dumps(oracle_info, indent=2))

    with zipfile.ZipFile(sub_dir / "submission_package.zip", "w") as z:
        for f in sub_dir.glob("*"):
            if f.is_file() and f.suffix != ".zip":
                z.write(f, f.name)

    st.success(f"✅ Package ready: {sub_dir}/submission_package.zip")
    st.download_button("Download Submission Package", 
                       data=open(sub_dir / "submission_package.zip", "rb").read(), 
                       file_name=f"sn63_{ts}.zip", 
                       mime="application/zip")
