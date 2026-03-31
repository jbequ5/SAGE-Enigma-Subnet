import streamlit as st
import json
import zipfile
import pandas as pd
from pathlib import Path
from datetime import datetime

from agents.arbos_manager import ArbosManager

# ====================== PAGE CONFIG - MUST BE FIRST ======================
st.set_page_config(
    page_title="ALLIED ENIGMA MINER",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== CUSTOM ENIGMA BUNKER THEME ======================
BUNKER_CSS = """
<style>
    [data-testid="stAppViewContainer"] {
        background-image: url("https://pub-1407f82391df4ab1951418d04be76914.r2.dev/custom-enigma-bunker-1944.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.85);
        z-index: -1;
    }

    [data-testid="stHeader"], footer, [data-testid="stToolbar"] {
        visibility: hidden;
    }

    h1, h2, h3, .stMarkdown h1, .stMarkdown h2 {
        color: #00ff9d !important;
        font-family: 'Courier New', monospace;
        text-shadow: 0 0 30px #00ff9d, 0 0 60px #00aa77;
        letter-spacing: 4px;
    }

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stMarkdown, p, span, label {
        color: #00ff9d !important;
        text-shadow: 0 0 10px rgba(0, 255, 150, 0.7);
    }

    .stButton > button {
        background-color: #001a0f;
        color: #00ff9d;
        border: 3px solid #00ff9d;
        font-family: 'Courier New', monospace;
        box-shadow: 0 0 15px rgba(0, 255, 150, 0.5);
    }

    .stButton > button:hover {
        background-color: #003322;
        box-shadow: 0 0 25px rgba(0, 255, 150, 0.9);
    }
</style>
"""
st.markdown(BUNKER_CSS, unsafe_allow_html=True)

# ====================== TITLE ======================
st.markdown("<h1 style='text-align: center;'>🔒 ALLIED ENIGMA MINER</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #aaffaa;'>US ARMY SIGNALS INTELLIGENCE • BUNKER COMMAND POST 1944 • SN63</h3>", unsafe_allow_html=True)
st.caption("Challenge-Agnostic • Quasar Long-Context • Dynamic Swarm • Verifier-First • Hardened Launch Version")

# ====================== SESSION STATE ======================
if "arbos_manager" not in st.session_state:
    st.session_state.arbos_manager = ArbosManager()

if "stage" not in st.session_state:
    st.session_state.stage = None

if "high_level_plan" not in st.session_state:
    st.session_state.high_level_plan = None

if "blueprint" not in st.session_state:
    st.session_state.blueprint = None

if "final_solution" not in st.session_state:
    st.session_state.final_solution = None

if "trace_log" not in st.session_state:
    st.session_state.trace_log = []

manager = st.session_state.arbos_manager

# ====================== GOAL.MD EDITOR ======================
st.subheader("🎯 GOAL.md / Strategy File")
st.caption("Single source of truth — edit toggles and base strategy here.")

goal_path = Path("goals/killer_base.md")
goal_path.parent.mkdir(parents=True, exist_ok=True)

if not goal_path.exists():
    goal_path.write_text("""# Enigma Machine Miner - Base Strategy

mode: optimal
compute_source: chutes
max_compute_hours: 3.8
resource_aware: true
guardrails: true
toolhunter_escalation: true
quasar_attention: true
dynamic_swarm: true
verifier_first: true
light_compression: true
grail_on_winning_runs: false
""")

with open(goal_path, "r", encoding="utf-8") as f:
    current_goal = f.read()

edited_goal = st.text_area(
    label="Edit GOAL.md content",
    value=current_goal,
    height=350,
    key="goal_editor_unique"
)

if st.button("💾 Save GOAL.md Changes"):
    with open(goal_path, "w", encoding="utf-8") as f:
        f.write(edited_goal)
    st.success("✅ GOAL.md saved!")
    st.rerun()

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("🛠️ Configuration")

    st.subheader("Core Intelligence")
    enable_quasar = st.checkbox("Enable Quasar Long-Context Attention", 
                                value=True, key="quasar_attention")

    st.subheader("Safety & Limits")
    max_hours = st.slider("Max Compute Hours", 1.0, 4.0, 3.8, key="max_hours_slider")

    # Apply Quasar toggle
    if "quasar_enabled" not in st.session_state or st.session_state.quasar_enabled != enable_quasar:
        st.session_state.quasar_enabled = enable_quasar
        try:
            manager.compute.enable_quasar(enable_quasar)
            if enable_quasar:
                st.sidebar.success("Quasar Enabled")
            else:
                st.sidebar.info("Quasar Disabled → Local GPU")
        except Exception as e:
            st.sidebar.error(f"Quasar toggle failed: {e}")

# ====================== COMPUTE SETUP (Works for anyone) ======================
if "compute_source" not in st.session_state:
    st.subheader("🔌 Compute Setup")
    compute_option = st.radio(
        "Choose compute source:",
        options=[
            "Local GPU (auto-detects your GPU)",
            "Chutes (decentralized GPUs)",
            "Already running (use existing endpoint)",
            "Custom / Hosted"
        ],
        index=0
    )
    endpoint = st.text_input("Endpoint URL (if needed)", placeholder="https://...")
    
    if st.button("Continue with this compute source", type="primary"):
        source_map = {
            "Local GPU (auto-detects your GPU)": "local",
            "Chutes (decentralized GPUs)": "chutes",
            "Already running (use existing endpoint)": "already_running",
            "Custom / Hosted": "custom"
        }
        st.session_state.compute_source = source_map[compute_option]
        st.session_state.custom_endpoint = endpoint if endpoint and endpoint.strip() else None
        
        # This line makes "Local GPU" work for anyone
        manager.compute.set_compute_source(st.session_state.compute_source, st.session_state.custom_endpoint)
        
        st.session_state.stage = "planning_approval"
        st.rerun()
    st.stop()

# ====================== QUICK PROMPT ======================
st.subheader("🚀 QUICK MINER PROMPT")
challenge = st.text_area("SN63 Challenge Description", height=150, key="challenge_input")
verification = st.text_area("Verification Instructions (optional)", height=100, key="verification_input")
enhancement = st.text_input("Enhancement Prompt (optional)", key="enhancement_input")

# ====================== Generate High-Level Plan ======================
if st.button("🔍 Generate High-Level Plan", type="primary"):
    if not challenge.strip():
        st.error("Please enter a challenge description.")
    else:
        with st.spinner("Planning Arbos running..."):
            plan = manager.plan_challenge(challenge, enhancement)
            st.session_state.high_level_plan = plan
            st.session_state.challenge = challenge
            st.session_state.verification = verification
            st.session_state.enhancement = enhancement
            st.session_state.stage = "planning_approval"
        st.rerun()

# ====================== STAGE 1: HIGH-LEVEL PLANNING ======================
if st.session_state.get("stage") == "planning_approval":
    st.subheader("📋 Stage 1: High-Level Plan – Strategic Review")
    if st.session_state.high_level_plan:
        st.json(st.session_state.high_level_plan)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("**Adapted Strategy:**")
            st.json(st.session_state.high_level_plan.get("adapted_strategy", {}))
        with col2:
            if st.button("✅ Approve Plan & Go to Orchestration Review", type="primary"):
                st.session_state.stage = "post_orchestration_review"
                st.rerun()
            if st.button("🔄 Re-plan"):
                st.session_state.stage = None
                st.rerun()
    else:
        st.warning("No plan generated yet.")

# ====================== STAGE 2: POST-ORCHESTRATION REVIEW ======================
if st.session_state.get("stage") == "post_orchestration_review":
    with st.spinner("Orchestrator Arbos creating detailed blueprint..."):
        blueprint = manager._refine_plan(
            st.session_state.high_level_plan,
            st.session_state.challenge,
            st.session_state.get("deterministic_tooling", ""),
            st.session_state.get("enhancement", "")
        )
        st.session_state.blueprint = blueprint

    st.header("🚀 Post-Orchestration Review Dashboard")
    st.subheader("Blueprint & Swarm Dynamics")
    st.json(blueprint)

    if st.button("🚀 Launch Swarm Now", type="primary", use_container_width=True):
        with st.spinner("Running dynamic swarm..."):
            verification_instructions = st.session_state.get("verification", "")
            final_solution = manager.execute_full_cycle(
                st.session_state.blueprint, 
                st.session_state.challenge, 
                verification_instructions
            )
            st.session_state.final_solution = final_solution
            st.session_state.stage = "final_review"
        st.rerun()

# ====================== FINAL REVIEW ======================
if st.session_state.get("stage") == "final_review":
    solution = st.session_state.get("final_solution", "")
    blueprint = st.session_state.get("blueprint", {})
    trace = st.session_state.get("trace_log", [])

    st.subheader("🔍 Final Review & Packaging")

    tab1, tab2, tab3, tab4 = st.tabs(["Solution + Oracle", "ToolHunter", "Memory History", "🧬 SELF-IMPROVEMENT"])

    with tab1:
        st.text_area("Final Synthesized Solution", solution, height=400)
        st.success(f"ValidationOracle Score: {getattr(manager.validator, 'last_score', 0):.3f}")

    with tab2:
        st.info("Tool proposals logged for next run")

    with tab3:
        st.info("Three-layer memory with light compression active")

    with tab4:
        if st.button("Run Self-Critique"):
            critique = manager.self_critique(st.session_state.challenge)
            st.json(critique)

    miner_notes = st.text_area("Your Final Notes (optional)")

    if st.button("📦 Package for SN63 Submission", type="primary"):
        manager.save_run_to_history(
            challenge=st.session_state.challenge,
            enhancement_prompt=st.session_state.get("enhancement", ""),
            solution=solution,
            score=getattr(manager.validator, 'last_score', 0),
            novelty=8.0,
            verifier=getattr(manager.validator, 'last_score', 0),
            main_issue="None"
        )
        _package_submission(solution, blueprint, trace, miner_notes, st.session_state.challenge, 
                           st.session_state.get("verification", ""), 
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
        "validation_score": getattr(manager.validator, 'last_score', 0.0),
        "fidelity": getattr(manager.validator, 'last_fidelity', 0.0),
        "vvd_ready": getattr(manager.validator, 'last_vvd_ready', False),
        "notes": getattr(manager.validator, 'last_notes', ''),
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
