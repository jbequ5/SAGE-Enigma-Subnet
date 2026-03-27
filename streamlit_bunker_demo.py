import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="ALLIED ENIGMA MINER",
    page_icon="🔒",
    layout="wide"
)

# Your image
bunker_bg_url = "https://pub-1407f82391df4ab1951418d04be76914.r2.dev/uploads/6700b7a0-d46e-4054-9f1c-3ed01c65c15b.jpg"

st.markdown(f"""
<style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("{bunker_bg_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* STRONGER dark green overlay for much better readability */
    .stApp {{
        background: linear-gradient(rgba(8, 20, 15, 0.94), rgba(5, 25, 18, 0.96));
    }}

    h1, h2, h3 {{
        color: #00ff9d !important;
        font-family: 'Courier New', monospace;
        text-shadow: 0 0 20px #00ff9d, 0 0 30px #00aa77;
        letter-spacing: 2px;
    }}

    .stTextInput input, .stTextArea textarea {{
        background-color: rgba(0, 15, 10, 0.95) !important;
        color: #00ff9d !important;
        border: 2px solid #00dd99;
        font-family: 'Courier New', monospace;
    }}

    .stButton button {{
        background-color: #001a0f;
        color: #00ff9d;
        border: 2px solid #00cc88;
        font-weight: bold;
        font-family: 'Courier New', monospace;
        text-transform: uppercase;
        box-shadow: 0 0 15px rgba(0, 255, 150, 0.5);
    }}

    .stButton button:hover {{
        background-color: #003322;
        border-color: #00ff9d;
        box-shadow: 0 0 25px #00ff9d;
    }}

    /* Allied sign watermark */
    .stApp::before {{
        content: "ALLIED COMMAND POST — US ARMY SIGNALS INTELLIGENCE";
        position: fixed;
        top: 30px;
        right: 45px;
        font-family: 'Courier New', monospace;
        font-size: 15px;
        color: rgba(255, 240, 120, 0.25);
        transform: rotate(-8deg);
        z-index: 9999;
        letter-spacing: 6px;
    }}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🔒 ALLIED ENIGMA MINER</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #ffdd88;'>US ARMY SIGNALS INTELLIGENCE • BUNKER COMMAND POST 1944</h3>", unsafe_allow_html=True)

st.info("🟡 Demo Mode — Text readability improved with stronger overlay")

# Simple demo interface
stage = st.radio("Stage", ["Compute Setup", "Planning", "Blueprint", "Final Review"], horizontal=True)

if stage == "Compute Setup":
    st.subheader("🔌 Compute Setup")
    st.radio("Source", ["Chutes (Recommended)", "Local GPU", "Custom"], index=0)
    if st.button("Continue", type="primary"):
        st.success("Moving to planning...")

elif stage == "Planning":
    st.subheader("📋 High-Level Planning")
    st.text_area("Challenge", height=80, placeholder="Enter your SN63 challenge...")
    st.text_area("Miner Enhancement Prompt", height=160, 
                 placeholder="Maximize novelty, use strong verification, focus on...")

    if st.button("Approve Plan & Continue", type="primary"):
        st.success("Plan approved!")

elif stage == "Blueprint":
    st.subheader("📋 Orchestrator Blueprint")
    st.write("Swarm configuration and tool recommendations would appear here.")

elif stage == "Final Review":
    st.subheader("🔍 Final Review")
    st.text_area("Solution", "Demo solution output...", height=250)
    if st.button("📦 Package Submission", type="primary"):
        st.success("Submission package created!")
        st.balloons()

st.caption("Allied Bunker Theme • Stronger overlay for better readability")
