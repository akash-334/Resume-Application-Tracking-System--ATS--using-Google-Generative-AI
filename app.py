import streamlit as st
import PyPDF2 as pdf
import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load API Key from Render Environment Variables
load_dotenv()  # Load .env file if running locally
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    st.error("❌ ERROR: Groq API Key is missing! Set 'GROQ_API_KEY' in Render environment variables.")
    st.stop()

# Initialize LLM
llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama3-8b-8192")

# Function to get response from Llama 3
def get_llama_response(input_text):
    try:
        with st.spinner("🔍 Analyzing resume against job description..."):
            response = llm.invoke(input_text)
        return response
    except Exception as e:
        st.error(f"❌ API Error: {str(e)}")
        return None

# Function to extract text from the uploaded PDF
def input_pdf_text(uploaded_file):
    try:
        reader = pdf.PdfReader(uploaded_file)
        text = "".join([page.extract_text() or "" for page in reader.pages])
        return text
    except Exception as e:
        st.error(f"❌ Error extracting text from PDF: {str(e)}")
        return ""

# Prompt Template
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

# Streamlit UI
st.set_page_config(page_title="Smart ATS", layout="wide")

st.title("🚀 Smart ATS (Powered by Llama 3)")
st.markdown("### 🎯 Improve Your Resume for Applicant Tracking Systems")

# Layout
col1, col2 = st.columns([1, 1])

with col1:
    jd = st.text_area("📌 Paste the Job Description", height=300)

with col2:
    uploaded_file = st.file_uploader("📄 Upload Your Resume (PDF)", type="pdf")
    if uploaded_file:
        st.success(f"✅ File uploaded: {uploaded_file.name}")

# Submit Button
_, center_col, _ = st.columns([1, 2, 1])
with center_col:
    submit = st.button("🔍 Analyze Resume", use_container_width=True)

# Results Container
result_container = st.container()

# Handling Submit
if submit:
    if not jd:
        st.error("⚠️ Please paste a job description.")
    elif not uploaded_file:
        st.error("⚠️ Please upload a resume PDF.")
    else:
        text = input_pdf_text(uploaded_file)
        if not text:
            st.error("❌ Could not extract text from the PDF. Please try another file.")
        else:
            st.info(f"✅ Extracted {len(text)} characters from PDF.")
            
            # Format the input prompt
            formatted_prompt = input_prompt.format(text=text, jd=jd)
            
            # Get response from Llama 3
            response = get_llama_response(formatted_prompt)

            if response is None:
                st.error("❌ No response from the AI. Please try again.")
            else:
                with result_container:
                    st.markdown("## 📊 Analysis Results")
                    
                    try:
                        # Extract response content
                        if isinstance(response, dict):  
                            result = response
                        elif hasattr(response, "content"):  
                            result = json.loads(response.content)
                        else:
                            st.error("Unexpected response format from the API.")
                            st.stop()
                        
                        col1, col2 = st.columns([1, 1])
                        
                        with col1:
                            st.metric("📊 JD Match", result["JD Match"])
                            
                            st.markdown("### 🔍 Missing Keywords")
                            if result["MissingKeywords"]:
                                for keyword in result["MissingKeywords"]:
                                    st.markdown(f"- {keyword}")
                            else:
                                st.markdown("✅ No missing keywords found.")
                        
                        with col2:
                            st.markdown("### 📝 Profile Summary")
                            st.markdown(result["Profile Summary"])
                        
                    except json.JSONDecodeError:
                        st.warning("⚠️ Could not parse the response as JSON. Showing raw response:")
                        st.markdown(response)

# Footer
st.markdown("---")
st.markdown("### ℹ️ How to get the best results:")
st.markdown("""
1. 📌 Paste the **complete job description**.
2. 📄 Upload your **resume in PDF format**.
3. 🔍 Click "Analyze Resume" and **wait for results**.
4. 🎯 Review **matches and missing keywords** to improve your resume.
""")
