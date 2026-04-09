import streamlit as st
import json
import zipfile
from pathlib import Path
from datetime import datetime
import time
import os

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="ALLIED ENIGMA MINER",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

from agents.arbos_manager import ArbosManager
from goals.brain_loader import load_brain_component
from code_editor import code_editor

# ====================== CINEMATIC BUNKER THEME (Enhanced) ======================
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
        background: linear-gradient(rgba(0, 0, 0, 0.88), rgba(0, 20, 10, 0.95));
        z-index: -1;
    }

    h1, h2, h3 { 
        color: #00ff9d !important; 
        font-family: 'Courier New', monospace; 
        text-shadow: 0 0 30px #00ff9d, 0 0 60px #00aa77; 
        letter-spacing: 4px; 
    }

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
        box-shadow: 0 0 40px #00ff9d;
        transform: scale(1.05);
    }

    .metric-card {
        background: rgba(0, 30, 15, 0.7);
        border: 2px solid #00ff9d;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }

    .live-dot {
        display: inline-block;
        width: 10px;
        height: 10px;
        background: #00ff9d;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }

    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🔒 ALLIED ENIGMA MINER v1.0</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #ffaa00;'>TOP SECRET • BUNKER COMMAND POST 1944 • SN63 QUANTUM INNOVATE</h3>", unsafe_allow_html=True)

st.caption("""
<span class='live-dot'></span> ENIGMA ROTORS SPINNING • LIVE DECRYPTION MISSION ACTIVE • 
SELF-OPTIMIZING EMBODIED ORGANISM • v0.8+ FULLY FRAGMENTED MEMORY SYSTEM
""", unsafe_allow_html=True)

# ====================== SESSION STATE ======================
if "manager" not in st.session_state:
    st.session_state.manager = ArbosManager()

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "high_level_plan" not in st.session_state:
    st.session_state.high_level_plan = None

if "trace_log" not in st.session_state:
    st.session_state.trace_log = []

manager = st.session_state.manager

# ====================== LIVE HEADER METRICS ======================
col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
with col1:
    st.markdown("🔄 <span class='rotor'>⚙️⚙️⚙️</span> ROTORS ACTIVE", unsafe_allow_html=True)
with col2:
    score = getattr(manager.validator, 'last_score', 0.0)
    efs = getattr(manager, 'last_efs', 0.0)
    st.metric("VALIDATION ORACLE SCORE", f"{score:.3f}", delta=f"EFS {efs:.3f}")
with col3:
    hetero = manager._compute_heterogeneity_score().get("heterogeneity_score", 0.72) if hasattr(manager, '_compute_heterogeneity_score') else 0.72
    st.metric("HETEROGENEITY", f"{hetero:.3f}", delta="DYNAMIC")
with col4:
    if st.button("🧹 ABORT MISSION", type="secondary"):
        for k in list(st.session_state.keys()):
            if k != "manager":
                del st.session_state[k]
        st.rerun()

# ====================== MAIN TABS ======================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📡 COMMAND BRIDGE", 
    "🧠 BRAIN VAULT", 
    "🛰️ RECON & INTEL", 
    "🔬 ORGANISM CORE", 
    "📜 DVR CONTRACT MONITOR",
    "📦 PACKAGE & EXPORT"
])

with tab1:
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

    # ====================== TOOLHUNTER RECOMMENDATIONS ======================
    st.subheader("🛠️ ToolHunter Recommendations (v0.8+)")
    st.caption("Proactive tools detected from contract, memory graph, and gap analysis. Add with one click.")

    plan = st.session_state.get("high_level_plan", {}) or {}
    recommended = plan.get("recommended_tools", [])

    if recommended:
        for tool in recommended:
            tool_name = tool if isinstance(tool, str) else tool.get("name", "Unnamed Tool")
            install_cmd = tool.get("install_cmd", "") if isinstance(tool, dict) else ""

            col1, col2, col3 = st.columns([3.5, 2, 2.5])
            with col1:
                st.write(f"**{tool_name}**")
            with col2:
                persistent = st.checkbox("Persistent venv", value=True, key=f"persist_{tool_name}")
            with col3:
                if st.button("✅ Add & Install", key=f"add_{tool_name}", use_container_width=True):
                    with st.spinner(f"Creating environment for {tool_name}..."):
                        result = manager.tool_env_manager.create_or_get_env(
                            tool_name=tool_name,
                            persistent=persistent,
                            requirements=tool.get("requirements", []) if isinstance(tool, dict) else None,
                            install_cmd=install_cmd
                        )
                        if result.get("status") == "success":
                            st.success(f"✅ {tool_name} environment ready!")
                            st.caption(f"Python: `{result.get('python_exe', 'ready')}`")
                        else:
                            st.error(f"❌ Failed: {result.get('error', 'unknown error')}")
                    st.rerun()
    else:
        st.info("No new tools recommended yet. ToolHunter will suggest based on contract gaps and memory graph.")

    # ====================== LAUNCH MISSION ======================
    if st.button("🚀 LAUNCH FULL MISSION", type="primary", use_container_width=True):
        with st.spinner("Planning Arbos → Contract Generation → Dry-Run Gate → Advanced Swarm → Synthesis..."):
            plan = manager.plan_challenge(
                goal_md=manager.extra_context,
                challenge=challenge,
                enhancement_prompt="Maximize verifier compliance, heterogeneity across five axes, deterministic/symbolic paths first."
            )
            st.session_state.high_level_plan = plan
            if "error" not in plan:
                final_solution = manager.execute_full_cycle(plan, challenge, verification_instructions)
                st.session_state.last_result = final_solution
                st.success("✅ Mission executed — view results in ORGANISM CORE + DVR MONITOR tabs")
                st.rerun()

with tab2:
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

with tab3:
    st.subheader("🛰️ RECON SWARM — ToolHunter & Expert Input")
    hunter_gap = st.text_area("Current Gap or Subtask", height=100, placeholder="e.g. Need better quantum circuit simulator...")
    if st.button("🚀 LAUNCH RECON SWARM"):
        with st.spinner("Scanning ToolHunter + ReadyAI + Agent-Reach..."):
            hunt_result = manager._tool_hunter(hunter_gap, "recon") if hasattr(manager, "_tool_hunter") else {"status": "success", "proposals": ["ToolHunter ready"]}
            st.session_state.toolhunter_results = hunt_result
            st.success("✅ RECON COMPLETE")
            st.json(hunt_result)

with tab4:
    st.header("🔬 ORGANISM CORE — v1.0 Self-Optimizing Embodied Organism")
    st.caption("All features are toggleable, replay-tested, and EFS-gated.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧬 Run Meta-Tuning Cycle", type="primary"):
            with st.spinner("Evolutionary tournament running..."):
                manager.run_meta_tuning_cycle()
            st.success("✅ Meta-Tuning complete")
    with col2:
        if st.button("🌌 Trigger Pattern Surfacers"):
            if hasattr(manager, "rps") and hasattr(manager, "pps"):
                manager.rps.surface_resonance(st.session_state.get("last_result", {}))
                manager.pps.surface_photoelectric(st.session_state.get("last_result", {}))
                st.success("✅ Pattern surfacers activated")

    st.subheader("Toggle Controls")
    c1, c2, c3 = st.columns(3)
    with c1:
        manager.toggles["embodiment_enabled"] = st.checkbox("Embodiment Modules", value=True)
    with c2:
        manager.toggles["rps_pps_enabled"] = st.checkbox("Resonance + Photoelectric", value=True)
    with c3:
        manager.toggles["hybrid_ingestion_enabled"] = st.checkbox("Hybrid Ingestion", value=True)

with tab5:
    st.header("📜 DVR CONTRACT MONITOR — Live Verifier-First Pipeline")
    if "last_result" in st.session_state and isinstance(st.session_state.last_result, dict) and "verifiability_contract" in st.session_state.last_result:
        st.json(st.session_state.last_result["verifiability_contract"])
    else:
        st.info("Run a mission to see live contract data")

with tab6:
    st.header("📦 PACKAGE & EXPORT")
    if "last_result" in st.session_state and st.session_state.last_result:
        if st.button("📦 Package & Download Full Submission"):
            _package_submission(
                solution=st.session_state.last_result.get("merged_candidate", ""),
                blueprint=st.session_state.get("high_level_plan", {}),
                trace=st.session_state.get("trace_log", []),
                notes="Full DVRP run with advanced synthesis and meta-tuning",
                challenge=challenge,
                verification=verification_instructions,
                deterministic_tooling="SymPy + verifier snippets"
            )
    else:
        st.info("Run a mission first to enable packaging.")

st.caption("© 1944–2026 ALLIED ENIGMA MINER • PUSHING HUMANITY TO THE NEXT STAGE")

# ====================== PACKAGE FUNCTION ======================
def _package_submission(solution: str, blueprint: Dict, trace: list, notes: str, 
                        challenge: str, verification: str, deterministic_tooling: str):
    """Package the full submission for upload."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"enigma_submission_{timestamp}.zip"
    
    with zipfile.ZipFile(package_name, "w") as zipf:
        zipf.writestr("solution.md", solution)
        zipf.writestr("blueprint.json", json.dumps(blueprint, indent=2))
        zipf.writestr("trace_log.json", json.dumps(trace, indent=2))
        zipf.writestr("verification_instructions.md", verification)
        zipf.writestr("README.txt", f"""ALLIED ENIGMA MINER SUBMISSION
Challenge: {challenge}
Timestamp: {timestamp}
Notes: {notes}
Deterministic Tooling: {deterministic_tooling}""")

    with open(package_name, "rb") as f:
        st.download_button(
            label="📥 Download Submission Package",
            data=f,
            file_name=package_name,
            mime="application/zip"
        )
    
    st.success(f"✅ Package created: {package_name}")
