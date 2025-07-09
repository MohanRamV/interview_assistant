from backend.llm_client import model

def generate_feedback(question: str, answer: str) -> str:
    """
    Generate coaching-style feedback for a candidate's answer.
    """
    prompt = f"""
    You are a career coach.

    Review the candidate's answer to the interview question and provide helpful feedback to improve clarity, structure, or depth.

    Question:
    {question}

    Answer:
    {answer}

    Give feedback in 2–3 sentences.
    """

    response = model.generate_content(prompt)
    return response.text.strip()
