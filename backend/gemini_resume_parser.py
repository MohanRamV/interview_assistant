import os
import json
import re
from backend.llm_client import model

def clean_llm_json(text: str) -> str:
    """
    Removes code fences and extracts JSON string from Gemini output.
    """
    # Strip ```json or ``` and get the JSON body
    cleaned = re.sub(r"^```json|^```|```$", "", text.strip(), flags=re.MULTILINE)
    return cleaned.strip()

def load_prompt_template(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def parse_resume_with_gemini(resume_text: str, prompt_path: str = "prompts/resume_parsing_prompt.txt") -> dict:
    prompt_template = load_prompt_template(prompt_path)
    full_prompt = prompt_template.replace("{{RESUME_TEXT}}", resume_text)

    response = model.generate_content(full_prompt)

    try:
        clean_text = clean_llm_json(response.text)
        return json.loads(clean_text)
    except json.JSONDecodeError:
        return {
            "error": "Invalid JSON from Gemini",
            "raw_output": response.text
        }

