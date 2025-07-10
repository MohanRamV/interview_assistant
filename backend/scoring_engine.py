import json
from backend.llm_client import model, clean_llm_json

def score_candidate_answer(question: str, answer: str) -> dict:
    """
    Score the candidate's answer based on interview rubrics.
    """
    prompt = f"""Rate this interview answer (0-5 each): clarity, relevance, technical_depth, confidence.

SCORING GUIDELINES:
- Clarity (0-5): How well the answer is communicated and structured
- Relevance (0-5): How well the answer addresses the question asked
- Technical_depth (0-5): Level of technical detail and expertise shown
- Confidence (0-5): How confidently and assertively the answer is delivered

ONLY assign 0 scores if the answer is completely irrelevant, contains only filler words, or is clearly a placeholder (like 'asdf', 'lorem ipsum', or repeated characters).

For any reasonable attempt to answer, start with at least 1-2 points and adjust based on quality.

Return JSON only:
{{
    "clarity": 4,
    "relevance": 3,
    "technical_depth": 4,
    "confidence": 3,
    "comment": "Brief comment"
}}

Q: {question}
A: {answer}"""

    try:
        response = model.generate_content(prompt)
        cleaned_response = clean_llm_json(response.text)
        result = json.loads(cleaned_response)
        # Ensure all required fields are present with default values
        return {
            "clarity": result.get("clarity", 2),  # Default to 2 for reasonable baseline
            "relevance": result.get("relevance", 2),  # Default to 2 for reasonable baseline
            "technical_depth": result.get("technical_depth", 2),  # Default to 2 for reasonable baseline
            "confidence": result.get("confidence", 2),  # Default to 2 for reasonable baseline
            "comment": result.get("comment", "No comment available")
        }
    except Exception as e:
        print(f"Scoring error: {e}")
        # Return reasonable default scores if parsing fails
        return {
            "clarity": 2,
            "relevance": 2,
            "technical_depth": 2,
            "confidence": 2,
            "comment": "Scoring failed - using default values"
        }
