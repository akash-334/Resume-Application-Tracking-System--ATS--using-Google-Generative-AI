import streamlit as st
import PyPDF2 as pdf
import os
import requests  # To call Llama API

# Get Llama API Key from environment variables
llama_api_key = os.getenv("LLAMA_API_KEY")

# Check if API Key is set
if not llama_api_key:
    st.error("Llama API Key is missing. Set it as an environment variable in Render.")
    st.stop()

# Function to get response from Llama 3
def get_llama_response(input_text):
    url = "https://api.together.xyz/v1/chat/completions"  # Together AI Llama 3 API
    headers = {
        "Authorization": f"Bearer {llama_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "meta-llama/llama-3-8b",  # Choose the specific Llama model
        "messages": [
            {"role": "system", "content": "You are an ATS specializing in tech resumes."},
            {"role": "user", "content": input_text}
        ],
        "temperature": 0.7
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]

# Function to extract text from the uploaded PDF
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        text += reader.pages[page].extract_text() or ""  # Avoid NoneType error
    return text

# Prompt Template
input_prompt = """
Hey Act Like a skilled or very experienced ATS(Application Tracking System)
with a deep understanding of the tech field, software engineering, data science, data analysis,
and big data engineering. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide 
best assistance for improving the resumes. Assign the percentage Matching based 
on JD and the missing keywords with high accuracy.
resume:{text}
description:{jd}

I want the response in one single string having the structure:
{{"JD Match":"%","MissingKeywords":[],"Profile Summary":""}}
"""

# Streamlit App UI
st.title("Smart ATS (Powered by Llama 3)")
st.text("Improve Your Resume ATS")
jd = st.text_area("Paste the Job Description")
uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload the PDF")

submit = st.button("Submit")

# Handling submit action
if submit:
    if uploaded_file is not None:
        # Extract text from the uploaded PDF
        text = input_pdf_text(uploaded_file)
        
        # Format the input prompt
        formatted_prompt = input_prompt.format(text=text, jd=jd)
        
        # Get response from Llama 3
        response = get_llama_response(formatted_prompt)
        
        # Display the response
        st.subheader(response)
