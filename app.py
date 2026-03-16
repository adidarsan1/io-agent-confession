import streamlit as st
import google.generativeai as genai
import os
import time
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

    st.markdown("---")
    st.markdown("**Model Settings**")
    model_choice = st.selectbox(
        "Gemini Model:",
        ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash", "gemini-1.5-flash-8b"],
        index=0,
        help="If quota exceeded on one model, try another free model."
    )

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


def generate_with_retry(model_name, system_prompt, user_input, max_retries=3):
    """Generate content with automatic retry on quota/rate limit errors."""
    for attempt in range(max_retries):
        try:
            model = genai.GenerativeModel(
                model_name,
                system_instruction=system_prompt
            )
            response = model.generate_content(f"USER INPUT:\n{user_input}")
            return response.text, None

        except Exception as e:
            error_str = str(e)

            # 429 Rate limit — wait and retry
            if "429" in error_str and "retry" in error_str.lower():
                # Extract retry delay from error if possible
                wait_seconds = 30
                try:
                    import re
                    match = re.search(r'retry_delay\s*\{[^}]*seconds:\s*(\d+)', error_str)
                    if match:
                        wait_seconds = int(match.group(1)) + 5
                except Exception:
                    pass

                if attempt < max_retries - 1:
                    with st.spinner(f"⏳ Rate limit hit. {wait_seconds} seconds wait பண்றோம்... (Attempt {attempt + 1}/{max_retries})"):
                        time.sleep(wait_seconds)
                    continue
                else:
                    return None, "quota_exhausted"

            # 429 Free tier fully exhausted (limit: 0)
            elif "429" in error_str and ("limit: 0" in error_str or "quota" in error_str.lower()):
                return None, "quota_exhausted"

            # 404 Model not found
            elif "404" in error_str:
                return None, "model_not_found"

            else:
                return None, error_str

    return None, "quota_exhausted"


st.markdown("### 📝 Enter Rough Notes (Tanglish / Local Tamil)")
rough_notes = st.text_area(
    "Type or paste the raw information here...",
    height=200,
    placeholder="E.g., Naan avarai kathi aal kuthitten. Andha kathi-a perumal koil pinnala irukka sevuru kitta marachu vechiruken. Enna kootitu pona eduthu tharen..."
)

if st.button("Generate Defense-Proof Legal Document", type="primary", use_container_width=True):
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar or start the app with it in the .env file.")
    elif not rough_notes.strip():
        st.warning("Please enter some rough notes to process.")
    else:
        system_prompt = CONFESSION_PROMPT if "Confession" in doc_type else MAHAZAR_PROMPT

        with st.spinner(f"Generating {doc_type}... Legal Guardrails apply பண்றோம்..."):
            result, error = generate_with_retry(model_choice, system_prompt, rough_notes)

        if result:
            st.success("✅ Document generated successfully!")
            st.markdown("### 📄 Generated Official Document")
            st.markdown(f"<div class='result-box'>{result}</div>", unsafe_allow_html=True)

            st.download_button(
                label="📥 Download Document as TXT",
                data=result,
                file_name=f"{'Confession' if 'Confession' in doc_type else 'Mahazar'}_Statement.txt",
                mime="text/plain"
            )

        elif error == "quota_exhausted":
            st.error("🚫 Gemini API Quota Exhausted!")
            st.markdown("""
            ### இதை எப்படி சரி பண்றது:

            **Option 1 — Billing Enable பண்ணுங்க (Recommended):**
            1. [Google AI Studio](https://aistudio.google.com) போங்க
            2. Settings → Billing → Enable pay-as-you-go
            3. மிகவும் cheap — ~$0.001 per request

            **Option 2 — Sidebar-ல் வேற Model Try பண்ணுங்க:**
            - `gemini-2.0-flash-lite` (lightest, separate quota)
            - `gemini-1.5-flash` (separate quota)
            - `gemini-1.5-flash-8b` (most lenient free tier)

            **Option 3 — நாளைக்கு Try பண்ணுங்க:**
            - Free tier daily quota midnight-ல reset ஆகும்

            **Option 4 — புதுசா API Key எடுங்க:**
            - [Google AI Studio](https://aistudio.google.com/apikey) போய் new key create பண்ணுங்க
            """)

        elif error == "model_not_found":
            st.error(f"❌ Model '{model_choice}' not found. Sidebar-ல் வேற model select பண்ணுங்க.")

        else:
            st.error(f"❌ Error: {error}")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Designed for Tamil Nadu Police | Developed by Anti-Gravity</p>", unsafe_allow_html=True)
