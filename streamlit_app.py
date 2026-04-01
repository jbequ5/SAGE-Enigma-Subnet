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

# Import after page config
from agents.arbos_manager import ArbosManager
from agents.tools.compute import compute_router

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

st.markdown("<h1 style='text-align: center;'>🔒 ALLIED ENIGMA MINER v4.5</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #aaffaa;'>US ARMY SIGNALS INTELLIGENCE • BUNKER COMMAND POST 1944 • SN63 Quantum Innovate</h3>", unsafe_allow_html=True)
st.caption("Challenge-Agnostic • Quasar Long-Context • Dynamic Swarm • Verifier-First • Mature Message Bus + Grail Compounding")

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

# ====================== GOAL.MD EDITOR ======================
st.subheader("🎯 GOAL.md / Strategy File")
st.caption("Single source of truth — edit toggles and base strategy here.")

goal_path = Path("goals/killer_base.md")
goal_path.parent.mkdir(parents=True, exist_ok=True)

if not goal_path.exists():
    goal_path.write_text("""# Enigma Machine Miner - Base Strategy

mode: optimal
compute_source: local
max_compute_hours: 3.8
resource_aware: true
guardrails: true
toolhunter_escalation: true
quasar_attention: true
dynamic_swarm: true
verifier_first: true
light_compression: true
grail_on_winning_runs: false
self_critique_enabled: true
""", encoding="utf-8")

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

# ====================== TOOLHUNTER SWARM (NEW - RUN ANYTIME) ======================
st.subheader("🛠️ ToolHunter Swarm • Run at Any Time")
st.caption("Describe a gap and get immediate tool/library/model recommendations + install commands")

hunter_gap = st.text_area(
    "Current Gap or Subtask",
    height=100,
    placeholder="e.g., Need better quantum circuit simulator, missing symbolic invariant checker, or faster matrix operations for SN63...",
    key="hunter_gap_input"
)

col_th1, col_th2 = st.columns([2, 1])
with col_th1:
    if st.button("🚀 Launch ToolHunter Swarm", type="secondary", use_container_width=True):
        if not hunter_gap.strip():
            st.error("Please describe a gap or subtask.")
        else:
            with st.spinner("Scanning ToolHunter + ReadyAI + Agent-Reach across knowledge bases..."):
                # Use the new dedicated public method
                hunt_result = manager.run_toolhunter_swarm(hunter_gap, max_proposals=6)
                st.session_state.toolhunter_results = hunt_result
                
                st.success("✅ ToolHunter Swarm completed!")
                st.subheader("🧪 ToolHunter Recommendations")

                # Nice formatted display
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
                    
                    st.caption(f"Confidence: {hunt_result.get('confidence', 0.7):.2f} | Loop: {hunt_result.get('loop', 0)}")
                else:
                    st.error(hunt_result.get("message", "Unknown error"))

                # Miner approval button
                if hunt_result.get("status") == "success" and hunt_result.get("proposals"):
                    if st.button("✅ Add Top Recommendations to GOAL.md as Grail Pattern", type="primary"):
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                        content = "\n".join(hunt_result["proposals"]) + "\n\nInstall commands:\n" + "\n".join(hunt_result["install_commands"])
                        
                        with open(goal_path, "a", encoding="utf-8") as f:
                            f.write(f"\n\n## TOOLHUNTER_MINER_APPROVED_{timestamp}\n{content}\n")
                        
                        manager.save_to_memdir(f"toolhunter_{timestamp}", {
                            "content": content,
                            "gap": hunter_gap,
                            "proposals": hunt_result["proposals"]
                        })
                        
                        st.success("✅ Added to GOAL.md and Grail! Will now compound into future runs via message bus + re_adapt.")
                        st.rerun()

with col_th2:
    st.info("Pro tip: Run this anytime — even mid-challenge — to discover new deterministic tools. Results are automatically logged to the mature message bus and Grail for compounding.")

# ====================== QUICK MINER PROMPT ======================
st.subheader("🚀 QUICK MINER PROMPT")
challenge = st.text_area("SN63 Challenge Description (Quantum Innovate task)", height=150, key="challenge_input")
verification = st.text_area("Verification Instructions (optional)", height=100, key="verification_input")

default_enhancement = ""
if st.session_state.get("high_level_plan") and isinstance(st.session_state.high_level_plan, dict):
    default_enhancement = st.session_state.high_level_plan.get("generated_post_planning_enhancement", "")

enhancement = st.text_area(
    "Enhancement Prompt (Post-Planning — Auto-generated & editable)",
    value=default_enhancement,
    height=150,
    key="enhancement_input"
)

col_a, col_b = st.columns([3, 1])
with col_a:
    st.caption("Edits here are passed to Orchestrator Arbos and can be saved as Grail patterns.")
with col_b:
    if st.button("💾 Save Edited Enhancement as Grail Pattern", type="secondary"):
        if enhancement and enhancement.strip():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            grail_section = f"\n\n## GRAIL_ENHANCEMENT_{timestamp} (Miner-Edited)\n{enhancement}\n"
            with open(goal_path, "a", encoding="utf-8") as f:
                f.write(grail_section)
            manager.save_to_memdir(f"grail_enhancement_{timestamp}", {
                "content": enhancement,
                "challenge": challenge or "unknown",
                "timestamp": timestamp
            })
            st.success("✅ Saved as Grail pattern.")
            st.rerun()
        else:
            st.warning("Enhancement is empty.")

# ====================== Generate High-Level Plan ======================
if st.button("🔍 Generate High-Level Plan", type="primary"):
    if not challenge.strip():
        st.error("Please enter a challenge description.")
    else:
        with st.spinner("Planning Arbos running on Local GPU..."):
            plan = manager.plan_challenge(
                goal_md=edited_goal, 
                challenge=challenge, 
                enhancement_prompt=enhancement,
                compute_mode=st.session_state.compute_source
            )
            st.session_state.high_level_plan = plan
            st.session_state.challenge = challenge
            st.session_state.verification = verification
            st.session_state.enhancement = enhancement
            st.session_state.stage = "planning_approval"
            st.session_state.trace_log.append({"stage": "high_level_plan", "timestamp": datetime.now().isoformat()})
        st.rerun()

# ====================== STAGE 1: HIGH-LEVEL PLAN ======================
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

# ====================== STAGE 2: POST-ORCHESTRATION ======================
if st.session_state.get("stage") == "post_orchestration_review":
    with st.spinner("Orchestrator Arbos refining blueprint..."):
        blueprint = manager._refine_plan(
            st.session_state.high_level_plan,
            st.session_state.challenge,
            st.session_state.get("deterministic_tooling", ""),
            st.session_state.get("enhancement", "")
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
            verification_instructions = st.session_state.get("verification", "")
            final_solution = manager.execute_full_cycle(
                blueprint, 
                st.session_state.challenge, 
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
            st.markdown(st.session_state.toolhunter_results)
        else:
            st.info("No ToolHunter results yet. Run the ToolHunter Swarm above.")

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
            st.success("✅ Adaptation Arbos executed. Check Grail & Messages tab.")

    with tab5:
        st.subheader("Live Trace Log")
        for entry in trace[-20:]:  # last 20 entries
            st.caption(str(entry))

    with tab6:
        st.json(validation_criteria)
        st.caption("These criteria were used by each Sub-Arbos worker during the swarm.")

    miner_notes = st.text_area("Your Final Notes (optional)")

    if st.button("📦 Package for SN63 Submission", type="primary"):
        _package_submission(
            solution, blueprint, trace, miner_notes, 
            st.session_state.get("challenge", ""), 
            st.session_state.get("verification", ""), 
            st.session_state.get("deterministic_tooling", "")
        )
        st.success("✅ Submission package created!")
        st.balloons()

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
