import streamlit as st
import PyPDF2 as pdf
import os
import json
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# ✅ Load API Key from Environment Variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    st.error("❌ ERROR: Groq API Key is missing! Set 'GROQ_API_KEY' in Render environment variables.")
    st.stop()

# ✅ Initialize LLM (Llama 3 via Groq)
llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama3-8b-8192")

# ✅ Function to Get Response from Llama 3
def get_llama_response(input_text):
    try:
        with st.spinner("🔍 Analyzing resume against job description..."):
            response = llm.invoke(input_text)
        return response
    except Exception as e:
        st.error(f"❌ API Error: {str(e)}")
        return None

# ✅ Function to Extract Text from PDF
def extract_text_from_pdf(uploaded_file):
    try:
        reader = pdf.PdfReader(uploaded_file)
        text = "".join([page.extract_text() or "" for page in reader.pages])
        return text
    except Exception as e:
        st.error(f"❌ Error extracting text from PDF: {str(e)}")
        return ""

# ✅ Improved Prompt to Force JSON Output - FIX: Escape curly braces in the JSON template
input_prompt = """
You are a highly accurate ATS (Applicant Tracking System) with expertise in software engineering, data science, and big data.
Analyze the resume against the job description and return JSON only.

JSON OUTPUT FORMAT:
{{
    "JD Match": "X%",
    "MissingKeywords": ["keyword1", "keyword2"],
    "Profile Summary": "Your profile summary here"
}}

Resume:
{text}

Job Description:
{jd}
"""

# ✅ Function to Format & Display AI Response
def format_ai_response(response):
    """ Extracts key details from AI response and formats them neatly. """
    
    if hasattr(response, "content"):
        response_text = response.content
    else:
        response_text = str(response)

    # ✅ Debugging: Show Raw AI Response
    st.text_area("🛠 Debugging AI Response", response_text, height=200)

    try:
        # ✅ Try parsing as JSON
        result = json.loads(response_text)
    except json.JSONDecodeError:
        # ✅ If JSON parsing fails, show warning & raw text
        st.warning("⚠️ AI response is not in JSON format. Trying text extraction.")
        return

    # ✅ Display Results in Streamlit
    st.markdown("## 📊 Resume Analysis Results")
    st.metric("📊 JD Match", result.get("JD Match", "N/A"))

    # ✅ Missing Keywords
    st.markdown("### 🔍 Missing Keywords")
    missing_keywords = result.get("MissingKeywords", [])
    if missing_keywords:
        for keyword in missing_keywords:
            st.markdown(f"- **{keyword}**")
    else:
        st.markdown("✅ No missing keywords found.")

    # ✅ Profile Summary
    st.markdown("### 📝 Profile Summary")
    st.markdown(result.get("Profile Summary", "No summary available."))

# ✅ Streamlit UI Setup
st.set_page_config(page_title="Smart ATS", layout="wide")

st.title("🚀 Smart ATS (Powered by Llama 3)")
st.markdown("### 🎯 Improve Your Resume for Applicant Tracking Systems")

# ✅ Layout for Inputs
col1, col2 = st.columns([1, 1])

with col1:
    jd = st.text_area("📌 Paste the Job Description", height=300)

with col2:
    uploaded_file = st.file_uploader("📄 Upload Your Resume (PDF)", type="pdf")
    if uploaded_file:
        st.success(f"✅ File uploaded: {uploaded_file.name}")

# ✅ Submit Button
_, center_col, _ = st.columns([1, 2, 1])
with center_col:
    submit = st.button("🔍 Analyze Resume", use_container_width=True)

# ✅ Results Container
result_container = st.container()

# ✅ Handling Submit Button
if submit:
    if not jd:
        st.error("⚠️ Please paste a job description.")
    elif not uploaded_file:
        st.error("⚠️ Please upload a resume PDF.")
    else:
        text = extract_text_from_pdf(uploaded_file)
        if not text:
            st.error("❌ Could not extract text from the PDF. Please try another file.")
        else:
            st.info(f"✅ Extracted {len(text)} characters from PDF.")
            
            # ✅ Format Prompt
            formatted_prompt = input_prompt.format(text=text, jd=jd)
            
            # ✅ Get Response from Llama 3
            response = get_llama_response(formatted_prompt)

            if response is None:
                st.error("❌ No response from the AI. Please try again.")
            else:
                with result_container:
                    format_ai_response(response)

# ✅ Footer
st.markdown("---")
st.markdown("### ℹ️ How to get the best results:")
st.markdown("""
1. 📌 Paste the **complete job description**.
2. 📄 Upload your **resume in PDF format**.
3. 🔍 Click "Analyze Resume" and **wait for results**.
4. 🎯 Review **matches and missing keywords** to improve your resume.
""")
