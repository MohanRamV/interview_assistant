import json
from backend.llm_client import model

def compare_resume_to_jd(resume_text, jd_text):
    # Check for empty input
    if not resume_text or not resume_text.strip():
        return {
            "matched_skills": [],
            "missing_skills": [],
            "summary": "Skills analysis failed: Resume text is empty or could not be extracted.",
            "error": "Empty resume text"
        }
    if not jd_text or not jd_text.strip():
        return {
            "matched_skills": [],
            "missing_skills": [],
            "summary": "Skills analysis failed: Job description text is empty or could not be extracted.",
            "error": "Empty job description text"
        }

    prompt = f"""
Compare the following resume and job description. Extract and analyze skills from both documents.

Return a JSON object with the following structure:
{{
    "matched_skills": ["skill1", "skill2", "skill3"],
    "missing_skills": ["skill4", "skill5"],
    "summary": "2-3 line summary of how well this resume matches the JD"
}}

CRITICAL RULES:
- Extract specific technical skills, programming languages, tools, frameworks, and soft skills
- matched_skills: skills that appear in BOTH resume AND job description (be generous with matches)
- missing_skills: skills that are REQUIRED in the job description BUT are NOT mentioned in the resume
- DO NOT include skills from the resume in missing_skills - only include JD requirements that are absent from resume
- If a skill appears in the resume but not in the JD, it should NOT be in missing_skills
- missing_skills should only contain skills that the JD explicitly requires but the resume lacks

SKILL MATCHING GUIDELINES:
- Be flexible with skill variations and synonyms (e.g., "Python" matches "Python programming", "Java" matches "Java development")
- Consider related technologies as matches (e.g., "AWS" matches "Amazon Web Services", "Git" matches "version control")
- Include both exact matches and conceptual matches
- For programming languages, frameworks, tools, databases, cloud platforms, and methodologies
- Be inclusive rather than exclusive - if there's any reasonable connection, count it as a match

Resume:
{resume_text[:2000]}

Job Description:
{jd_text[:2000]}
"""

    try:
        response = model.generate_content(prompt)
        json_text = response.text.strip()
        # Remove markdown code blocks
        if json_text.startswith("```json"):
            json_text = json_text[7:]
        elif json_text.startswith("```"):
            json_text = json_text[3:]
        if json_text.endswith("```"):
            json_text = json_text[:-3]
        # Find the first occurrence of { and last occurrence of }
        start_idx = json_text.find('{')
        end_idx = json_text.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_text = json_text[start_idx:end_idx + 1]
        else:
            return {
                "matched_skills": [],
                "missing_skills": [],
                "summary": "Skills analysis failed: LLM did not return valid JSON. Please check your input files.",
                "error": f"No valid JSON object found in LLM response: {response.text[:200]}..."
            }
        json_text = json_text.strip()
        result = json.loads(json_text)
        # Ensure the required fields exist and are lists
        if "matched_skills" not in result or not isinstance(result["matched_skills"], list):
            result["matched_skills"] = []
        if "missing_skills" not in result or not isinstance(result["missing_skills"], list):
            result["missing_skills"] = []
        if "summary" not in result:
            result["summary"] = "Skills analysis completed."
        # Filter out empty strings and normalize skills
        result["matched_skills"] = [skill.strip() for skill in result["matched_skills"] if skill and skill.strip()]
        result["missing_skills"] = [skill.strip() for skill in result["missing_skills"] if skill and skill.strip()]
        print(f"Skills analysis completed - Matched: {len(result['matched_skills'])}, Missing: {len(result['missing_skills'])}")
        return result
    except json.JSONDecodeError as e:
        print(f"JSON decode error in compare_resume_to_jd: {e}")
        print(f"Raw response: {response.text}")
        return {
            "matched_skills": [],
            "missing_skills": [],
            "summary": "Skills analysis failed due to parsing error.",
            "error": f"Invalid JSON response: {response.text[:200]}..."
        }
    except Exception as e:
        print(f"Error in compare_resume_to_jd: {e}")
        return {
            "matched_skills": [],
            "missing_skills": [],
            "summary": "Skills analysis failed due to processing error.",
            "error": str(e)
        }
