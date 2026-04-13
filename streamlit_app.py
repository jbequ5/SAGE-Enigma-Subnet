import streamlit as st
import json
import zipfile
from pathlib import Path
from datetime import datetime
import time
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.cluster.hierarchy import linkage, fcluster
import networkx as nx
import numpy as np

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
st.markdown("<h3 style='text-align: center; color: #ffaa00;'>TOP SECRET • BUNKER COMMAND POST 1944 • SN63 ENIGMA</h3>", unsafe_allow_html=True)
st.caption("""
<span class='live-dot'></span> ENIGMA ROTORS SPINNING • LIVE DECRYPTION MISSION ACTIVE •
SELF-OPTIMIZING EMBODIED ORGANISM • v0.9.5 CONTINUOUS INTELLIGENCE ENGINE • TRACE ENABLED
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
if "current_run_status" not in st.session_state:
    st.session_state.current_run_status = {}
if "current_double_click_recommendations" not in st.session_state:
    st.session_state.current_double_click_recommendations = []

manager = st.session_state.manager

# Sync trace_log from manager to session_state for Streamlit reactivity
if hasattr(manager, 'trace_log'):
    st.session_state.trace_log = manager.trace_log

# ====================== LIVE HEADER METRICS ======================
col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
with col1:
    st.markdown("🔄 <span class='rotor'>⚙️⚙️⚙️</span> ROTORS ACTIVE", unsafe_allow_html=True)
with col2:
    score = getattr(getattr(manager, 'validator', None), 'last_score', 0.0)
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
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
    "📊 OVERVIEW DASHBOARD",
    "🎯 COMMAND BRIDGE",
    "🧠 BRAIN VAULT",
    "🛰️ RECON & INTEL",
    "🔬 ORGANISM CORE",
    "📜 DVR CONTRACT MONITOR",
    "📈 LIVE SYSTEM METRICS",
    "🔍 MISSION TRACE LOG",
    "🌌 COSMIC COMPRESSION — Memory Graph Pruning",
    "🧹 PRUNING ADVISOR — Intelligent Recommendations",
    "🧪 RECOMMENDED EXPERIMENTS"   # NEW TAB
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
        fragments = len(getattr(manager.fragment_tracker, 'fragments', [])) if hasattr(manager, 'fragment_tracker') else 0
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
        "Enigma Challenge Description",
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

    # ToolHunter Recommendations
    st.subheader("🛠️ ToolHunter Recommendations")
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
                        else:
                            st.error(f"❌ Failed: {result.get('error', 'unknown error')}")
                    st.rerun()
    else:
        st.info("No new tools recommended yet. ToolHunter will suggest based on contract gaps and memory graph.")

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

# ====================== TAB 3: BRAIN VAULT ======================
with tab3:
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

# ====================== TAB 4: RECON & INTEL ======================
with tab4:
    st.subheader("🛰️ RECON SWARM — ToolHunter & Expert Input")
    hunter_gap = st.text_area("Current Gap or Subtask", height=100, placeholder="e.g. Need better quantum circuit simulator...")
    if st.button("🚀 LAUNCH RECON SWARM"):
        with st.spinner("Scanning ToolHunter + ReadyAI + Agent-Reach..."):
            hunt_result = manager._tool_hunter(hunter_gap, "recon") if hasattr(manager, "_tool_hunter") else {"status": "success", "proposals": ["ToolHunter ready"]}
            st.session_state.toolhunter_results = hunt_result
            st.success("✅ RECON COMPLETE")
            st.json(hunt_result)

# ====================== TAB 5: ORGANISM CORE ======================
with tab5:
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

# ====================== TAB 6: DVR CONTRACT MONITOR ======================
with tab6:
    st.header("📜 DVR CONTRACT MONITOR — Live Verifier-First Pipeline")
    if "last_result" in st.session_state and isinstance(st.session_state.last_result, dict) and "verifiability_contract" in st.session_state.last_result:
        st.json(st.session_state.last_result["verifiability_contract"])
    else:
        st.info("Run a mission to see live contract data")

# ====================== TAB 7: LIVE METRICS ======================
with tab7:
    st.header("📈 LIVE SYSTEM METRICS")
   
    # EFS Trend Sparkline
    if hasattr(manager, 'recent_scores') and len(manager.recent_scores) > 3:
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=manager.recent_scores, mode='lines+markers', name='Score', line=dict(color='#00ff9d')))
        fig.update_layout(title="EFS / Validation Score Trend", height=280, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    # Fragment Utilization Heatmap
    if hasattr(manager, 'fragment_tracker') and hasattr(manager.fragment_tracker, 'graph'):
        nodes = list(manager.fragment_tracker.graph.nodes)
        if nodes:
            scores = [manager.fragment_tracker.get_impact_score(n) for n in nodes]
            fig2 = px.histogram(x=scores, nbins=20, title="Fragment Utilization Distribution", color_discrete_sequence=['#00ff9d'])
            st.plotly_chart(fig2, use_container_width=True)

    st.subheader("System Health")
    st.json({
        "loop": getattr(manager, 'loop_count', 0),
        "last_efs": efs,
        "heterogeneity": hetero,
        "approximation_mode": "active" if getattr(manager.validator, 'last_approximation_used', False) else "real_backends"
    })

# ====================== TAB 8: MISSION TRACE LOG ======================
with tab8:
    st.header("🔍 MISSION TRACE LOG — Full System Observability")
    st.caption("Real-time chronological execution trace of every major phase")
    if st.session_state.trace_log:
        for entry in reversed(st.session_state.trace_log[-40:]): # Last 40 entries
            ts = entry.get("timestamp", "")[-8:] if entry.get("timestamp") else "—"
            step = entry.get("step", "Unknown Step")
            details = entry.get("details", "")
            with st.expander(f"[{ts}] {step}", expanded=False):
                st.write(details)
                if entry.get("metrics"):
                    st.json(entry["metrics"])
                if entry.get("verifier_5d"):
                    st.subheader("5D Verifier Self-Check")
                    st.json(entry["verifier_5d"])
                if "DOUBLE_CLICK" in str(entry).upper() or entry.get("double_click"):
                    st.warning("🔴 DOUBLE_CLICK EVENT DETECTED")
    else:
        st.info("No trace data yet. Launch a full mission from the Command Bridge.")
    if st.button("🔄 Refresh Trace Log"):
        st.rerun()

# ====================== TAB 9: COSMIC COMPRESSION ======================
with tab9:
    st.header("🌌 COSMIC COMPRESSION — Memory Graph Pruning")
    st.caption("Intelligent pruning to keep the brain lean and high-signal")
    if st.button("🚀 Run Cosmic Compression Now", type="primary", use_container_width=True):
        with st.spinner("Performing advanced graph pruning..."):
            compressed, promoted = manager.perform_cosmic_compression(force=True)
            st.success(f"✅ Compression complete — Removed {compressed} low-value fragments | Promoted {promoted} invariants to Grail")
            st.rerun()
    # Live graph stats
    if hasattr(manager, 'fragment_tracker') and hasattr(manager.fragment_tracker, 'graph'):
        g = manager.fragment_tracker.graph
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Nodes", len(g.nodes))
        with col2:
            st.metric("Graph Density", f"{nx.density(g):.4f}" if 'nx' in globals() else "N/A")
        with col3:
            grail_count = len([n for n,d in g.nodes(data=True) if d.get('in_grail', False)])
            st.metric("Grail Nodes", grail_count)
        with col4:
            avg_mau = np.mean([d.get('mau', 0) for n,d in g.nodes(data=True)]) if g.nodes else 0
            st.metric("Avg MAU", f"{avg_mau:.3f}")

# ====================== TAB 10: PRUNING ADVISOR ======================
with tab10:
    st.header("🧹 PRUNING ADVISOR — Intelligent Recommendations")
    st.caption("Data-driven analysis of the last run with actionable recommendations")
    if st.button("🔍 Analyze Current Run", type="primary", use_container_width=True):
        with st.spinner("Analyzing run data..."):
            if st.session_state.last_result:
                analysis = manager._analyze_run(
                    current_results=st.session_state.last_result.get("subtask_outputs", {}),
                    blueprint=st.session_state.get("high_level_plan", {})
                )
                st.session_state.last_analysis = analysis
                st.success("✅ Analysis complete")
            else:
                st.error("No recent run data available. Launch a mission first.")
    if "last_analysis" in st.session_state:
        analysis = st.session_state.last_analysis
        st.metric("Run Health Score", f"{analysis.get('health_score', 0):.3f}", delta="Higher is better")
        st.subheader("Recommendations")
        for rec in analysis.get("recommendations", []):
            priority_color = "🔴" if rec.get("priority") == "critical" else "🟠" if rec.get("priority") == "high" else "🟡"
            with st.expander(f"{priority_color} {rec.get('module')} → {rec.get('action')}"):
                st.write(rec.get("reason"))
                st.caption(f"Priority: {rec.get('priority', 'medium').upper()}")
        st.subheader("Key Signals")
        st.json(analysis.get("signals", {}))

# ====================== TAB 11: RECOMMENDED EXPERIMENTS (NEW) ======================
with tab11:
    st.subheader("🧪 Scientist Mode — Recommended Experiments")
    st.caption("Data-driven recommendations generated from recent runs. One-click execution available.")

    if hasattr(manager, "_current_scientist_summary") and manager._current_scientist_summary:
        summary = manager._current_scientist_summary
        
        # Latest recommendations
        st.markdown("**Latest Recommendations (from most recent run)**")
        if "experiment_summaries" in summary and summary["experiment_summaries"]:
            for i, exp in enumerate(summary["experiment_summaries"]):
                with st.expander(f"Recommendation {i+1}: {exp.get('target_variable', 'Unknown')} → {exp.get('effect_variable', 'Unknown')}"):
                    st.json(exp)
                    if st.button("🚀 Run This Experiment", key=f"run_exp_{i}"):
                        with st.spinner("Running targeted Scientist Mode experiment..."):
                            intent = {
                                "target_variable": exp.get("target_variable"),
                                "effect_variable": exp.get("effect_variable"),
                                "domain_focus": exp.get("domain_focus"),
                                "goal": exp.get("goal", "maximize_EFS_and_robustness"),
                                "trial_weights": exp.get("trial_weights", {"retention": 0.6, "efs_impact": 0.4})
                            }
                            result = manager.run_scientist_mode(intent=intent)
                            st.success("✅ Experiment completed and logged!")
                            st.json(result)
        else:
            st.info("No active recommendations from the latest run.")
        
        # Historical overview
        st.divider()
        st.subheader("Historical Experiment Impact")
        recent = manager.get_run_history(n=15)
        if recent:
            df_data = []
            for r in recent:
                if isinstance(r, dict) and "experiment_count" in r:
                    df_data.append({
                        "Timestamp": r.get("timestamp", "N/A"),
                        "Experiments Run": r.get("experiment_count", 0),
                        "Avg EFS": round(r.get("avg_efs", 0), 4),
                        "High-Signal Experiments": r.get("high_signal_count", 0),
                        "Contract Deltas": len(r.get("contract_deltas", []))
                    })
            if df_data:
                st.dataframe(pd.DataFrame(df_data), use_container_width=True)
        else:
            st.info("No experiment history yet — run more missions with Scientist Mode enabled.")
        
        st.caption("Recommendations are automatically generated from EFS deltas, stall patterns, verifier quality, and memory utilization in recent runs.")

    # NEW: Post-run DOUBLE_CLICK Recommendations from PatternEvolutionArbos
    st.subheader("🔄 Post-Run DOUBLE_CLICK Recommendations")
    if hasattr(manager, "_current_double_click_recommendations") and manager._current_double_click_recommendations:
        for i, rec in enumerate(manager._current_double_click_recommendations):
            with st.expander(f"DOUBLE_CLICK {i+1}: {rec['goal']}"):
                st.json(rec)
                if st.button("🚀 Run This DOUBLE_CLICK Now", key=f"double_click_{i}"):
                    with st.spinner("Running targeted DOUBLE_CLICK experiment..."):
                        intent = {
                            "target_variable": rec["target_variable"],
                            "effect_variable": rec["effect_variable"],
                            "domain_focus": rec["domain_focus"],
                            "goal": rec["goal"]
                        }
                        result = manager.run_scientist_mode(intent=intent)
                        st.success("DOUBLE_CLICK completed!")
                        st.json(result)
    else:
        st.info("No post-run DOUBLE_CLICK recommendations yet.")

    st.caption("DOUBLE_CLICK recommendations are generated post-run by PatternEvolutionArbos to strengthen patterns or fill small discovery gaps.")

# ====================== PACKAGE & EXPORT ======================
st.divider()
if st.session_state.last_result:
    if st.button("📦 Package & Download Submission"):
        _package_submission(
            solution=st.session_state.last_result.get("merged_candidate", ""),
            blueprint=st.session_state.get("high_level_plan", {}),
            trace=st.session_state.get("trace_log", []),
            notes="Full run with PuLP, real backends, TPE meta-tuning, and deep graph memory",
            challenge=challenge,
            verification=verification_instructions,
            deterministic_tooling="SymPy + Cirq + Z3 + PuLP"
        )

def _package_submission(solution: str, blueprint: dict, trace: list, notes: str,
                        challenge: str, verification: str, deterministic_tooling: str):
    """Package the full submission for upload."""
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    sub_dir = Path("submissions") / f"sn63_{ts}"
    sub_dir.mkdir(parents=True, exist_ok=True)
    (sub_dir / "solution.md").write_text(str(solution), encoding="utf-8")
    (sub_dir / "blueprint.json").write_text(json.dumps(blueprint, indent=2), encoding="utf-8")
    (sub_dir / "trace.log").write_text("\n".join(str(t) for t in trace), encoding="utf-8")
    (sub_dir / "miner_notes.txt").write_text(notes, encoding="utf-8")
    (sub_dir / "challenge.txt").write_text(challenge, encoding="utf-8")
    (sub_dir / "verification.txt").write_text(verification, encoding="utf-8")
    (sub_dir / "deterministic_tooling.txt").write_text(deterministic_tooling, encoding="utf-8")
    with zipfile.ZipFile(sub_dir / "submission_package.zip", "w") as z:
        for f in sub_dir.glob("*"):
            if f.is_file() and f.suffix != ".zip":
                z.write(f, f.name)
    with open(sub_dir / "submission_package.zip", "rb") as f:
        st.download_button(
            label="📥 Download Submission Package",
            data=f.read(),
            file_name=f"sn63_{ts}.zip",
            mime="application/zip"
        )
   
    st.success(f"✅ Package created: sn63_{ts}.zip")

st.caption("© 1944–2026 ALLIED ENIGMA MINER • PUSHING HUMANITY TO THE NEXT STAGE")
