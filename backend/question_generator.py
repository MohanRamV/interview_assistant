from backend.llm_client import model

def generate_followup_question(last_question, last_answer):
    prompt = f"""
Given this previous question and answer from a job interview:

Question: {last_question}
Answer: {last_answer}

Generate one follow-up interview question to probe deeper into their response.
Only return the question text.
"""
    response = model.generate_content(prompt)
    return response.text.strip()
