import streamlit as st
import PyPDF2 as pdf
import os
import re
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# ✅ Load API Key from Environment Variables (Render Deployment)
load_dotenv()  
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    st.error("❌ ERROR: Groq API Key is missing! Set 'GROQ_API_KEY' in Render environment variables.")
    st.stop()

# ✅ Initialize LLM (Llama 3 via Groq)
llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama3-8b-8192")

# ✅ Function to get response from AI
def get_llama_response(input_text):
    try:
        with st.spinner("🔍 Analyzing resume against job description..."):
            response = llm.invoke(input_text)
        return response
    except Exception as e:
        st.error(f"❌ API Error: {str(e)}")
        return None

# ✅ Function to extract text from PDF
def extract_text_from_pdf(uploaded_file):
    try:
        reader = pdf.PdfReader(uploaded_file)
        text = "".join([page.extract_text() or "" for page in reader.pages])
        return text
    except Exception as e:
        st.error(f"❌ Error extracting text from PDF: {str(e)}")
        return ""

# ✅ Formatting Prompt for Llama 3
input_prompt = """
Hey, act like a skilled ATS (Applicant Tracking System) with deep expertise in software engineering, data science, and big data.
Evaluate the resume based on the provided job description. Consider the competitive job market and provide detailed feedback.

Assign a **matching percentage**, list missing **keywords**, and generate a **profile summary**.

**Resume:** {text}
**Job Description:** {jd}

Provide a structured response in JSON format:
{{
    "JD Match": "X%",
    "MissingKeywords": ["keyword1", "keyword2"],
    "Profile Summary": "Your profile summary here"
}}
"""

# ✅ Function to Format AI Response
def format_ai_response(response):
    """ Extracts key details from AI response and formats them neatly. """

    if hasattr(response, "content"):
        response_text = response.content
    else:
        response_text = str(response)

    try:
        result = json.loads(response_text)  # ✅ Try parsing as JSON
    except json.JSONDecodeError:
        # ✅ If JSON fails, extract manually using regex
        match_percentage = re.search(r"JD Match:\s*(\d+)%", response_text)
        match_percentage = match_percentage.group(1) + "%" if match_percentage else "N/A"

        missing_keywords_match = re.search(r"\* \[(.*?)\]", response_text)
        missing_keywords = missing_keywords_match.group(1).split(", ") if missing_keywords_match else []

        profile_summary_match = re.search(r"Profile Summary:\n(.*?)\n\nNote:", response_text, re.DOTALL)
        profile_summary = profile_summary_match.group(1).strip() if profile_summary_match else "No summary found."

        # ✅ Display Results in Streamlit
        st.markdown("## 📊 Resume Analysis Results")
        st.metric("📊 JD Match", match_percentage)

        st.markdown("### 🔍 Missing Keywords")
        if missing_keywords:
            for keyword in missing_keywords:
                st.markdown(f"- **{keyword}**")
        else:
            st.markdown("✅ No missing keywords found.")

        st.markdown("### 📝 Profile Summary")
        st.markdown(profile_summary)

        return

    # ✅ Display JSON Response
    st.markdown("## 📊 Resume Analysis Results")
    st.metric("📊 JD Match", result.get("JD Match", "N/A"))

    st.markdown("### 🔍 Missing Keywords")
    missing_keywords = result.get("MissingKeywords", [])
    if missing_keywords:
        for keyword in missing_keywords:
            st.markdown(f"- **{keyword}**")
    else:
        st.markdown("✅ No missing keywords found.")

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
