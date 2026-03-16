import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(page_title="IO-Assist (Tamil Mahazar & Confession Generator)", page_icon="⚖️", layout="wide")

# Custom CSS for styling
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; color: #1E3A8A; font-weight: bold; text-align: center; }
    .sub-header { font-size: 1.2rem; color: #4B5563; text-align: center; margin-bottom: 2rem; }
    .stTextArea textarea { font-size: 1.1rem; }
    .result-box { background-color: #F3F4F6; padding: 20px; border-radius: 10px; border-left: 5px solid #1E3A8A; margin-top: 20px;}
    .admissible-box { background-color: #ECFDF5; padding: 15px; border-radius: 8px; border-left: 5px solid #10B981; margin-top: 10px;}
    .inadmissible-box { background-color: #FEF2F2; padding: 15px; border-radius: 8px; border-left: 5px solid #EF4444; margin-top: 10px;}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-header'>Anti-Gravity IO-Assist ⚖️</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Automated Defense-Proof Tamil Mahazar & Confession Generator for CCTNS</div>", unsafe_allow_html=True)

# API Key Configuration
api_key = os.getenv("GEMINI_API_KEY")
with st.sidebar:
    st.title("Configuration")
    if not api_key:
        st.warning("⚠️ Gemini API Key not found in environment variables.")
        api_key = st.text_input("Enter your Gemini API Key:", type="password")
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
            st.success("API Key set temporarily for this session.")
    
    doc_type = st.radio("Select Document Type:", ("Confession Statement (Sec 27)", "Observation Mahazar"))

if api_key:
    genai.configure(api_key=api_key)

# System Prompts
CONFESSION_PROMPT = """
You are a Senior Legal Draftsman and Domain Expert for the Tamil Nadu Police.
Your task is to take rough 'Tanglish' or colloquial Tamil police notes and generate a Defense-Proof Confession Statement (Section 27 Evidence Act) in high-level "அலுவலகத் தமிழ்" (Official Tamil) suitable for CCTNS.

CRITICAL LEGAL GUARDRAILS (DEFENSE-SHIELD AUTOMATION):
1. MANDATORY SEPARATION: You MUST strictly separate the 'Admissible Portion' from the 'Inadmissible Portion'.
   - Inadmissible Portion: Details regarding the commission of the crime (e.g., "I murdered him with a knife"). This must be documented but marked clearly as inadmissible and excluded from evidence.
   - Admissible Portion (Discovery of Fact): Information exclusively known to the accused that leads to the discovery of a fact/evidence (e.g., "I hid the knife in the bushes near the temple. If taken there, I will show it.").
2. PREVENT FLAWS: Ensure the language implies voluntary disclosure without coercion. 
3. FORMATTING: Structure the final output clearly with headings for "Case Context", "Inadmissible Portion (Confession of Crime)", and "Admissible Portion (Section 27 Discovery)". Formulate the text so that it aligns strictly with recent Supreme Court judgements on confessions.
"""

MAHAZAR_PROMPT = """
You are a Senior Legal Draftsman and Domain Expert for the Tamil Nadu Police.
Your task is to take rough 'Tanglish' or colloquial Tamil crime scene notes and generate a Defense-Proof Observation Mahazar in high-level "அலுவலகத் தமிழ்" (Official Tamil) suitable for CCTNS.

CRITICAL LEGAL GUARDRAILS (DEFENSE-SHIELD AUTOMATION):
1. MANDATORY SCANNING: Scan the input for the following mandatory details:
   - Boundaries of the crime scene (Four sides: North, South, East, West).
   - Witness presence (Name and details of independent witnesses).
   - Source of light (Crucial if the incident/observation happened at night - e.g., Streetlight, Moonlight, Torchlight).
   - Time and Date of arrest/observation.
2. AUTO-SUGGEST & FILL: If any of these details are missing from the input, you MUST point out the "Legal Flaw" in a separate "Flaw Analysis" section and auto-suggest standard, bullet-proof legal language or placeholders (e.g., "கிழக்கு: [Auto-fill based on location]"). Ensure the drafted mahazar includes sections for these even if missing, highlighting the need for verification.
3. FORMATTING: Use official structures and vocabulary for a Mahazar document.
"""

st.markdown("### 📝 Enter Rough Notes (Tanglish / Local Tamil)")
rough_notes = st.text_area("Type or paste the raw information here...", height=200, placeholder="E.g., Naan avarai kathi aal kuthitten. Andha kathi-a perumal koil pinnala irukka sevuru kitta marachu vechiruken. Enna kootitu pona eduthu tharen...")

if st.button("Generate Defense-Proof Legal Document", type="primary", use_container_width=True):
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar or start the app with it in the .env file.")
    elif not rough_notes.strip():
        st.warning("Please enter some rough notes to process.")
    else:
        with st.spinner(f"Generating {doc_type}... applying Legal Guardrails..."):
            try:
                # Using Gemini system instructions
                model = genai.GenerativeModel('gemini-1.5-pro', system_instruction=CONFESSION_PROMPT if "Confession" in doc_type else MAHAZAR_PROMPT)
                response = model.generate_content(f"USER INPUT:\n{rough_notes}")
                
                st.markdown("### 📄 Generated Official Document")
                st.markdown(f"<div class='result-box'>{response.text}</div>", unsafe_allow_html=True)
                
                # Render download button
                st.download_button(
                    label="Download Document as TXT",
                    data=response.text,
                    file_name=f"{'Confession' if 'Confession' in doc_type else 'Mahazar'}_Statement.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error(f"An error occurred during generation: {str(e)}")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Designed for Tamil Nadu Police | Developed by Anti-Gravity</p>", unsafe_allow_html=True)
