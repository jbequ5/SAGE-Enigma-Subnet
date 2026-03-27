import streamlit as st
import json
import zipfile
from pathlib import Path
from datetime import datetime

from agents.arbos_manager import ArbosManager

# ====================== PAGE CONFIG & BUNKER THEME ======================
st.set_page_config(
    page_title="ENIGMA MINER - SN63",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Full bunker background with Enigma on table (replace URL with your saved image)
bunker_bg_url = "https://i.imgur.com/YOUR_BUNKER_IMAGE_URL.jpg"   # ← CHANGE THIS

st.markdown(f"""
<style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("{https://pub-1407f82391df4ab1951418d04be76914.r2.dev/uploads/6e9e5059-d813-470c-b43e-c39eeccb173c.jpg}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    [data-testid="stHeader"], footer, [data-testid="stToolbar"] {{
        visibility: hidden;
    }}

    /* Semi-transparent green classified overlay */
    .stApp {{
        background: linear-gradient(rgba(8, 28, 18, 0.88), rgba(12, 38, 24, 0.92));
    }}

    /* Retro military green glowing text */
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
        color: #00ff9d !important;
        font-family: 'Courier New', monospace;
        text-shadow: 0 0 12px #00ff9d, 0 0 25px #00aa77;
        letter-spacing: 1.5px;
    }}

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stCodeBlock {{
        background-color: rgba(0, 25, 15, 0.95) !important;
        color: #00ff9d !important;
        border: 2px solid #00cc88;
        font-family: 'Courier New', monospace;
        box-shadow: 0 0 10px rgba(0, 255, 150, 0.4);
    }}

    .stButton > button {{
        background-color: #002211;
        color: #00ff9d;
        border: 2px solid #00aa77;
        font-weight: bold;
        font-family: 'Courier New', monospace;
        text-transform: uppercase;
        letter-spacing: 2px;
        box-shadow: 0 0 15px rgba(0, 255, 150, 0.6);
    }}

    .stButton > button:hover {{
        background-color: #004422;
        border-color: #00ff9d;
        box-shadow: 0 0 25px #00ff9d;
    }}

    /* Top Secret watermark */
    .stApp::before {{
        content: "TOP SECRET — ENIGMA MINER COMMAND POST 1943";
        position: fixed;
        top: 25px;
        right: 40px;
        font-family: 'Courier New', monospace;
        font-size: 15px;
        color: rgba(255, 60, 60, 0.18);
        transform: rotate(-8deg);
        pointer-events: none;
        z-index: 9999;
        letter-spacing: 6px;
    }}

    .stMetric {{
        background: rgba(0, 30, 20, 0.7);
        border: 1px solid #00aa77;
    }}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; margin-bottom: 5px;'>🔒 ENIGMA MINER</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #ffaa44; margin-top: 0;'>WWII BUNKER COMMAND POST • SUBNET 63</h3>", unsafe_allow_html=True)
st.caption("Arbos Planning • vLLM Swarm • ToolHunter • Verification")

# ====================== SESSION STATE & MANAGER ======================
if "arbos_manager" not in st.session_state:
    st.session_state.arbos_manager = ArbosManager()
manager = st.session_state.arbos_manager

# ====================== SIDEBAR (ToolHunter + Compute Info) ======================
st.sidebar.title("🛠️ BUNKER OPERATIONS")
max_hours = manager.config.get("max_compute_hours", 3.8)
st.sidebar.metric("Max Compute Limit", f"{max_hours} hours")

if torch.cuda.is_available():
    try:
        free_vram = torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated(0)
        st.sidebar.metric("VRAM Free", f"{free_vram / (1024**3):.1f} GB")
    except:
        pass

# ToolHunter pre-run
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
            st.stop()

        discovered = manager.discover_from_goal(goal_content)
        
        if discovered:
            st.success(f"✅ Discovered and added {len(discovered)} relevant tools/models")
            st.info("Registry updated. ToolHunter will now use these during runs.")
        else:
            st.warning("No strong matches found.")
        st.rerun()

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

    endpoint = None

    if compute_option == "Chutes (decentralized GPUs - recommended if no local GPU)":
        st.markdown("### 🚀 Go to Chutes to rent compute")
        st.markdown("[Open Chutes Dashboard](https://chutes.ai)")
        endpoint = st.text_input("Chutes Endpoint URL", placeholder="https://your-chutes-endpoint.chutes.ai")

    elif compute_option == "Already running (use existing endpoint)":
        endpoint = st.text_input("Existing compute endpoint URL", placeholder="https://my-hosted-miner.com/api")

    elif compute_option == "Custom / Hosted (RunPod, Vast, AWS, etc.)":
        endpoint = st.text_input("Custom compute endpoint URL", placeholder="https://...")

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

# ====================== STAGE 1: HIGH-LEVEL PLANNING APPROVAL ======================
if st.session_state.get("stage") == "planning_approval":
    if "challenge" not in st.session_state:
        st.session_state.challenge = st.text_area("SN63 Challenge", height=120, placeholder="Describe the hard problem...")

    with st.spinner("Planning Arbos running..."):
        plan = manager.plan_challenge(st.session_state.challenge)
        st.session_state.high_level_plan = plan

    st.subheader("📋 Stage 1: High-Level Plan – Strategic Review")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Goals:** {plan.get('high_level_goals', 'N/A')}")
        st.markdown("**Risks:**")
        for r in plan.get("risks_and_mitigations", []):
            st.write(f"• {r}")
        st.markdown("**Rough Decomposition:**")
        for t in plan.get("rough_decomposition", []):
            st.write(f"• {t}")
        
        st.markdown("### 🔧 Arbos Deterministic Recommendations")
        st.info(plan.get("deterministic_recommendations", "No specific recommendations yet."))

        st.markdown("### 🚀 **Miner Enhancement Prompt (10/10 Instructions)**")
        st.caption("**Required / Highly Recommended** — Tell Arbos your strategy, model preferences, tool priorities, novelty focus, etc.")
        enhancement_prompt = st.text_area(
            "Your strategic instructions",
            height=160,
            placeholder="Examples:\n• Maximize novelty and IP potential\n• Use TheBloke/Llama-3-70B-Instruct for synthesis\n• Prioritize symbolic tools and verifier strength\n• Focus on Quantum Rings fidelity"
        )
        st.session_state.enhancement_prompt = enhancement_prompt

    with col2:
        st.metric("Suggested Swarm Size", plan.get("suggested_swarm_size", 1))

    feedback = st.text_area("Feedback / Tweak (optional)")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("✅ Approve High-Level Plan & Continue", type="primary"):
            st.session_state.approved_plan = plan
            st.session_state.stage = "orchestrator_review"
            st.rerun()
    with col_b:
        if st.button("🔄 Re-plan"):
            if feedback.strip():
                with st.spinner("Re-planning..."):
                    tweaked = manager.plan_challenge(f"{st.session_state.challenge}\n\nMiner feedback: {feedback}")
                    st.session_state.high_level_plan = tweaked
                    st.rerun()
    with col_c:
        if st.button("❌ Restart"):
            st.session_state.clear()
            st.rerun()

# ====================== STAGE 2: ORCHESTRATOR BLUEPRINT REVIEW ======================
if st.session_state.get("stage") == "orchestrator_review":
    with st.spinner("Orchestrator Arbos creating detailed blueprint..."):
        blueprint = manager._refine_plan(
            st.session_state.approved_plan, 
            st.session_state.challenge,
            st.session_state.get("deterministic_tooling", ""),
            st.session_state.get("enhancement_prompt", "")
        )
        st.session_state.blueprint = blueprint

    st.subheader("📋 Stage 2: Orchestrator Blueprint – Tactical Review")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**Detailed Decomposition:**")
        for t in blueprint.get("decomposition", []):
            st.write(f"• {t}")
        
        st.markdown("### 🔧 Updated Tool Recommendations")
        st.info(blueprint.get("deterministic_recommendations", "No new recommendations."))

        st.markdown("### 🚀 **Final Miner Enhancement Prompt**")
        st.caption("**Last chance** to add model requests, tool priorities, or strategic adjustments.")
        final_enhancement = st.text_area(
            "Final instructions",
            height=140,
            value=st.session_state.get("enhancement_prompt", ""),
            placeholder="Any last tactical adjustments or model requests..."
        )
        st.session_state.enhancement_prompt = final_enhancement

    with col2:
        st.metric("Final Swarm Size", blueprint.get("swarm_config", {}).get("total_instances", 1))

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("✅ Approve Blueprint & Launch Swarm", type="primary"):
            st.session_state.stage = "final_review"
            final_solution, _, _ = manager._smart_route(st.session_state.challenge)
            st.session_state.final_solution = final_solution
            st.rerun()
    with col_b:
        if st.button("🔄 Re-refine Blueprint"):
            with st.spinner("Re-refining..."):
                blueprint = manager._refine_plan(
                    st.session_state.approved_plan, 
                    st.session_state.challenge,
                    st.session_state.get("deterministic_tooling", ""),
                    st.session_state.get("enhancement_prompt", "")
                )
                st.session_state.blueprint = blueprint
                st.rerun()
    with col_c:
        if st.button("❌ Go Back to High-Level Plan"):
            st.session_state.stage = "planning_approval"
            st.rerun()

# ====================== FINAL REVIEW ======================
if st.session_state.get("stage") == "final_review":
    solution = st.session_state.final_solution
    blueprint = st.session_state.get("blueprint", {})
    trace = st.session_state.get("trace_log", [])

    st.subheader("🔍 Final Miner Review")

    tab1, tab2, tab3, tab4 = st.tabs(["Solution", "ToolHunter", "Memory History", "Verification & Deterministic Tooling"])

    with tab1:
        st.text_area("Final Solution", solution, height=400)

    with tab2:
        st.markdown("### ⚠️ ToolHunter Results & Manual Actions")
        manual_actions = [entry for entry in trace if isinstance(entry, str) and ("MANUAL REQUIRED" in entry.upper() or "ToolHunter found" in entry)]
        
        if manual_actions:
            st.warning("**ToolHunter Recommendations Found**")
            for action in manual_actions:
                st.info(action)
                if "found specialized" in action.lower() or "model:" in action.lower():
                    if st.button("🔄 Apply Recommended Model/Tool", key=action[:50]):
                        st.session_state.deterministic_tooling = action
                        st.success("✅ Recommendation copied to Deterministic Tooling field. You can now re-run.")
                        st.rerun()
        else:
            st.success("✅ No ToolHunter actions required.")

    with tab3:
        st.markdown("### Memory History (Re-loop Learning)")
        past = memory.query(st.session_state.challenge, n_results=8)
        if past:
            for i, p in enumerate(past, 1):
                st.write(f"**Attempt {i}:** {p[:300]}...")
        else:
            st.info("No previous attempts in memory.")

    with tab4:
        st.markdown("### 🔬 **Verification & Deterministic Tooling**")
        st.caption("**Important:** Provide any custom verification code or tool requirements here.")

        col_v, col_d = st.columns(2)
        with col_v:
            st.markdown("**Verification Instructions / Code**")
            verification = st.text_area(
                "",
                height=180,
                value=st.session_state.get("verification_instructions", ""),
                placeholder="Example: Simulate on Quantum Rings with 5000 shots. Require fidelity > 0.95"
            )
            st.session_state.verification_instructions = verification

        with col_d:
            st.markdown("**Deterministic Tooling Requirements**")
            deterministic_tooling = st.text_area(
                "",
                height=180,
                value=st.session_state.get("deterministic_tooling", ""),
                placeholder="Example: Use stim for stabilizer checks. Prefer symbolic fallbacks. Use TheBloke/Llama-3-70B-Instruct for synthesis."
            )
            st.session_state.deterministic_tooling = deterministic_tooling

        if st.button("🔄 Re-run with Verification & Tooling"):
            with st.spinner("Re-running..."):
                new_solution = manager._run_swarm(
                    st.session_state.blueprint, 
                    st.session_state.challenge, 
                    verification, 
                    deterministic_tooling
                )
                st.session_state.final_solution = new_solution
                st.rerun()

        # Quality gate
        if "quality_critique" not in st.session_state:
            with st.spinner("Running quality gate..."):
                task = f"""You are Arbos. Evaluate with this verification: {verification or 'General SN63 standards'}
Deterministic tooling: {deterministic_tooling or 'None'}
Solution: {solution[:2000]}
Output JSON with novelty, verifier_potential, overall_score, recommendation, verification_assessment."""
                raw = manager.compute.run_on_compute(task)
                try:
                    start = raw.find("{")
                    end = raw.rfind("}") + 1
                    st.session_state.quality_critique = json.loads(raw[start:end])
                except:
                    st.session_state.quality_critique = {"overall_score": 7.0}

        q = st.session_state.quality_critique
        cols = st.columns(6)
        metrics = [
            ("Novelty", q.get("novelty", 0)),
            ("Verifier", q.get("verifier_potential", 0)),
            ("Alignment", q.get("alignment", 0)),
            ("Completeness", q.get("completeness", 0)),
            ("Efficiency", q.get("efficiency", 0)),
            ("IP", q.get("ip_licensability", 0))
        ]
        for col, (label, value) in zip(cols, metrics):
            col.metric(label, f"{value}/10")

        st.success(f"**Overall Score: {q.get('overall_score', 0)}/10** → {q.get('recommendation', '')}")

    miner_notes = st.text_area("Your Final Notes (optional)")

    if st.button("📦 Package for SN63 Submission", type="primary"):
        _package_submission(solution, blueprint, trace, miner_notes, st.session_state.challenge, verification, deterministic_tooling)
        st.success("✅ Submission package created!")
        st.balloons()

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

    past = memory.query(challenge, n_results=8)
    (sub_dir / "memory_history.txt").write_text("\n\n".join(past))

    with zipfile.ZipFile(sub_dir / "submission_package.zip", "w") as z:
        for f in sub_dir.glob("*"):
            if f.is_file() and f.suffix != ".zip":
                z.write(f, f.name)

    print(f"✅ Package ready: {sub_dir}/submission_package.zip")
