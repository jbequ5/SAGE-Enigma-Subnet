import streamlit as st
import json
import zipfile
from pathlib import Path
from datetime import datetime
import time

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

# ====================== CINEMATIC BUNKER THEME ======================
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

st.markdown("<h1 style='text-align: center;'>🔒 ALLIED ENIGMA MINER v1.0</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #ffaa00;'>TOP SECRET • BUNKER COMMAND POST 1944 • SN63 QUANTUM INNOVATE</h3>", unsafe_allow_html=True)
st.caption("🔴 ENIGMA ROTORS SPINNING • LIVE DECRYPTION MISSION ACTIVE • SELF-OPTIMIZING EMBODIED ORGANISM")

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

# ====================== LIVE HEADER ======================
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    st.markdown("🔄 <span class='rotor'>⚙️⚙️⚙️</span> ROTORS ACTIVE", unsafe_allow_html=True)
with col2:
    score = getattr(manager.validator, 'last_score', 0.0)
    efs = getattr(manager, 'last_efs', 0.0)
    c_val = getattr(manager.validator, 'last_c', 0.75)
    st.metric("VALIDATION ORACLE SCORE", f"{score:.3f}", delta=f"EFS {efs:.3f} | c {c_val:.3f}")
with col3:
    if st.button("🧹 ABORT MISSION"):
        for k in list(st.session_state.keys()):
            if k != "manager":
                del st.session_state[k]
        st.rerun()

# ====================== MAIN TABS ======================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📡 COMMAND BRIDGE", 
    "🧠 BRAIN VAULT", 
    "🛰️ RECON & INTEL", 
    "🔬 ORGANISM CORE", 
    "📜 DVR CONTRACT MONITOR"
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

    if st.button("🚀 LAUNCH FULL MISSION", type="primary", use_container_width=True):
        with st.spinner("Planning Arbos → Contract Generation → Dry-Run Gate → Advanced Swarm → Synthesis..."):
            plan = manager.plan_challenge(
                goal_md=manager.extra_context,
                challenge=challenge,
                enhancement_prompt="Maximize verifier compliance, heterogeneity, and deterministic paths."
            )
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
    if "last_result" in st.session_state and "verifiability_contract" in st.session_state.last_result:
        st.json(st.session_state.last_result["verifiability_contract"])
    else:
        st.info("Run a mission to see live contract data")

# ====================== PACKAGING ======================
if "last_result" in st.session_state:
    st.divider()
    if st.button("📦 Package & Download Submission"):
        _package_submission(
            solution=st.session_state.last_result.get("merged_candidate", ""),
            blueprint=st.session_state.get("high_level_plan", {}),
            trace=st.session_state.get("trace_log", []),
            notes="Full DVRP run with advanced synthesis and meta-tuning",
            challenge=challenge,
            verification=verification_instructions,
            deterministic_tooling="SymPy + verifier snippets"
        )

st.caption("© 1944–2026 ALLIED ENIGMA MINER • PUSHING HUMANITY TO THE NEXT STAGE")
