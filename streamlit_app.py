import streamlit as st
import json
import zipfile
from pathlib import Path
from datetime import datetime

# ====================== PAGE CONFIG - MUST BE FIRST ======================
st.set_page_config(
    page_title="ALLIED ENIGMA MINER",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

from agents.arbos_manager import ArbosManager
from agents.tools.compute import compute_router
from code_editor import code_editor

# ====================== CINEMATIC ENIGMA BUNKER THEME ======================
st.markdown("""
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
        background: rgba(0, 0, 0, 0.88);
        z-index: -1;
        animation: scanline 8s linear infinite;
    }
    @keyframes scanline { 0% { background-position: 0 0; } 100% { background-position: 0 100%; } }

    h1, h2, h3 { 
        color: #00ff9d !important; 
        font-family: 'Courier New', monospace; 
        text-shadow: 0 0 30px #00ff9d, 0 0 60px #00aa77; 
        letter-spacing: 6px; 
    }
    .rotor { animation: spin 12s linear infinite; }
    @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

    .stButton > button {
        background-color: #001a0f;
        color: #00ff9d;
        border: 3px solid #00ff9d;
        font-family: 'Courier New', monospace;
        box-shadow: 0 0 20px #00ff9d;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #003322;
        box-shadow: 0 0 35px #00ff9d;
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)

# Sound effects
st.markdown("""
<audio id="click" src="https://freesound.org/data/previews/276/276951_5123854-lq.mp3" preload="auto"></audio>
<audio id="rotor" src="https://freesound.org/data/previews/202/202113_3720023-lq.mp3" preload="auto"></audio>
<audio id="success" src="https://freesound.org/data/previews/269/269026_5123854-lq.mp3" preload="auto"></audio>
<script>
    function playSound(id) {
        const audio = document.getElementById(id);
        if (audio) audio.play();
    }
</script>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🔒 ALLIED ENIGMA MINER v4.5</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #ffaa00;'>TOP SECRET • BUNKER COMMAND POST 1944 • SN63 QUANTUM INNOVATE</h3>", unsafe_allow_html=True)
st.caption("🔴 ENIGMA ROTORS SPINNING • LIVE DECRYPTION MISSION ACTIVE")

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

if "compute_source" not in st.session_state:
    st.session_state.compute_source = "local"

if "validation_criteria" not in st.session_state:
    st.session_state.validation_criteria = {}

if "toolhunter_results" not in st.session_state:
    st.session_state.toolhunter_results = None

manager = st.session_state.arbos_manager

# ====================== LIVE HEADER ======================
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    st.markdown("🔄 <span class='rotor'>⚙️⚙️⚙️</span> ROTORS ACTIVE", unsafe_allow_html=True)
with col2:
    score = getattr(manager.validator, 'last_score', 0.0)
    st.metric("VALIDATION ORACLE SCORE", f"{score:.3f}")
with col3:
    if st.button("🧹 ABORT MISSION"):
        for k in list(st.session_state.keys()):
            if k != "arbos_manager":
                del st.session_state[k]
        st.rerun()

# ====================== GOAL.MD EDITOR (Full Strategy - Single Source of Truth) ======================
st.subheader("📟 FULL STRATEGY — GOAL.md")
st.caption("This is the single source of truth. Edit Core Strategy, English Modules, and Templates here.")

goal_path = Path("goals/killer_base.md")
goal_path.parent.mkdir(parents=True, exist_ok=True)

if not goal_path.exists():
    goal_path.write_text("""# Enigma Machine Miner - Base Strategy

## Core Strategy (Challenge-Agnostic Base Prompt)
Treat every problem as pure symbolic/text — no premature domain assumptions.
Verifier-code-first + symbolic invariants on every subtask before any LLM generation.
ToolHunter sub-swarm (ModelHunter / ToolHunter / PaperHunter / ReadyAI-DataHunter) must run in parallel where possible; serial handoffs go through ValidationOracle.
Reward only trajectories that measurably improve ValidationOracle score via exact 0-1 deterministic checks.
Every Adaptation Arbos step must first search trajectory_vector_db + memdir for proven high-score symbolic patterns.
Maximize symbolic coverage per compute unit while preserving reproducibility.

## English Evolution Modules
### ENGLISH_MEMDIR_GRAIL_MODULE
Maintain a persistent memdir-backed Grail store. After every high ValidationOracle run, auto-extract symbolic invariants, ToolHunter HF models, verifier snippets, and module-effectiveness reflections.

### ENGLISH_TOOL_SWARM_MODULE
Turn ToolHunter into four coordinated sub-swarms (ModelHunter, ToolHunter, PaperHunter, ReadyAI-DataHunter) that run in parallel where possible.

### ENGLISH_AMDAHL_COORDINATION_MODULE
Apply Amdahl-aware coordination to every decomposition: identify truly parallel subtasks vs. serial dependencies.

## Auto-Populate Templates
### AUTO_POST_PLANNING_ENHANCEMENT_TEMPLATE
Post-Planning Refinement v4: Elevate the high-level plan with strict symbolic-first discipline...

### AUTO_PRE_LAUNCH_CONTEXT_TEMPLATE
Pre-Launch Final Context v4: Before spawning the Dynamic Swarm...
""", encoding="utf-8")

with open(goal_path, "r", encoding="utf-8") as f:
    current_goal = f.read()

edited_goal = st.text_area("Full Strategy Content (Core + Modules + Templates)", value=current_goal, height=420, key="goal_editor_unique")

if st.button("💾 Save Full Strategy"):
    with open(goal_path, "w", encoding="utf-8") as f:
        f.write(edited_goal)
    st.success("✅ Full Strategy saved to GOAL.md")
    st.rerun()

# ====================== CHALLENGE DEFINITION & VERIFICATION ======================
st.subheader("🎯 MISSION TARGET")
col_chal, col_ver = st.columns([1, 1])
with col_chal:
    challenge = st.text_area(
        "SN63 Challenge Description (Quantum Innovate task)",
        height=160,
        placeholder="Describe the full problem in detail...",
        key="challenge_input"
    )
with col_ver:
    st.caption("✅ VERIFICATION PROTOCOL")
    default_verification = '''def verify_solution(solution, params=None):
    """Return (passed: bool, explanation: str, score: float)"""
    return False, "Verification not implemented yet", 0.0'''

    verification_response = code_editor(
        default_verification,
        lang="python",
        theme="vs-dark",
        height=320,
        allow_reset=True,
        key="verification_editor_unique"
    )

    if isinstance(verification_response, dict):
        verification_instructions = verification_response.get("text", default_verification)
    else:
        verification_instructions = str(verification_response) if verification_response else default_verification

# ====================== TOOLHUNTER SWARM ======================
st.subheader("🛰️ RECON SWARM — TOOLHUNTER")
st.caption("Describe a gap and get immediate tool/library/model recommendations + install commands")

hunter_gap = st.text_area(
    "Current Gap or Subtask",
    height=100,
    placeholder="e.g., Need better quantum circuit simulator...",
    key="hunter_gap_input"
)

col_th1, col_th2 = st.columns([2, 1])
with col_th1:
    if st.button("🚀 LAUNCH RECON SWARM", type="secondary", use_container_width=True):
        if not hunter_gap.strip():
            st.error("Please describe a gap or subtask.")
        else:
            with st.spinner("Scanning ToolHunter + ReadyAI + Agent-Reach..."):
                hunt_result = manager.run_toolhunter_swarm(hunter_gap, max_proposals=6)
                st.session_state.toolhunter_results = hunt_result
                st.success("✅ RECON COMPLETE")

                if hunt_result.get("status") == "success":
                    st.markdown("**Gap Analyzed:** " + hunt_result["gap"])
                    if hunt_result.get("proposals"):
                        st.subheader("Recommended Tools / Approaches")
                        for i, prop in enumerate(hunt_result["proposals"], 1):
                            st.markdown(f"{i}. {prop}")
                    if hunt_result.get("install_commands"):
                        st.subheader("Install Commands")
                        for cmd in hunt_result["install_commands"]:
                            st.code(cmd, language="bash")
                    st.caption(f"Confidence: {hunt_result.get('confidence', 0.7):.2f}")

                if hunt_result.get("status") == "success" and hunt_result.get("proposals"):
                    if st.button("✅ ADD RECOMMENDATIONS TO GOAL.md AS GRAIL PATTERN", type="primary"):
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                        content = "\n".join(hunt_result["proposals"]) + "\n\nInstall commands:\n" + "\n".join(hunt_result.get("install_commands", []))
                        with open(goal_path, "a", encoding="utf-8") as f:
                            f.write(f"\n\n## TOOLHUNTER_MINER_APPROVED_{timestamp}\n{content}\n")
                        manager.save_to_memdir(f"toolhunter_{timestamp}", {"content": content, "gap": hunter_gap})
                        st.success("✅ Added to GOAL.md and Grail!")
                        st.rerun()

with col_th2:
    st.info("Pro tip: Run this anytime — even mid-challenge.")

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("🛠️ BUNKER COMMAND CONSOLE")

    st.subheader("Core Intelligence")
    enable_quasar = st.checkbox("Enable Quasar Long-Context Attention", value=True, key="quasar_attention")
    enable_dynamic_swarm = st.checkbox("Enable Dynamic Swarm (VRAM-aware)", value=True, key="dynamic_swarm")
    enable_light_compression = st.checkbox("Enable Light Context Compression", value=True, key="light_compression")
    enable_self_critique = st.checkbox("Enable Self-Critique & Autoresearch", value=True, key="self_critique")

    st.subheader("Safety & Tooling")
    enable_toolhunter = st.checkbox("Enable ToolHunter + ReadyAI", value=True, key="toolhunter")
    enable_grail = st.checkbox("Enable Grail on Winning Runs", value=False, key="grail")

    toggles = {
        "Quasar": enable_quasar,
        "Three-Layer Memory Compression": True,
        "ToolHunter + ReadyAI": enable_toolhunter,
        "Grail on winning runs": enable_grail,
        "Self-Critique": enable_self_critique,
        "Light Compression": enable_light_compression,
        "Dynamic Swarm": enable_dynamic_swarm,
        "Dynamic Swarm Size": 5
    }
    manager.update_toggles(toggles)

    st.divider()
    st.caption("Advanced Controls")
    if st.button("🧹 Clear All Session Data"):
        for key in list(st.session_state.keys()):
            if key != "arbos_manager":
                del st.session_state[key]
        st.rerun()

# ====================== COMPUTE SETUP ======================
st.subheader("🔌 Compute Setup")
compute_option = st.radio(
    "Choose compute source:",
    options=[
        "Local GPU (Ollama — recommended, no API keys)",
        "Chutes (remote H100)",
        "Already running (use existing endpoint)",
        "Custom / Hosted"
    ],
    index=0,
    key="compute_radio"
)

endpoint = st.text_input("Custom Endpoint URL (if needed)", placeholder="https://...", key="endpoint_input")

if st.button("Apply Compute Source", type="primary"):
    source_map = {
        "Local GPU (Ollama — recommended, no API keys)": "local_gpu",
        "Chutes (remote H100)": "chutes",
        "Already running (use existing endpoint)": "already_running",
        "Custom / Hosted": "custom"
    }
    new_source = source_map[compute_option]
    st.session_state.compute_source = new_source
    st.session_state.custom_endpoint = endpoint if endpoint.strip() else None
    
    compute_router.set_mode(new_source)
    manager.set_compute_source(new_source, st.session_state.custom_endpoint)
    
    st.success(f"✅ Compute source set to: **{new_source}**")
    st.rerun()

st.info(f"Current Compute: **{st.session_state.compute_source}**")

# ====================== Generate High-Level Plan ======================
if st.button("🔍 Generate High-Level Plan", type="primary", use_container_width=True):
    if not challenge.strip():
        st.error("Please enter a challenge description.")
    else:
        with st.spinner("Planning Arbos running on Local GPU..."):
            plan = manager.plan_challenge(
                goal_md=edited_goal, 
                challenge=challenge, 
                enhancement_prompt="",   # No separate enhancement - use GOAL.md as base
                compute_mode=st.session_state.compute_source
            )
            st.session_state.high_level_plan = plan
            st.session_state.challenge = challenge
            st.session_state.verification = verification_instructions
            st.session_state.stage = "planning_approval"
            st.session_state.trace_log.append({"stage": "high_level_plan", "timestamp": datetime.now().isoformat()})
        st.rerun()

# ====================== STAGE 1: HIGH-LEVEL PLAN ======================
if st.session_state.get("stage") == "planning_approval":
    st.subheader("📋 Stage 1: High-Level Plan – Strategic Review")
    if st.session_state.high_level_plan:
        st.json(st.session_state.high_level_plan)

        st.subheader("📜 CURRENT FULL STRATEGY (from GOAL.md)")
        with st.expander("Full Strategy Content", expanded=True):
            st.text_area("GOAL.md Content", value=edited_goal, height=300, disabled=True)

        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("✅ Approve Plan & Go to Orchestration Review", type="primary"):
                st.session_state.stage = "post_orchestration_review"
                st.rerun()
            if st.button("🔄 Re-plan"):
                st.session_state.stage = None
                st.rerun()
    else:
        st.warning("No plan generated yet.")

# ====================== STAGE 2: POST-ORCHESTRATION ======================
if st.session_state.get("stage") == "post_orchestration_review":
    with st.spinner("Orchestrator Arbos refining blueprint..."):
        blueprint = manager._refine_plan(
            st.session_state.high_level_plan,
            st.session_state.challenge,
            st.session_state.get("deterministic_tooling", ""),
            ""  # No separate enhancement
        )
        st.session_state.blueprint = blueprint
        st.session_state.validation_criteria = blueprint.get("validation_criteria", {})

    st.header("🚀 Post-Orchestration Review Dashboard")
    st.subheader("Blueprint & Swarm Dynamics")
    st.json(blueprint)

    pre_launch = blueprint.get("generated_pre_launch_context", "No pre-launch context generated.")
    st.subheader("📜 Auto-Generated Pre-Launch Context")
    st.info(pre_launch[:1000] + "..." if len(pre_launch) > 1000 else pre_launch)

    if st.button("🚀 Launch Swarm Now", type="primary", use_container_width=True):
        with st.spinner("Launching dynamic swarm with verifier-first execution..."):
            final_solution = manager.execute_full_cycle(
                blueprint, 
                challenge, 
                verification_instructions
            )
            st.session_state.final_solution = final_solution
            st.session_state.stage = "final_review"
            st.session_state.trace_log.append({"stage": "swarm_launch", "timestamp": datetime.now().isoformat()})
        st.rerun()

# ====================== FINAL REVIEW & PACKAGING ======================
if st.session_state.get("stage") == "final_review":
    solution = st.session_state.get("final_solution", "")
    blueprint = st.session_state.get("blueprint", {})
    trace = st.session_state.get("trace_log", [])
    validation_criteria = st.session_state.get("validation_criteria", {})

    st.subheader("🔍 Final Review & Packaging")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Solution + Oracle", "ToolHunter Results", "Grail & Messages", "Self-Improvement", "Trace Log", "Validation Criteria"])

    with tab1:
        st.text_area("Final Synthesized Solution", value=str(solution), height=400)
        score = getattr(manager.validator, 'last_score', 0.0)
        st.success(f"ValidationOracle Score: **{score:.3f}**")

    with tab2:
        if st.session_state.toolhunter_results:
            st.json(st.session_state.toolhunter_results)
        else:
            st.info("No ToolHunter results yet.")

    with tab3:
        st.subheader("Recent Messages (Mature Message Bus)")
        recent_msgs = manager.get_recent_messages(limit=10)
        if recent_msgs:
            for msg in recent_msgs:
                st.markdown(f"**{msg['type']}** (score: {msg['validation_score']:.2f}, fidelity: {msg['fidelity']:.2f})")
                st.caption(msg['content'][:300] + "...")
        else:
            st.info("No messages yet.")

        st.subheader("Latest Grail Entry")
        grail = manager.load_from_memdir("latest_grail")
        if grail:
            st.json(grail)

    with tab4:
        if st.button("Run Self-Critique Now"):
            critique = manager.self_critique(st.session_state.get("challenge", "unknown"))
            st.json(critique)
        
        if st.button("Force Adaptation Arbos (re_adapt)"):
            current_sol = str(solution)[:2000] if solution else "No solution yet"
            manager.re_adapt({"solution": current_sol}, "miner_forced_adaptation")
            st.success("✅ Adaptation Arbos executed.")

    with tab5:
        st.subheader("Live Trace Log")
        for entry in trace[-20:]:
            st.caption(str(entry))

    with tab6:
        st.json(validation_criteria)
        st.caption("These criteria were used by each Sub-Arbos worker during the swarm.")

    miner_notes = st.text_area("Your Final Notes (optional)")

    if st.button("📦 Package for SN63 Submission", type="primary"):
        _package_submission(
            solution, blueprint, trace, miner_notes, 
            challenge, 
            verification_instructions, 
            st.session_state.get("deterministic_tooling", "")
        )
        st.balloons()
        st.success("✅ Submission package created!")

# ====================== PACKAGING FUNCTION ======================
def _package_submission(solution: str, blueprint: dict, trace: list, notes: str, challenge: str, verification: str, deterministic_tooling: str):
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    sub_dir = Path("submissions") / f"sn63_{ts}"
    sub_dir.mkdir(parents=True, exist_ok=True)

    (sub_dir / "solution.md").write_text(str(solution))
    (sub_dir / "blueprint.json").write_text(json.dumps(blueprint, indent=2))
    (sub_dir / "trace.log").write_text("\n".join(str(t) for t in trace))
    (sub_dir / "miner_notes.txt").write_text(notes)
    (sub_dir / "challenge.txt").write_text(challenge)
    (sub_dir / "verification.txt").write_text(verification)
    (sub_dir / "deterministic_tooling.txt").write_text(deterministic_tooling)

    oracle_info = {
        "validation_score": getattr(manager.validator, 'last_score', 0.0),
        "timestamp": datetime.now().isoformat()
    }
    (sub_dir / "validation_oracle.json").write_text(json.dumps(oracle_info, indent=2))

    with zipfile.ZipFile(sub_dir / "submission_package.zip", "w") as z:
        for f in sub_dir.glob("*"):
            if f.is_file() and f.suffix != ".zip":
                z.write(f, f.name)

    with open(sub_dir / "submission_package.zip", "rb") as f:
        st.download_button(
            "Download Submission Package", 
            data=f.read(), 
            file_name=f"sn63_{ts}.zip", 
            mime="application/zip"
        )

st.caption("© 1944–2026 ALLIED ENIGMA MINER • PUSHING HUMANITY TO THE NEXT STAGE")
