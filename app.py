import streamlit as st
import os
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="IO-Assist (Tamil Mahazar & Confession Generator)", page_icon="⚖️", layout="wide")

st.markdown("""
<style>
    .main-header { font-size: 2.5rem; color: #1E3A8A; font-weight: bold; text-align: center; }
    .sub-header { font-size: 1.2rem; color: #4B5563; text-align: center; margin-bottom: 2rem; }
    .stTextArea textarea { font-size: 1.1rem; }
    .result-box { background-color: #F3F4F6; padding: 20px; border-radius: 10px; border-left: 5px solid #1E3A8A; margin-top: 20px;}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-header'>Anti-Gravity IO-Assist ⚖️</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Automated Defense-Proof Tamil Mahazar & Confession Generator for CCTNS</div>", unsafe_allow_html=True)

api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")

with st.sidebar:
    st.title("Configuration")
    if not api_key:
        st.warning("Groq API Key not found.")
        api_key = st.text_input("Enter your Groq API Key:", type="password")
        if api_key:
            os.environ["GROQ_API_KEY"] = api_key
            st.success("API Key set!")
    doc_type = st.radio("Select Document Type:", ("Confession Statement (Sec 27)", "Observation Mahazar"))
    st.markdown("---")
    st.markdown("**Model Settings**")
    model_choice = st.selectbox("Groq Model:",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"], index=0)

CONFESSION_PROMPT = """You are a Senior Legal Draftsman for Tamil Nadu Police. Generate a Defense-Proof Confession Statement (Section 27 Evidence Act) in official Tamil from rough Tanglish notes.
RULES:
1. Separate Inadmissible Portion (crime commission) from Admissible Portion (discovery of fact).
2. Language must imply voluntary disclosure without coercion.
3. Headings: Case Context, Inadmissible Portion, Admissible Portion (Section 27). Follow Supreme Court judgements."""

MAHAZAR_PROMPT = """You are a Senior Legal Draftsman for Tamil Nadu Police. Generate a Defense-Proof Observation Mahazar in official Tamil from rough Tanglish notes.
RULES:
1. Check: Boundaries (N/S/E/W), Witness details, Source of light, Time and Date.
2. If missing, show Flaw Analysis with auto-suggested legal language.
3. Use official Mahazar document structure."""


def generate_with_groq(api_key, model_name, system_prompt, user_input, max_retries=3):
    client = Groq(api_key=api_key)
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "USER INPUT:\n" + user_input}
                ],
                temperature=0.3,
                max_tokens=4096,
            )
            return response.choices[0].message.content, None
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "rate_limit" in error_str.lower():
                if attempt < max_retries - 1:
                    with st.spinner("Rate limit. Waiting 30s... (Attempt " + str(attempt+1) + "/" + str(max_retries) + ")"):
                        time.sleep(30)
                    continue
                return None, "rate_limit"
            elif "401" in error_str or "invalid_api_key" in error_str.lower():
                return None, "invalid_key"
            else:
                return None, error_str
    return None, "rate_limit"


st.markdown("### Enter Rough Notes (Tanglish / Local Tamil)")
rough_notes = st.text_area("Type or paste the raw information here...", height=200,
    placeholder="E.g., Naan avarai kathi aal kuthitten. Andha kathi-a perumal koil pinnala irukka sevuru kitta marachu vechiruken...")

if st.button("Generate Defense-Proof Legal Document", type="primary", use_container_width=True):
    if not api_key:
        st.error("Please enter your Groq API Key in the sidebar.")
    elif not rough_notes.strip():
        st.warning("Please enter some rough notes to process.")
    else:
        system_prompt = CONFESSION_PROMPT if "Confession" in doc_type else MAHAZAR_PROMPT
        with st.spinner("Generating " + doc_type + "..."):
            result, error = generate_with_groq(api_key, model_choice, system_prompt, rough_notes)
        if result:
            st.success("Document generated successfully!")
            st.markdown("### Generated Official Document")
            st.markdown("<div class='result-box'>" + result + "</div>", unsafe_allow_html=True)
            st.download_button(label="Download Document as TXT", data=result,
                file_name=("Confession" if "Confession" in doc_type else "Mahazar") + "_Statement.txt", mime="text/plain")
        elif error == "invalid_key":
            st.error("Invalid API Key!")
        elif error == "rate_limit":
            st.error("Rate limit. Wait a few minutes and try again.")
        else:
            st.error("Error: " + str(error))

st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Designed for Tamil Nadu Police | Developed by Anti-Gravity</p>", unsafe_allow_html=True)
