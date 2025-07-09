import json
from backend.llm_client import model

def score_candidate_answer(question: str, answer: str) -> dict:
    """
    Score the candidate's answer based on interview rubrics.
    """
    prompt = f"""
    You are an AI interview evaluator.

    Based on the following question and answer, rate the candidate on:
    - Clarity (0–5)
    - Relevance to question (0–5)
    - Technical depth (0–5)
    - Confidence/tone (0–5)

    Provide a short comment and return as JSON.

    Question:
    {question}

    Answer:
    {answer}
    """

    response = model.generate_content(prompt)

    try:
        return json.loads(response.text.replace("```json", "").replace("```", "").strip())
    except:
        return {"error": "Could not parse Gemini score", "raw_output": response.text}
