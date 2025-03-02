import streamlit as st
import google.generativeai as genai
import PyPDF2 as pdf

# Directly use the API key here
google_api_key = 'AIzaSyA1vr7sklCDHK-IKsb5LelVdoGCpL8b8ng'

# Configure the API with the key
genai.configure(api_key=google_api_key)

# Function to get response from Gemini model
def get_gemini_response(input):
    # First, let's list the available models to find one we can use
    def get_gemini_response(input):
    try:
        models = genai.list_models()
        available_models = [model.name for model in models]
        st.write("Available models:", available_models)
        
        # List of models to try in order of preference
        preferred_models = [
            "models/gemini-2.0-pro-exp",  # Try the newest models first
            "models/gemini-2.0-flash",
            "models/gemini-1.5-pro",
            "models/gemini-1.5-flash",
            "models/gemini-1.5-flash-8b"
        ]
        
        # Find the first preferred model that's available
        selected_model = None
        for model_name in preferred_models:
            if model_name in available_models:
                selected_model = model_name
                break
                
        if not selected_model:
            # If none of our preferred models are available, use the newest non-vision model
            valid_models = [m for m in available_models if 
                           "gemini" in m.lower() and 
                           "vision" not in m.lower() and 
                           "1.0" not in m]  # Skip deprecated models
            
            if valid_models:
                selected_model = valid_models[0]
            else:
                raise Exception("No suitable Gemini models available")
        
        st.write(f"Using model: {selected_model}")
        model = genai.GenerativeModel(selected_model)
        
        response = model.generate_content(input)
        return response.text
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return f"API Error: {str(e)}"
# Function to extract text from the uploaded PDF
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
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
        
        # Get response from the Gemini model
        response = get_gemini_response(formatted_prompt)
        
        # Display the response
        st.subheader(response)
