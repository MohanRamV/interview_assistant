from backend.llm_client import model

def generate_feedback(question: str, answer: str) -> str:
    """
    Generate coaching-style feedback for a candidate's interview answer.
    """
    prompt = f"""You are an experienced interview coach.

Your job is to review the following candidate's answer to an interview question and provide **brief but useful coaching feedback** (2–3 sentences).

Here is the question:
Q: {question}

And the candidate's answer:
A: {answer}

Please give realistic and constructive feedback on:
- Clarity and structure of the answer
- Whether it directly addressed the question
- Use of examples, specifics, or evidence
- Depth of explanation or logic

Be specific. Avoid vague compliments like "good attempt" or "great answer."
If the answer is strong, say what made it strong.
If it needs improvement, say exactly what and how.

**Output only the feedback text. Do not include labels, intro, or formatting.**"""

    response = model.generate_content(prompt)
    return response.text.strip()
