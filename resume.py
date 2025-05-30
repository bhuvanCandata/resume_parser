import os
import json
import streamlit as st
import google.generativeai as genai
import tempfile

# --- Configuration ---

# IMPORTANT: API Key Management
# For production applications, avoid hardcoding API keys. It's recommended to use:
# 1. Environment variables: genai.configure(api_key=os.environ["GEMINI_API_KEY"])
# 2. Streamlit secrets: genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
# Ensure the API key has the necessary permissions for file uploads and content generation.
# genai.configure(api_key=os.environ.get("GEMINI_API_KEY")) # Example using environment variable
genai.configure(api_key="AIzaSyAMB0_LqvH731gOEby2SeZ8wlf-6QiII-I") # Replace with your actual API key if not using env var or secrets

# --- Streamlit Page Setup ---
st.set_page_config(layout="wide", page_title="AI Resume Analyzer") 
st.title("🤖 AI Resume Analyzer")

# --- File Uploader ---
uploaded_file_streamlit = st.file_uploader(
    "Upload your Resume (PDF, DOCX, or TXT)", 
    type=['pdf', 'docx', 'txt'], # Supported file types
    accept_multiple_files=False, # Process one resume at a time
    help="Upload your resume in PDF, DOCX, or TXT format. The AI will extract structured information."
)

# --- Prompt for Gemini API ---
# This prompt guides the AI on how to parse the resume and what information to extract.
prompt = """
You are an intelligent AI Resume Parser and Career Analyst trained to extract and enhance structured metadata from resumes to support hiring, upskilling, and AI-powered career recommendations.

📌 Your task:
Read the resume and return a structured JSON object with four main categories:
1. Profile Information
2. Talent Information
3. Anchor Attributes
4. Inferred Persona Insights: Need to explain with contextualixation, expecting what a person might 
  have gained thorugh his education, experience, certifications, hobbies, activities etc. Should be slighly elaborated

You must:
✅ Analyze all details related to **experience**, **certifications**, and **skills**.
✅ Provide **augmented information** — such as inferred job level, personality traits, skill clusters, and career potential — even if not explicitly mentioned.

🔍 Instructions:
Extract the fields **exactly as listed**.
If a field is not found, return "Not specified".
Use your knowledge of industries and job roles to infer missing or unclear values.
Your response should be a **valid 
JSON object**. Do not include commentary or explanation.

📂 Output JSON Format:
{
  "Profile Information": {

  "Full Name": "",
  "DOB": "",
  "Gender": "",
  "Email ID": "",
  "Phone Number": "",
  "Address": "",
  "Nationality": "",
  "Marital Status": "",
  "LinkedIn": "",
  "Career Objective": "",
  "Current Salary": "",
  "Expected Salary": "",
  "Worked Period": "",
  "Gap Period": "",
  "Worked period": "" calculate the years a person worked in various companies from experience
  "Gap period:" "" Calculate the not working period after education or in between switching different job roles/companies
  "Current Location": "",
  "Preferred Location": ""
  "Languages Known": ""
    
  },
  "Talent Information": {
  "Education": "",
  "Skill Clusters":
      {
      "Soft Skills": "",
      "Technical Skills": "",
      "Functional Skills": "",
      "Life Skills": "",
      "Organisational Skills": "",
      "Behaviour Skills": "",
      },
  "Job Titles with Employment Dates and Employer Details": "",
  "Experience Summary per Job Title": "",
  "Certifications": "",
  "Personality Traits": "",
  "AI Involvement": "",
  "Related Job Roles": "",
  "On-the-Job Training": "",
  "Core Tasks": "",
  "Supplemental Tasks": "",
  "Tools Used": ""

  },
  "Anchor Attributes": {
  "Hobbies": "",
  "Personal Interests": "",
  "Achievements": "",
  "Social Causes": "",
  "Behavioral Traits": "",
  "Work Style": "",
  "Volunteering": "",
  "Creative Inclinations": "",
  "Cognitive Preferences": "",
  "Cultural Exposure": ""
  },
"Know about yourself":
{
  "Inferred Persona Insights": ""
}}

Respond ONLY with the structured JSON.
"""

# --- Main Processing Logic ---
if uploaded_file_streamlit is not None:
    st.info(f"Processing '{uploaded_file_streamlit.name}'...")
    
    temp_file_path = None         # Path to the temporary local file
    uploaded_file_gemini = None # Object representing the file uploaded to Gemini service

    try:
        # Step 1: Save the uploaded Streamlit file to a temporary local file.
        # This is necessary because the Gemini API's `upload_file` expects a file path.
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file_streamlit.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file_streamlit.getvalue())
            temp_file_path = tmp_file.name
        
        # Critical check: Ensure temporary file was actually created before proceeding.
        if not os.path.exists(temp_file_path):
            st.error(f"Critical Error: Temporary file at {temp_file_path} was not created or is not accessible.")
            raise FileNotFoundError(f"Temporary file {temp_file_path} not found after creation attempt.")

        # Step 2: Upload the temporary local file to the Gemini API.
        try:
            with st.spinner(f"Uploading '{uploaded_file_streamlit.name}' to Gemini API... This may take a moment."):
                uploaded_file_gemini = genai.upload_file(
                    path=temp_file_path, 
                    display_name=uploaded_file_streamlit.name # Use original filename for display in Gemini
                )
            # st.info(f"Successfully uploaded '{uploaded_file_gemini.display_name}' to Gemini.") # Optional: Can be verbose
        except Exception as e_upload:
            st.error(f"Error uploading file to Gemini API: {e_upload}")
            raise # Re-raise to be caught by the outer try-except, which triggers 'finally' for cleanup

        # Step 3: Generate structured content using the Gemini API with the uploaded file and prompt.
        model = genai.GenerativeModel("gemini-1.5-flash-latest") # Or your preferred model
        try:
            with st.spinner(f"Analyzing '{uploaded_file_streamlit.name}' and extracting data... This can take some time."):
                response = model.generate_content(
                    contents=[uploaded_file_gemini, prompt], # Pass the uploaded file object and the prompt
                    generation_config=genai.types.GenerationConfig(
                        response_mime_type="application/json" # Expect a JSON response
                    )
                )
        except Exception as e_generate:
            st.error(f"Error during resume analysis with Gemini API: {e_generate}")
            raise # Re-raise

        # Step 4: Parse the JSON response from Gemini and display it.
        st.subheader("📊 Extracted Resume Data:")
        try:
            extracted_data = json.loads(response.text)
            st.json(extracted_data)
            st.success("Resume processed and data extracted successfully!")
        except json.JSONDecodeError:
            st.error("Error: Could not parse the response from the AI. The response was not valid JSON.")
            st.caption("Details for developers (raw AI response):")
            st.code(response.text, language="text") # Show raw text for easier debugging
        except Exception as e_parse: 
            st.error(f"An unexpected error occurred while parsing the AI's response: {e_parse}")

    except FileNotFoundError as e_fnf: 
        # Catches the explicit raise if temp file isn't found after creation attempt.
        st.error(f"File System Error: {e_fnf}")
    except Exception as e_global: 
        # Catch-all for other unexpected errors during the process.
        st.error(f"An unexpected global error occurred: {e_global}")
        if hasattr(e_global, 'response') and e_global.response: 
            # Attempt to show more specific API error details if available
            st.error(f"Underlying API Error details: {e_global.response}")
            
    finally:
        # --- Resource Cleanup ---
        # This block executes regardless of whether an exception occurred or not.
        
        # 1. Delete the temporary local file.
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                # st.info(f"Temporary local file {temp_file_path} deleted.") # For debugging
            except Exception as e_remove_local:
                st.warning(f"Error deleting temporary local file {temp_file_path}: {e_remove_local}. Manual cleanup might be required.")
        
        # 2. Delete the file from the Gemini service.
        # Check if 'uploaded_file_gemini' object exists and has a 'name' attribute (which is its ID on Gemini).
        if uploaded_file_gemini and hasattr(uploaded_file_gemini, 'name'):
            try:
                # Deletion from Gemini service can also be a spinner if it's slow, but usually quick.
                # with st.spinner(f"Cleaning up '{uploaded_file_gemini.display_name}' from Gemini service..."):
                genai.delete_file(uploaded_file_gemini.name)
                # st.info(f"File '{uploaded_file_gemini.display_name}' successfully cleaned up from Gemini service.") # For debugging
            except Exception as e_delete_gemini:
                st.warning(f"Could not delete file '{uploaded_file_gemini.display_name}' from Gemini service: {e_delete_gemini}. Manual cleanup via Gemini dashboard might be needed.")
else:
    # Initial message when no file is uploaded yet.
    st.info("👋 Welcome! Please upload a resume (PDF, DOCX, or TXT) to begin the AI-powered analysis.")
