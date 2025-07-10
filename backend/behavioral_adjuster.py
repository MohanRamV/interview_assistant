import json
from backend.llm_client import model

def detect_tone_and_suggest_style(answer: str) -> dict:
    """
    Use Gemini to detect tone/confidence and suggest agent style.
    """
    prompt = f"""Analyze tone and suggest interviewer style for: "{answer}"

Return JSON: {{"tone": "confident/unsure", "suggestion": "supportive/formal/challenging"}}"""

    response = model.generate_content(prompt)

    try:
        return json.loads(response.text.replace("```json", "").replace("```", "").strip())
    except:
        return {"error": "Could not parse Gemini response", "raw_output": response.text}
