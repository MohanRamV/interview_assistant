import json
from backend.llm_client import model

def compare_resume_to_jd(resume_text, jd_text):
    prompt = f"""
Compare the following resume and job description. Return a JSON with:
- matched_skills: list of skills that appear in both
- missing_skills: list of skills required in the JD but not in resume
- summary: 2–3 line summary of how well this resume matches the JD

Resume:
{resume_text}

Job Description:
{jd_text}
"""

    response = model.generate_content(prompt)
    
    try:
        json_data = response.text.strip("```json").strip("```")
        return json.loads(json_data)
    except Exception as e:
        return {"error": "Invalid response", "raw_output": response.text}
