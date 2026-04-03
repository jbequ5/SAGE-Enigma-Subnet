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

st.markdown("<h1 style='text-align: center;'>🔒 ALLIED ENIGMA MINER v4.8</h1>", unsafe_allow_html=True)
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

# ====================== IMPROVED BRAIN-AWARE STRATEGY EDITOR ======================
st.subheader("🧠 STRATEGY LAYERS — Brain Suite")
st.caption("killer_base.md is now a thin shim. Edit high-leverage components selectively below.")

# Thin shim overview (read-only)
st.markdown("**Canonical Entry Point (Thin Shim)**")
with st.expander("View killer_base.md shim", expanded=False):
    try:
        with open("goals/killer_base.md", "r", encoding="utf-8") as f:
            shim_content = f.read()
        st.text_area("Shim Content (read-only — do not edit here)", value=shim_content, height=180, disabled=True)
    except Exception as e:
        st.error(f"Could not load shim: {e}")

# Structured editing by component
col_shim, col_select = st.columns([1, 2])
with col_select:
    edit_mode = st.radio(
        "Edit Mode",
        options=["Individual Components", "Full Concatenated View", "Quick Toggles Only"],
        horizontal=True,
        key="strategy_edit_mode"
    )

if edit_mode == "Individual Components":
    st.markdown("**Select Component to Edit**")
    component_options = {
        "Core Strategy": "core_strategy",
        "Shared Core Principles": "principles/shared_core",
        "Compression Prompt": "principles/compression",
        "Wiki Strategy": "principles/wiki_strategy",
        "Bio Strategy (mycelial + quantum)": "principles/bio_strategy",
        "English Evolution Modules": "principles/english_evolution",
        "Centralized Toggles": "toggles",
        "Live Metrics": "metrics"
    }
    
    selected = st.selectbox("Choose layer", options=list(component_options.keys()), key="component_select")
    component_path = component_options[selected]
    
    try:
        content = load_brain_component(component_path)
        edited = st.text_area(f"Editing: {selected}", value=content, height=380, key=f"edit_{component_path.replace('/', '_')}")
        
        col_save1, col_save2 = st.columns(2)
        with col_save1:
            if st.button(f"💾 Save {selected}", type="primary"):
                full_path = f"goals/brain/{component_path}.md"
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(edited)
                st.success(f"✅ Saved {selected}")
                st.rerun()
        with col_save2:
            if st.button("🔄 Save & Compress Full Suite", type="secondary"):
                # Trigger MCTS-style compression across the entire brain
                raw = f"Manual edit to {selected} — triggering suite-wide compression"
                compressed = manager.compress_intelligence_delta(raw)
                st.success("✅ Full brain suite compressed")
                st.json(compressed[:800] + "..." if len(str(compressed)) > 800 else compressed)
                st.rerun()
    except Exception as e:
        st.error(f"Could not load or save component '{selected}': {e}")

elif edit_mode == "Full Concatenated View":
    # Legacy full view (concat shim + key brain pieces)
    st.caption("Legacy full view — use sparingly (for backward compatibility)")
    try:
        full_concat = load_brain_component("index") + "\n\n" + load_brain_component("core_strategy")
        edited_full = st.text_area("Full Concatenated Strategy", value=full_concat, height=420, key="full_concat_edit")
        if st.button("Save Full View (updates shim + core)"):
            with open("goals/killer_base.md", "w", encoding="utf-8") as f:
                f.write(edited_full)
            st.success("✅ Full view saved to killer_base.md shim")
            st.rerun()
    except Exception as e:
        st.error(f"Error building full view: {e}")

else:  # Quick Toggles Only
    st.subheader("Quick Toggles")
    try:
        toggles_content = load_brain_component("toggles")
        edited_toggles = st.text_area("Edit Toggles (brain_depth, aha_adaptation_enabled, symbiosis_synthesis, etc.)", 
                                      value=toggles_content, height=300, key="quick_toggles_edit")
        if st.button("Save Toggles"):
            with open("goals/brain/toggles.md", "w", encoding="utf-8") as f:
                f.write(edited_toggles)
            st.success("✅ Toggles saved — reload manager / rerun to apply")
            st.rerun()
    except Exception as e:
        st.error(f"Error loading toggles: {e}")

# Optional: Show importance / last compressed note
st.caption("**Pro tip**: Changess.")
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
        
# ====================== NEW: BRAIN SUITE DASHBOARD TAB ======================
tab_plan, tab_orch, tab_brain, tab_hunter, tab_final = st.tabs([
    "📋 High-Level Plan", 
    "🚀 Orchestration", 
    "🧠 Brain Suite", 
    "🛰️ ToolHunter Recon", 
    "📦 Final Review & Packaging"
])

with tab_brain:
    st.header("🧠 BRAIN SUITE — Self-Compounding Intelligence Layer")
    st.caption("Mycelial + Karpathy-style wiki + Bio heuristics. Edit live. One-click compress & promote.")

    # Master Index
    st.subheader("Master Index")
    index_content = load_brain_component("index")
    st.markdown(index_content)

    # Principles Accordion
    with st.expander("📜 Principles (Stable — change only on proven lift)", expanded=False):
        for principle in ["shared_core", "compression", "wiki_strategy", "bio_strategy", "english_evolution"]:
            with st.expander(f"→ {principle.replace('_', ' ').title()}", expanded=False):
                content = load_brain_component(f"principles/{principle}")
                edited = st.text_area(f"Edit {principle}", value=content, height=300, key=f"edit_{principle}")
                if st.button(f"Save & Compress {principle}", key=f"save_{principle}"):
                    # Save back to correct file
                    full_path = f"goals/brain/principles/{principle}.md"
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(edited)
                    st.success(f"✅ Saved {principle}")
                    # Trigger compression across suite
                    manager.compress_intelligence_delta("Brain suite updated — run MCTS compression")
                    st.rerun()

    # Toggles
    with st.expander("🔧 Centralized Toggles", expanded=True):
        toggles_content = load_brain_component("toggles")
        edited_toggles = st.text_area("Toggles (brain_depth, aha_adaptation_enabled, etc.)", value=toggles_content, height=250)
        if st.button("Save Toggles"):
            with open("goals/brain/toggles.md", "w", encoding="utf-8") as f:
                f.write(edited_toggles)
            st.success("✅ Toggles saved — reload manager to apply")
            st.rerun()

    # Metrics
    with st.expander("📊 Live Metrics", expanded=False):
        metrics_content = load_brain_component("metrics")
        st.markdown(metrics_content)
        if st.button("Refresh Metrics"):
            st.rerun()

    # Grail Patterns
    with st.expander("🏆 Grail Patterns (auto-promoted)", expanded=False):
        grail_dir = Path("goals/brain/grail_patterns")
        if grail_dir.exists():
            for f in grail_dir.glob("*.json"):
                st.json(f.read_text())
        else:
            st.info("No grail patterns yet — will auto-populate on high-signal runs")

    # One-click full suite compression
    if st.button("🔄 Compress Entire Brain Suite + Promote to Grail", type="primary"):
        with st.spinner("Running MCTS-guided compression across all principles..."):
            # Trigger existing compression on brain components
            raw = "Brain suite update — high-signal deltas from recent aha/wiki runs"
            compressed = manager.compress_intelligence_delta(raw)
            st.success("✅ Brain suite compressed")
            st.json(compressed)
            st.rerun()

# ====================== SIDEBAR - MISSION CONTROLS ======================
with st.sidebar:
    st.header("⚙️ MISSION CONTROLS")
    st.markdown("---")

    # Core Toggles
    manager.quasar_enabled = st.checkbox("Quasar Long-Context Attention", value=False)
    manager.enable_grail = st.checkbox("Grail Reinforcement (on high scores)", value=True)
    
    st.markdown("---")

    # Compute Source
    st.subheader("🔌 Compute")
    compute_option = st.radio(
        "Compute Source",
        options=["Local GPU (Ollama)", "Chutes (Remote)", "Custom Endpoint"],
        index=0,
        key="compute_sidebar"
    )
    if compute_option == "Custom Endpoint":
        custom_endpoint = st.text_input("Custom Endpoint URL", placeholder="http://...", key="custom_endpoint")
        if custom_endpoint:
            manager.set_compute_source("custom", custom_endpoint)
    else:
        source_map = {"Local GPU (Ollama)": "local_gpu", "Chutes (Remote)": "chutes"}
        manager.set_compute_source(source_map[compute_option])

    st.markdown("---")

    # Challenge State Management
    st.subheader("💾 Challenge State")
    col_save, col_load = st.columns(2)
    with col_save:
        if st.button("Save Current State", key="save_state_btn"):
            challenge_id = st.text_input("Challenge ID", value="current", key="save_id")
            if challenge_id:
                manager.save_challenge_state(challenge_id)
                st.success("State saved")
    with col_load:
        if st.button("Load State", key="load_state_btn"):
            challenge_id = st.text_input("Challenge ID", value="current", key="load_id")
            if challenge_id and manager.load_challenge_state(challenge_id):
                st.success("State loaded")
            else:
                st.error("No saved state found")

    st.markdown("---")

    # Deep Replan
    if st.button("🧠 Generate New Avenue Plan (Deep Replan)", type="secondary", key="deep_replan_btn"):
        if "challenge" in st.session_state and st.session_state.challenge:
            plan = manager._generate_new_avenue_plan(
                challenge=st.session_state.challenge,
                recent_feedback="User requested deep replan"
            )
            st.json(plan)
        else:
            st.warning("Run a challenge first before deep replan")

    st.markdown("---")

    # VectorDB Stats
    if st.button("📊 Show VectorDB Stats", key="vector_stats_btn"):
        stats = manager.get_vector_db_stats()
        st.json(stats)

    st.markdown("---")
 # ====================== SCIENTIST MODE ======================
    st.markdown("### 🧪 SCIENTIST MODE")
    st.caption("Generate synthetic hard challenges and measure system progress")
    
    if st.button("🚀 Run Scientist Mode Now", type="primary"):
        with st.spinner("Running Scientist Mode (5 synthetic challenges)..."):
            manager.run_scientist_mode(num_synthetic=5)
        st.success("✅ Scientist Mode completed! Check logs below.")
    
    # Show last scientist run
    if Path("scientist_log.json").exists():
        try:
            log = json.loads(Path("scientist_log.json").read_text())
            if log:
                last = log[-1]
                st.info(f"**Last Scientist Run**: {last['timestamp'][:16]}\n"
                        f"{len(last['synthetic_runs'])} challenges • Avg Score: "
                        f"{sum(r['score'] for r in last['synthetic_runs'])/len(last['synthetic_runs']):.3f}")
        except:
            pass

    st.divider()
    # ====================== EXPERT INPUT MODE ======================
    st.markdown("### 🧪 EXPERT INPUT MODE")
    st.caption("For physicists, mathematicians, and domain experts")

    with st.expander("📋 When to use which option", expanded=False):
        st.markdown("""
        **Expert Plugin System** (.md files in `experts/` folder)  
        → Best for **permanent knowledge injection** (e.g. quantum rules, crypto invariants).  
        Auto-injected into every prompt.

        **Streamlit Expert Input** (below)  
        → Best for **creating new tools / invariants / strategy changes**.  
        Gets turned into real runnable code after safety review.
        """)

    tab_tool, tab_invariant, tab_strategy = st.tabs(["New Tool", "Symbolic Invariant", "Strategy Change"])

    with tab_tool:
        tool_name = st.text_input("Tool Name")
        tool_desc = st.text_area("Description / What it should do", height=100)
        if st.button("Submit New Tool Proposal"):
            if tool_name and tool_desc:
                proposal = {
                    "name": tool_name,
                    "description": tool_desc,
                    "code": "AUTO_GENERATE",
                    "type": "tool"
                }
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

    st.divider()
    st.caption("© 1944–2026 ALLIED ENIGMA MINER")

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

# ====================== NEW v4.8 FEATURES ======================
st.subheader("🧠 v4.8 Intelligence Layer")
col_a, col_b = st.columns(2)

with col_a:
    if st.button("💾 Save Current Challenge State"):
        challenge_id = st.text_input("Challenge ID", value="current", key="save_id_main")
        if challenge_id:
            manager.save_challenge_state(challenge_id)
            st.success(f"State saved: {challenge_id}")

with col_b:
    if st.button("📂 Load Challenge State"):
        challenge_id = st.text_input("Challenge ID", value="current", key="load_id_main")
        if challenge_id:
            if manager.load_challenge_state(challenge_id):
                st.success(f"Loaded: {challenge_id}")
            else:
                st.error("No saved state found")

if st.button("🧠 Generate New Avenue Plan (Deep Replan)"):
    plan = manager._generate_new_avenue_plan(
        challenge=challenge or "Current Challenge",
        recent_feedback="User requested deep replan"
    )
    st.json(plan)

# Grail Status
reinforcement_avg = sum(manager.grail_reinforcement.values()) / max(len(manager.grail_reinforcement), 1) if hasattr(manager, 'grail_reinforcement') and manager.grail_reinforcement else 0.0
st.metric("Grail Reinforcement Signal", f"{reinforcement_avg:.3f}")

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
        with st.spinner("Planning Arbos running..."):
            plan = manager.plan_challenge(
                goal_md=edited_goal, 
                challenge=challenge, 
                enhancement_prompt="",   
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
            ""  
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

    tab_sol, tab_tool, tab_grail, tab_self, tab_trace, tab_criteria = st.tabs([
        "Solution + Oracle", 
        "ToolHunter Results", 
        "Grail & Messages", 
        "Self-Improvement", 
        "Trace Log", 
        "Validation Criteria"
    ])

    with tab_sol:
        st.text_area("Final Synthesized Solution", value=str(solution), height=400)
        score = getattr(manager.validator, 'last_score', 0.0)
        st.success(f"ValidationOracle Score: **{score:.3f}**")

    with tab_tool:
        if st.session_state.toolhunter_results:
            st.json(st.session_state.toolhunter_results)
        else:
            st.info("No ToolHunter results yet.")

    with tab_grail:
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

    with tab_self:
        if st.button("Run Self-Critique Now"):
            critique = manager.self_critique(st.session_state.get("challenge", "unknown"))
            st.json(critique)
        
        if st.button("Force Adaptation Arbos (re_adapt)"):
            current_sol = str(solution)[:2000] if solution else "No solution yet"
            manager.re_adapt({"solution": current_sol}, "miner_forced_adaptation")
            st.success("✅ Adaptation Arbos executed.")

    with tab_trace:
        st.subheader("Live Trace Log")
        for entry in trace[-20:]:
            st.caption(str(entry))

    with tab_criteria:
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
