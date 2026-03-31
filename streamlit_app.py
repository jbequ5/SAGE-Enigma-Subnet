import streamlit as st
import json
import zipfile
import pandas as pd
from pathlib import Path
from datetime import datetime

from agents.arbos_manager import ArbosManager

# ←←← MOVE THIS TO THE VERY TOP (first Streamlit command)
st.set_page_config(
    page_title="Enigma Machine Miner",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)
# ====================== BUNKER THEME ======================
BUNKER_CSS = """
<style>
    [data-testid="stAppViewContainer"] {
        background-image: url("https://pub-1407f82391df4ab1951418d04be76914.r2.dev/uploads/6700b7a0-d46e-4054-9f1c-3ed01c65c15b.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Stronger dark overlay for much better text readability */
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.75);   /* Increased to 0.85 as requested */
        z-index: -1;
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
        font-size: 16px;
        padding: 12px 24px;
        border-radius: 4px;
        box-shadow: 0 0 15px rgba(0, 255, 150, 0.5);
    }

    .stButton > button:hover {
        background-color: #003322;
        box-shadow: 0 0 25px rgba(0, 255, 150, 0.8);
    }

    /* Sidebar improvements */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 10, 6, 0.95) !important;
        border-right: 2px solid #00ff9d;
    }

    /* Make all text more readable */
    .stMarkdown, p, span, label {
        color: #00ff9d !important;
        text-shadow: 0 0 8px rgba(0, 255, 150, 0.6);
    }
</style>
"""

st.markdown(BUNKER_CSS, unsafe_allow_html=True)

# Extra overlay for top header text
st.markdown("""
<style>
    /* Strong overlay for the main title area */
    .stApp header, .stApp .block-container {
        background: rgba(0, 0, 0, 0.75) !important;
        padding: 1rem 2rem;
        border-radius: 8px;
    }
    
    /* Make title and subtitle stand out more */
    h1, .stMarkdown h1 {
        text-shadow: 0 0 20px #00ff9d, 0 0 40px #00ff9d !important;
        color: #00ff9d !important;
    }
</style>
""", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'>🔒 ALLIED ENIGMA MINER</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #aaffaa;'>US ARMY SIGNALS INTELLIGENCE • BUNKER COMMAND POST 1944 • SN63</h3>", unsafe_allow_html=True)
st.caption("Challenge-Agnostic • Quasar Long-Context • Dynamic Swarm • Verifier-First • Hardened Launch Version")

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
# ====================== GOAL.MD EDITOR (Make it obvious) ======================
st.subheader("🎯 GOAL.md / Strategy File")
st.caption("This is your single source of truth for miner preferences, toggles, and base strategy. Edit it here — changes are saved automatically.")

goal_path = Path("goals/killer_base.md")

if not goal_path.exists():
    goal_path.parent.mkdir(parents=True, exist_ok=True)
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
    height=400,
    key="goal_editor"
)

if st.button("💾 Save GOAL.md Changes"):
    with open(goal_path, "w", encoding="utf-8") as f:
        f.write(edited_goal)
    st.success("✅ GOAL.md saved! Restart the run to apply changes.")
    st.rerun()

st.info("💡 Tip: This file controls all toggles (Quasar, Grail, compression, etc.). The sidebar checkboxes are for quick overrides only.")
# ====================== SIDEBAR ======================
st.sidebar.title("🛠️ ALLIED OPERATIONS")
with st.sidebar:
    st.header("🛠️ Configuration")
    
    st.subheader("Core Intelligence")
    enable_quasar = st.checkbox("Enable Quasar Long-Context Attention (Planning + Adaptation)", 
                                value=True, key="quasar_attention")
    
    enable_grail = st.checkbox("Enable Grail verifiable post-training on winning runs (>0.92)", 
                               value=False, key="grail_post_training")
    
    enable_three_layer = st.checkbox("Enable Three-Layer Memory Compression", 
                                     value=True, key="three_layer_memory")
    
    enable_light_compression = st.checkbox("Enable Light Context Compression after each loop", 
                                           value=True, key="light_compression")
    
    st.subheader("Tool & Swarm")
    enable_toolhunter = st.checkbox("Enable ToolHunter + ReadyAI llms.txt Grounding", 
                                    value=True, key="toolhunter_enabled")
    enable_dynamic_swarm = st.checkbox("Enable Dynamic VRAM-aware Swarm", 
                                       value=True, key="dynamic_swarm")
    
    st.subheader("Safety & Limits")
    max_hours = st.slider("Max Compute Hours (H100/Chutes)", 1.0, 4.0, 3.8, key="max_hours_slider")
    
    st.subheader("Advanced")
    enable_self_critique = st.checkbox("Enable Self-Critique + Autoresearch", 
                                       value=True, key="self_critique")

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
        st.session_state.challenge = st.text_area("SN63 Challenge + Verification Code", height=180, placeholder="Paste full challenge + any verification code blocks...")

    with st.spinner("Planning Arbos + Orchestrator Arbos + Adaptation Arbos running..."):
        plan = manager.plan_challenge(
            st.session_state.challenge,
            st.session_state.get("enhancement_prompt", "")
        )
        st.session_state.high_level_plan = plan

    st.subheader("📋 Stage 1: High-Level Plan – Strategic Review")
    st.json(plan)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**Adapted Strategy (post-ToolHunter + Adaptation Arbos):**")
        st.json(plan.get("adapted_strategy", {}))
    with col2:
        if st.button("✅ Approve Plan & Launch Swarm", type="primary"):
            st.session_state.stage = "post_orchestration_review"
            st.rerun()
        if st.button("🔄 Tweak & Re-plan"):
            st.session_state.stage = "planning_approval"
            st.rerun()

# ====================== PHASE 4: POST-ORCHESTRATION REVIEW DASHBOARD ======================
if st.session_state.get("stage") == "post_orchestration_review":
    with st.spinner("Orchestrator Arbos creating detailed blueprint..."):
        blueprint = manager._refine_plan(
            st.session_state.approved_plan if "approved_plan" in st.session_state else st.session_state.high_level_plan, 
            st.session_state.challenge,
            st.session_state.get("deterministic_tooling", ""),
            st.session_state.get("enhancement_prompt", "")
        )
        st.session_state.blueprint = blueprint

    st.header("🚀 Phase 4: Post-Orchestration Review Dashboard")
    st.subheader("Blueprint & Swarm Dynamics")
    st.json(blueprint)
    st.caption("**NO-BS ASSESSMENT:** Per-subtask validation_criteria + self-scoring + dynamic prompt improvement active.")

    col1, col2 = st.columns(2)
    with col1:
        apply_arbo = st.checkbox("⭐ Apply Arbos Recommended patterns", value=True)
        enable_three_layer = st.checkbox("Enable Three-Layer Memory Compression", value=True, key="three_layer_memory")
    with col2:
        add_context = st.checkbox("➕ Add My Context / Tools / Tests", value=False)
        user_context = st.text_area("Your custom input (tools, tests, constraints)", "")
        enable_runtime_tools = st.checkbox("Allow Safe Runtime Tool Creation", value=False)

    if st.button("**Encode & Launch Swarm**", type="primary", use_container_width=True):
        if apply_arbo:
            st.success("Applied Arbos Recommended patterns")
        if add_context and user_context:
            st.success("Custom context added")
        if enable_three_layer:
            st.info("Three-layer memory compression enabled")
        if enable_runtime_tools:
            st.info("Safe runtime tool creation enabled")
        st.session_state.stage = "final_review"
        verification_instructions = st.session_state.get("verification_instructions", "")
        final_solution = manager.execute_full_cycle(st.session_state.blueprint, st.session_state.challenge, verification_instructions)
        st.session_state.final_solution = final_solution
        st.rerun()

# ====================== FINAL REVIEW (Phase 11) ======================
if st.session_state.get("stage") == "final_review":
    solution = st.session_state.get("final_solution", "")
    blueprint = st.session_state.get("blueprint", {})
    trace = st.session_state.get("trace_log", [])

    st.subheader("🔍 Phase 11: Final Review & Packaging")

    tab1, tab2, tab3, tab4 = st.tabs(["Solution + Oracle", "ToolHunter", "Memory History", "🧬 SELF-IMPROVEMENT"])

    with tab1:
        st.text_area("Final Synthesized Solution", solution, height=400)
        st.markdown("### ValidationOracle Results")
        st.success(f"Score: {getattr(manager.validator, 'last_score', 0):.3f}")

    with tab2:
        st.markdown("### ToolHunter Results")
        st.info("Tool proposals logged for next run (no creation performed)")

    with tab3:
        st.markdown("### Memory History")
        st.info("Three-layer memory with light compression active")

    with tab4:
        st.markdown("### SELF-IMPROVEMENT")
        if st.button("Run Self-Critique"):
            critique = manager.self_critique(st.session_state.challenge)
            st.json(critique)

    miner_notes = st.text_area("Your Final Notes (optional)")

    if st.button("📦 Package for SN63 Submission", type="primary"):
        manager.save_run_to_history(
            challenge=st.session_state.challenge,
            enhancement_prompt=st.session_state.get("enhancement_prompt", ""),
            solution=solution,
            score=getattr(manager.validator, 'last_score', 0),
            novelty=8.0,
            verifier=getattr(manager.validator, 'last_score', 0),
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
