import json
from backend.llm_client import model

def detect_tone_and_suggest_style(answer: str) -> dict:
    """
    Use Gemini to detect tone/confidence and suggest agent style.
    """
    prompt = f"""
    Analyze the following candidate answer.

    1. What is the emotional tone? (e.g., confident, unsure, formal, casual)
    2. Does the candidate sound confident?
    3. Suggest how the AI interviewer should respond: more supportive, more formal, or more challenging.

    Answer:
    \"\"\"
    {answer}
    \"\"\"

    Return as JSON.
    """

    response = model.generate_content(prompt)

    try:
        return json.loads(response.text.replace("```json", "").replace("```", "").strip())
    except:
        return {"error": "Could not parse Gemini response", "raw_output": response.text}
