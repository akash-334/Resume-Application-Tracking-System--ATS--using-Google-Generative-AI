import streamlit as st
import google.generativeai as genai
import PyPDF2 as pdf
import os  # Import os to access environment variables

# Get Gemini API Key from environment variables
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Check if API Key is set
if not gemini_api_key:
    st.error("Google Gemini API Key is missing. Set it as an environment variable in Render.")
    st.stop()

# Configure Gemini AI Client
genai.configure(api_key=gemini_api_key)

# Function to get response from Gemini 2.0 Flash
def get_gemini_response(input_text):
    model = genai.GenerativeModel("gemini-2.0-flash")  # Using Gemini 1.5 Flash (latest fast model)
    response = model.generate_content(input_text)
    return response.text

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
st.title("Smart ATS (Powered by Gemini 2.0 Flash)")
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
        
        # Get response from Gemini
        response = get_gemini_response(formatted_prompt)
        
        # Display the response
        st.subheader(response)
