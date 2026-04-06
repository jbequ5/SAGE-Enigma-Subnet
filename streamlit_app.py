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
        background: rgba(0, 0, 0, 0.92);
        z-index: -1;
        animation: scanline 8s linear infinite;
    }
    @keyframes scanline { 0% { background-position: 0 0; } 100% { background-position: 0 100%; } }

    h1, h2, h3 { 
        color: #00ff9d !important; 
        font-family: 'Courier New', monospace; 
        text-shadow: 0 0 30px #00ff9d, 0 0 60px #00aa77; 
        letter-spacing: 4px; 
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

st.markdown("<h1 style='text-align: center;'>🔒 ALLIED ENIGMA MINER v1.0</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #ffaa00;'>TOP SECRET • BUNKER COMMAND POST 1944 • SN63 QUANTUM INNOVATE</h3>", unsafe_allow_html=True)
st.caption("🔴 ENIGMA ROTORS SPINNING • LIVE DECRYPTION MISSION ACTIVE • SELF-OPTIMIZING EMBODIED ORGANISM")

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
    efs = getattr(manager, 'last_efs', 0.0)
    st.metric("VALIDATION ORACLE SCORE", f"{score:.3f}", delta=f"EFS {efs:.3f}")
with col3:
    if st.button("🧹 ABORT MISSION"):
        for k in list(st.session_state.keys()):
            if k != "arbos_manager":
                del st.session_state[k]
        st.rerun()

# ====================== MISSION TABS ======================
tab_command, tab_brain, tab_recon, tab_organism = st.tabs([
    "📡 COMMAND BRIDGE", 
    "🧠 BRAIN VAULT", 
    "🛰️ RECON & INTEL", 
    "🔬 ORGANISM CORE (v0.6)"
])

with tab_command:
    st.subheader("🎯 MISSION TARGET")
    challenge = st.text_area(
        "SN63 Challenge Description (Quantum Innovate task)",
        height=160,
        placeholder="Describe the full problem in detail...",
        key="challenge_input"
    )
    
    st.subheader("✅ VERIFICATION PROTOCOL")
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

    if st.button("🚀 LAUNCH FULL MISSION", type="primary", use_container_width=True):
        with st.spinner("Planning Arbos → Orchestrator → Dynamic Swarm..."):
            plan = manager.plan_challenge(
                goal_md=load_brain_component("core_strategy"),
                challenge=challenge,
                enhancement_prompt="",
                compute_mode=st.session_state.get("compute_source", "local_gpu")
            )
            if "error" not in plan:
                final_solution = manager.execute_full_cycle(plan, challenge, verification_instructions)
                st.session_state.final_solution = final_solution
                st.success("✅ Mission executed — view results in ORGANISM CORE tab")
                st.rerun()

with tab_brain:
    st.header("🧠 BRAIN VAULT — Living Second Brain")
    st.caption("Mycelial + wiki + bio heuristics. Edit live.")

    edit_mode = st.radio("Edit Mode", ["Quick Toggles", "Individual Components"], horizontal=True)

    if edit_mode == "Quick Toggles":
        toggles_content = load_brain_component("toggles")
        edited_toggles = st.text_area("Centralized Toggles", value=toggles_content, height=300)
        if st.button("Save Toggles"):
            with open("goals/brain/toggles.md", "w", encoding="utf-8") as f:
                f.write(edited_toggles)
            st.success("✅ Toggles saved")
            st.rerun()
    else:
        component_options = {
            "Shared Core Principles": "principles/shared_core",
            "Bio Strategy": "principles/bio_strategy",
            "English Evolution": "principles/english_evolution",
            "Wiki Strategy": "principles/wiki_strategy",
            "Compression Prompt": "principles/compression"
        }
        selected = st.selectbox("Choose Layer", list(component_options.keys()))
        path = component_options[selected]
        content = load_brain_component(path)
        edited = st.text_area(f"Editing {selected}", value=content, height=380)
        if st.button(f"Save {selected}"):
            full_path = f"goals/brain/{path}.md"
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(edited)
            st.success(f"✅ Saved {selected}")
            st.rerun()

with tab_recon:
    st.subheader("🛰️ RECON SWARM — ToolHunter & Expert Input")
    hunter_gap = st.text_area("Current Gap or Subtask", height=100, placeholder="e.g. Need better quantum circuit simulator...")
    if st.button("🚀 LAUNCH RECON SWARM"):
        with st.spinner("Scanning ToolHunter + ReadyAI + Agent-Reach..."):
            hunt_result = manager._tool_hunter(hunter_gap, "recon") if hasattr(manager, "_tool_hunter") else {"status": "success", "proposals": ["ToolHunter ready"]}
            st.session_state.toolhunter_results = hunt_result
            st.success("✅ RECON COMPLETE")
            st.json(hunt_result)

    st.subheader("Expert Input Mode")
    tab_tool, tab_invariant, tab_strategy = st.tabs(["New Tool", "Symbolic Invariant", "Strategy Change"])

    with tab_tool:
        tool_name = st.text_input("Tool Name")
        tool_desc = st.text_area("Description / What it should do", height=100)
        if st.button("Submit New Tool Proposal"):
            if tool_name and tool_desc:
                proposal = {"name": tool_name, "description": tool_desc, "code": "AUTO_GENERATE", "type": "tool"}
                manager.save_to_memdir(f"tool_proposal_{int(time.time())}", proposal)
                st.success(f"✅ Tool proposal '{tool_name}' saved. Will be processed after next run.")
            else:
                st.error("Name and description required")

    with tab_invariant:
        inv_name = st.text_input("Invariant Name")
        inv_code = st.text_area("SymPy / Deterministic Code", height=150)
        if st.button("Submit Symbolic Invariant"):
            if inv_name and inv_code:
                proposal = {"name": inv_name, "code": inv_code, "type": "invariant"}
                manager.save_to_memdir(f"invariant_{int(time.time())}", proposal)
                st.success("✅ Symbolic invariant submitted")
    
    with tab_strategy:
        strat_desc = st.text_area("Strategy / Approach Suggestion", height=120)
        if st.button("Submit Strategy Change"):
            if strat_desc:
                manager.save_to_memdir(f"strategy_{int(time.time())}", {"description": strat_desc})
                st.success("✅ Strategy suggestion saved")

with tab_organism:
    st.header("🔬 ORGANISM CORE — v0.6 Self-Optimizing Embodied Organism")
    st.caption("All features are toggleable, replay-tested, and EFS-gated.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Run Meta-Tuning Cycle", type="primary"):
            with st.spinner("Running EFS tournament..."):
                manager.meta_tuner.run_meta_tuning_cycle(stall_detected=manager._is_stale_regime(manager.recent_scores))
            st.success("✅ Meta-tuning complete")
            st.rerun()

        if st.button("📼 Trigger Retrospective on Latest MP4"):
            with st.spinner("Decoding latest archive..."):
                manager.history_hunter.trigger_retrospective()
            st.success("✅ Retrospective complete")

    with col2:
        if st.button("🔍 Run Full-System Audit"):
            with st.spinner("Auditing MP4 backlog..."):
                audit = manager.history_hunter.run_audit_on_mp4_backlog()
            st.success(audit.get("summary", "Audit complete"))
            st.json(audit)

    st.subheader("Toggle Controls")
    c1, c2, c3 = st.columns(3)
    with c1:
        manager.toggles["embodiment_enabled"] = st.checkbox("Embodiment Modules", value=manager.toggles.get("embodiment_enabled", True))
    with c2:
        manager.toggles["rps_pps_enabled"] = st.checkbox("Resonance + Photoelectric Pattern Surfacers", value=manager.toggles.get("rps_pps_enabled", True))
    with c3:
        manager.toggles["hybrid_ingestion_enabled"] = st.checkbox("Hybrid Genome/Paper Ingestion", value=manager.toggles.get("hybrid_ingestion_enabled", True))

    if st.button("Apply All v0.6 Toggles"):
        manager.update_toggles(manager.toggles)
        st.success("✅ Toggles applied — organism updated")

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("⚙️ MISSION CONTROLS")
    manager.enable_grail = st.checkbox("Grail Reinforcement (on high scores)", value=True)

    st.subheader("🔌 Compute")
    compute_option = st.radio("Source", ["Local GPU (Ollama)", "Custom"], key="compute_sidebar")
    if compute_option == "Custom":
        endpoint = st.text_input("Endpoint URL")
        if endpoint:
            manager.set_compute_source("custom", endpoint)
    else:
        manager.set_compute_source("local_gpu")

    st.divider()
    if st.button("🧪 Run Scientist Mode"):
        manager.run_scientist_mode(5)
        st.success("Scientist Mode complete")

    st.caption("© 1944–2026 ALLIED ENIGMA MINER • v1.0 Embodied Organism")

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
