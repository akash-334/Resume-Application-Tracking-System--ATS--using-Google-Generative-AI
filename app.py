import streamlit as st
import openai
import PyPDF2 as pdf

# OpenAI API Key (Replace with your actual API key)
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

openai_api_key = os.getenv("openai_api_key")

# Function to get response from ChatGPT model
def get_chatgpt_response(input_text):
    response = openai.ChatCompletion.create(
        model="gpt-4",  # You can use "gpt-3.5-turbo" for a cheaper option
        messages=[{"role": "system", "content": "You are an ATS specializing in tech resumes."},
                  {"role": "user", "content": input_text}]
    )
    return response["choices"][0]["message"]["content"]

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
st.title("Smart ATS")
st.text("Improve Your Resume ATS")
jd = st.text_area("Paste the Job Description")
uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload the pdf")

submit = st.button("Submit")

# Handling submit action
if submit:
    if uploaded_file is not None:
        # Extract text from the uploaded PDF
        text = input_pdf_text(uploaded_file)
        
        # Format the input prompt
        formatted_prompt = input_prompt.format(text=text, jd=jd)
        
        # Get response from OpenAI ChatGPT
        response = get_chatgpt_response(formatted_prompt)
        
        # Display the response
        st.subheader(response)
