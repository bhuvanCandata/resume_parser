import os
import json
import google.generativeai as genai

# ✅ Configure Gemini API key
genai.configure(api_key="AIzaSyAMB0_LqvH731gOEby2SeZ8wlf-6QiII-I")

# ✅ Path to PDF resume
file_path = r"resume_data/For demo/Rocky Sasmal_Lowes Jun'23.pdf"

# ✅ Output JSON file
output_json_path = "structured_resume_data.json"

# ✅ Final Prompt
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

# ✅ Processing pipeline
try:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} was not found. Please ensure it exists.")

    print(f"Uploading file: {file_path}...")
    uploaded_file = genai.upload_file(path=file_path, display_name="Resume PDF")
    print(f"Uploaded file '{uploaded_file.display_name}' as: {uploaded_file.name}")

    model = genai.GenerativeModel("gemini-1.5-flash-latest")

    print("Generating structured data from the document...")
    response = model.generate_content(
        contents=[uploaded_file, prompt],
        generation_config=genai.types.GenerationConfig(response_mime_type="application/json")
    )

    print("\n--- Parsing Extracted Structured Data ---")
    try:
        extracted_data = json.loads(response.text)
        print(json.dumps(extracted_data, indent=2))

        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(extracted_data, f, ensure_ascii=False, indent=2)

        print(f"\n✅ Cleaned JSON data saved to: {output_json_path}")
    except json.JSONDecodeError as je:
        print(f"❌ Failed to parse JSON from response:\n{response.text}")

except FileNotFoundError as e:
    print(f"❌ File Error: {e}")
except Exception as e:
    print(f"❌ An unexpected error occurred: {e}")
    if hasattr(e, 'response'):
        print(f"🔍 API Error details: {e.response}")