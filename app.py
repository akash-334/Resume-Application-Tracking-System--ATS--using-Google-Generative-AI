import streamlit as st
import PyPDF2 as pdf
import os
import requests
import json

# ✅ Get Llama API Key from environment variables
llama_api_key = os.getenv("LLAMA_API_KEY")

# 🔴 If API Key is missing, show error
if not llama_api_key:
    st.error("Llama API Key is missing. Set it as an environment variable.")
    st.stop()

# ✅ Function to get response from Llama 3 with error handling
def get_llama_response(input_text):
    url = "https://api.together.xyz/v1/chat/completions"  # Together AI endpoint
    headers = {
        "Authorization": f"Bearer {llama_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "meta-llama/llama-3-8b",
        "messages": [
            {"role": "system", "content": "You are an ATS specializing in tech resumes."},
            {"role": "user", "content": input_text}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        with st.spinner("Analyzing resume against job description..."):
            response = requests.post(url, headers=headers, json=data, timeout=90)
            response.raise_for_status()  # Raise error for HTTP issues
            return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            st.error(f"Response text: {e.response.text}")
        return f"Error calling Llama API: {str(e)}"
    except (KeyError, IndexError) as e:
        st.error(f"Response parsing error: {str(e)}")
        if 'response' in locals():
            st.error(f"Full response: {response.text}")
        return f"Error parsing API response: {str(e)}"

# ✅ Function to extract text from uploaded PDF
def input_pdf_text(uploaded_file):
    try:
        reader = pdf.PdfReader(uploaded_file)
        text = ""
        for page in range(len(reader.pages)):
            text += reader.pages[page].extract_text() or ""
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return ""

# ✅ Prompt Template
input_prompt = """
Hey Act Like a skilled or very experienced ATS (Application Tracking System)
with a deep understanding of the tech field, software engineering, data science, data analysis,
and big data engineering. Your task is to evaluate the resume based on the given job description.
You must consider that the job market is very competitive, and you should provide 
the best assistance for improving resumes. Assign the percentage Matching based 
on JD and the missing keywords with high accuracy.
resume:{text}
description:{jd}
I want the response in one single string having the structure:
{{"JD Match":"%","MissingKeywords":[],"Profile Summary":""}}
"""

# ✅ Streamlit UI Setup
st.set_page_config(page_title="Smart ATS", layout="wide")
st.title("📄 Smart ATS (Powered by Llama 3)")
st.markdown("### Improve Your Resume for Applicant Tracking Systems")

# 🔹 Create two columns layout
col1, col2 = st.columns([1, 1])

with col1:
    jd = st.text_area("📌 Paste the Job Description", height=300)

with col2:
    uploaded_file = st.file_uploader("📂 Upload Your Resume (PDF)", type="pdf")
    if uploaded_file:
        st.success(f"✅ File uploaded: {uploaded_file.name}")

# 🔘 Centered submit button
_, center_col, _ = st.columns([1, 2, 1])
with center_col:
    submit = st.button("📊 Analyze Resume", use_container_width=True)

# 🔍 Results Container
result_container = st.container()

# ✅ Handle button click
if submit:
    if not jd:
        st.error("⚠️ Please paste a job description.")
    elif not uploaded_file:
        st.error("⚠️ Please upload a resume PDF.")
    else:
        # 📄 Extract text from PDF
        text = input_pdf_text(uploaded_file)
        
        if not text:
            st.error("❌ Could not extract text from the PDF. Please try another file.")
        else:
            st.info(f"✅ Extracted {len(text)} characters from PDF.")
            
            # 📩 Format input for Llama
            formatted_prompt = input_prompt.format(text=text, jd=jd)
            
            # 🔥 Get response from Llama 3
            response = get_llama_response(formatted_prompt)
            
            # 📊 Display results
            with result_container:
                st.markdown("## 📈 Analysis Results")
                
                try:
                    # ✅ Try parsing as JSON
                    result = json.loads(response)
                    
                    # 🔹 Two-column layout for results
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
                    # ❌ If JSON parsing fails, show raw response
                    st.warning("⚠️ Could not parse the response as JSON. Showing raw response:")
                    st.markdown(response)

# 🏁 Footer
st.markdown("---")
st.markdown("### 🏆 How to get the best results")
st.markdown("""
1️⃣ Paste the **complete job description**  
2️⃣ Upload your **resume in PDF format**  
3️⃣ Click **Analyze Resume** and wait for results  
4️⃣ Review **matches & missing keywords** to improve your resume  
""")
