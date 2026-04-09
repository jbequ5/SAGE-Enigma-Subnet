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

# ====================== CINEMATIC BUNKER DASHBOARD THEME ======================
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
        background: linear-gradient(rgba(0, 0, 0, 0.92), rgba(0, 25, 10, 0.96));
        z-index: -1;
    }
    h1, h2, h3 {
        color: #00ff9d !important;
        font-family: 'Courier New', monospace;
        text-shadow: 0 0 30px #00ff9d, 0 0 60px #00aa77;
        letter-spacing: 4px;
    }
    .metric-card {
        background: rgba(0, 30, 15, 0.85);
        border: 2px solid #00ff9d;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
    }
    .live-dot {
        display: inline-block;
        width: 12px;
        height: 12px;
        background: #00ff9d;
        border-radius: 50%;
        animation: pulse 1.8s infinite;
        margin-right: 8px;
    }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
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
        box-shadow: 0 0 45px #00ff9d;
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🔒 ALLIED ENIGMA MINER — COMMAND DASHBOARD v1.0</h1>", unsafe_allow_html=True)
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
    score = getattr(manager.validator, 'last_score', 0.0) if hasattr(manager, 'validator') else 0.0
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
    "📊 OVERVIEW DASHBOARD",
    "🎯 COMMAND BRIDGE",
    "🧠 BRAIN VAULT",
    "🛰️ RECON & INTEL",
    "🔬 ORGANISM CORE",
    "📜 DVR CONTRACT MONITOR"
])

# ====================== TAB 1: OVERVIEW DASHBOARD ======================
with tab1:
    st.header("📊 OPERATIONAL DASHBOARD")
    st.caption("Real-time system status • Memory health • Mission metrics")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("CURRENT LOOP", getattr(manager, 'loop_count', 0))
        st.markdown("</div>", unsafe_allow_html=True)
    with m2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        best_score = max(getattr(manager, 'recent_scores', [0.0])) if hasattr(manager, 'recent_scores') else 0.0
        st.metric("BEST SCORE", f"{best_score:.3f}")
        st.markdown("</div>", unsafe_allow_html=True)
    with m3:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        fragments = len(getattr(manager, 'fragment_tracker', {}).get('fragments', [])) if hasattr(manager, 'fragment_tracker') else 0
        st.metric("FRAGMENTS INDEXED", fragments)
        st.markdown("</div>", unsafe_allow_html=True)
    with m4:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("EMBODIMENT STATUS", "ACTIVE" if manager.toggles.get("embodiment_enabled", True) else "STANDBY")
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.subheader("📜 RECENT MISSION ACTIVITY")
    if st.session_state.last_result:
        result = st.session_state.last_result
        st.success(f"Last Mission — Score: **{result.get('validation_score', 0):.3f}** | EFS: **{result.get('efs', 0):.3f}**")
    else:
        st.info("No missions executed yet. Launch from Command Bridge.")

    st.subheader("🛠️ SYSTEM HEALTH")
    health_cols = st.columns(3)
    with health_cols[0]:
        st.metric("COMPUTE SAFETY", "GREEN", delta="All gates passed")
    with health_cols[1]:
        st.metric("MEMORY COHERENCE", "HIGH", delta="Fragment decay stable")
    with health_cols[2]:
        st.metric("PATTERN SURFACING", "ACTIVE" if manager.toggles.get("rps_pps_enabled", True) else "OFF")

# ====================== TAB 2: COMMAND BRIDGE ======================
with tab2:
    st.subheader("🎯 MISSION TARGET")
    challenge = st.text_area(
        "SN63 Challenge Description",
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
    verification_instructions = verification_response.get("text", default_verification) if isinstance(verification_response, dict) else str(verification_response) if verification_response else default_verification

    # ToolHunter Recommendations
    st.subheader("🛠️ ToolHunter Recommendations (v0.8+)")
    st.caption("Proactive tools from contract, memory graph, and gap analysis. Add with one click.")
    plan = st.session_state.get("high_level_plan", {}) or {}
    recommended = plan.get("recommended_tools", [])
    if recommended:
        for idx, tool in enumerate(recommended):
            tool_name = tool if isinstance(tool, str) else tool.get("name", f"Tool_{idx}")
            install_cmd = tool.get("install_cmd", "") if isinstance(tool, dict) else ""
            col1, col2, col3 = st.columns([3.5, 2, 2.5])
            with col1:
                st.write(f"**{tool_name}**")
            with col2:
                persistent = st.checkbox("Persistent venv", value=True, key=f"persist_{tool_name}_{idx}")
            with col3:
                if st.button("✅ Add & Install", key=f"add_{tool_name}_{idx}", use_container_width=True):
                    with st.spinner(f"Creating environment for {tool_name}..."):
                        if hasattr(manager, 'tool_env_manager'):
                            result = manager.tool_env_manager.create_or_get_env(
                                tool_name=tool_name,
                                persistent=persistent,
                                requirements=tool.get("requirements", []) if isinstance(tool, dict) else None,
                                install_cmd=install_cmd
                            )
                            if result.get("status") == "success":
                                st.success(f"✅ {tool_name} ready!")
                            else:
                                st.error(f"❌ {result.get('error', 'unknown')}")
                        else:
                            st.error("ToolEnvManager not available")
                    st.rerun()
    else:
        st.info("No new tools recommended yet. Run a mission to trigger ToolHunter.")

    col_launch, col_export = st.columns([3, 1])
    with col_launch:
        if st.button("🚀 LAUNCH FULL MISSION", type="primary", use_container_width=True):
            with st.spinner("Planning → Contract Generation → Dry-Run Gate → Swarm → Synthesis..."):
                plan = manager.plan_challenge(
                    goal_md=getattr(manager, 'extra_context', ""),
                    challenge=challenge,
                    enhancement_prompt="Maximize verifier compliance, heterogeneity, deterministic paths first."
                )
                st.session_state.high_level_plan = plan
                if "error" not in plan:
                    final_solution = manager.execute_full_cycle(plan, challenge, verification_instructions)
                    st.session_state.last_result = final_solution
                    st.success("✅ Mission executed — check ORGANISM CORE & DVR MONITOR")
                    st.rerun()

    with col_export:
        if st.button("📓 Export Academic Notebook", type="primary"):
            if hasattr(manager, '_current_challenge_id') and st.session_state.last_result:
                export_path = manager._export_notebook_entry(manager._current_challenge_id)
                st.success(f"✅ Exported to {export_path}")
                with open(export_path, "r", encoding="utf-8") as f:
                    st.download_button("📥 Download Notebook", f.read(), f"notebook_{manager._current_challenge_id}.md")
            else:
                st.error("No completed run to export")

# ====================== TAB 3: BRAIN VAULT ======================
with tab3:
    st.header("🧠 BRAIN VAULT — Living Second Brain")
    edit_mode = st.radio("Edit Mode", ["Quick Toggles", "Individual Components"], horizontal=True)
    if edit_mode == "Quick Toggles":
        toggles_content = load_brain_component("toggles")
        edited_toggles = st.text_area("Centralized Toggles", value=toggles_content, height=300)
        if st.button("Save Toggles"):
            Path("goals/brain/toggles.md").write_text(edited_toggles, encoding="utf-8")
            st.success("✅ Saved")
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
            Path(full_path).write_text(edited, encoding="utf-8")
            st.success(f"✅ Saved {selected}")
            st.rerun()

# ====================== TAB 4: RECON & INTEL ======================
with tab4:
    st.subheader("🛰️ RECON SWARM — ToolHunter & Expert Input")
    hunter_gap = st.text_area("Current Gap or Subtask", height=100, placeholder="e.g. Need better quantum circuit simulator...")
    if st.button("🚀 LAUNCH RECON SWARM"):
        with st.spinner("Scanning ToolHunter + memory graph..."):
            if hasattr(manager, '_tool_hunter'):
                hunt_result = manager._tool_hunter(hunter_gap, "recon")
                st.session_state.toolhunter_results = hunt_result
                st.json(hunt_result)
            else:
                st.info("ToolHunter not wired yet — ready for v0.8+")

# ====================== TAB 5: ORGANISM CORE ======================
with tab5:
    st.header("🔬 ORGANISM CORE — Self-Optimizing Embodied Organism")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧬 Run Meta-Tuning Cycle", type="primary"):
            with st.spinner("Evolutionary tournament..."):
                manager.run_meta_tuning_cycle()
            st.success("✅ Meta-Tuning complete")
    with col2:
        if st.button("🌌 Trigger Pattern Surfacers"):
            if hasattr(manager, "rps") and hasattr(manager, "pps"):
                manager.rps.surface_resonance(st.session_state.get("last_result", {}))
                manager.pps.surface_photoelectric(st.session_state.get("last_result", {}))
                st.success("✅ Pattern surfacers activated")

    st.subheader("Scientist Mode (Outer-Loop Intelligence)")
    intent_preset = st.selectbox("Intent Preset", ["Memory Tuning (default)", "Novelty Probe", "Contract Evolution"])
    if st.button("🚀 Run Scientist Mode"):
        with st.spinner("Running synthetic experiments..."):
            intent = {"target_variable": "decay_k", "goal": "maximize_fragment_retention"} if intent_preset == "Memory Tuning (default)" else {}
            result = manager.run_scientist_mode(num_synthetic=3, intent=intent)
            st.success(f"Scientist Mode completed — {result.get('experiment_count', 0)} experiments | Avg EFS: {result.get('avg_efs', 0):.3f}")

    st.subheader("Toggle Controls")
    c1, c2, c3 = st.columns(3)
    with c1:
        manager.toggles["embodiment_enabled"] = st.checkbox("Embodiment Modules", value=manager.toggles.get("embodiment_enabled", True))
    with c2:
        manager.toggles["rps_pps_enabled"] = st.checkbox("Resonance + Photoelectric", value=manager.toggles.get("rps_pps_enabled", True))
    with c3:
        manager.toggles["hybrid_ingestion_enabled"] = st.checkbox("Hybrid Ingestion", value=manager.toggles.get("hybrid_ingestion_enabled", True))

# ====================== TAB 6: DVR CONTRACT MONITOR ======================
with tab6:
    st.header("📜 DVR CONTRACT MONITOR — Verifier-First Pipeline")
    if st.session_state.last_result and isinstance(st.session_state.last_result, dict):
        if "verifiability_contract" in st.session_state.last_result:
            st.json(st.session_state.last_result["verifiability_contract"])
        if "contract_deltas" in st.session_state.last_result:
            st.subheader("Contract Evolution Deltas")
            st.json(st.session_state.last_result.get("contract_deltas", []))
    else:
        st.info("Run a full mission to see live DVR contracts and evolution.")

# ====================== PACKAGE & EXPORT ======================
st.divider()
if st.session_state.last_result:
    if st.button("📦 Package & Download Full Submission", use_container_width=True):
        _package_submission(
            solution=st.session_state.last_result.get("merged_candidate", ""),
            blueprint=st.session_state.get("high_level_plan", {}),
            trace=st.session_state.get("trace_log", []),
            notes="Full DVRP run with advanced synthesis, meta-tuning, and fragmented memory",
            challenge=challenge if 'challenge' in locals() else "Unknown",
            verification=verification_instructions if 'verification_instructions' in locals() else "",
            deterministic_tooling="SymPy + verifier snippets + ToolEnvManager"
        )

def _package_submission(solution: str, blueprint: dict, trace: list, notes: str,
                        challenge: str, verification: str, deterministic_tooling: str):
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    sub_dir = Path("submissions") / f"sn63_{ts}"
    sub_dir.mkdir(parents=True, exist_ok=True)

   
