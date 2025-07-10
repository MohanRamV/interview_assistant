def load_prompt_template(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def generate_dynamic_question(resume_text, jd_text, transcript, question_type, prompt_path="prompts/question_generation_prompt.txt"):
    from backend.llm_client import model
    import json

    # Validate inputs to prevent hallucination
    if not resume_text or not resume_text.strip():
        print("WARNING: Empty or missing resume text - this may cause hallucination")
        resume_text = "No resume information available"
    
    if not jd_text or not jd_text.strip():
        print("WARNING: Empty or missing job description text - this may cause hallucination")
        jd_text = "No job description information available"
    
    # Add explicit instructions to prevent hallucination
    anti_hallucination_instruction = """
CRITICAL: Only ask questions about information that is EXPLICITLY mentioned in the provided resume and job description. 
DO NOT fabricate, invent, or assume any projects, experiences, or details that are not clearly stated in the source materials.
If insufficient information is provided, ask general questions about the candidate's background rather than specific projects.
"""

    template = load_prompt_template(prompt_path)
    formatted_transcript = "\n".join([
        f"Q: {t['question']}\nA: {t.get('answer', '')}" for t in transcript
    ])

    prompt = template.replace("{{RESUME_TEXT}}", resume_text)\
                     .replace("{{JD_TEXT}}", jd_text)\
                     .replace("{{INTERVIEW_TRANSCRIPT}}", formatted_transcript)\
                     .replace("{{QUESTION_TYPE}}", question_type)
    
    # Add anti-hallucination instruction
    prompt += "\n\n" + anti_hallucination_instruction

    response = model.generate_content(prompt)
    return response.text.strip()
