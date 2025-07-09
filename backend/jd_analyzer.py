import os
import json
import re
from backend.llm_client import model

def clean_llm_json(text: str) -> str:
    cleaned = re.sub(r"^```json|^```|```$", "", text.strip(), flags=re.MULTILINE)
    return cleaned.strip()

def load_prompt_template(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def analyze_job_description(jd_text: str, prompt_path: str = "prompts/jd_parsing_prompt.txt") -> dict:
    prompt_template = load_prompt_template(prompt_path)
    full_prompt = prompt_template.replace("{{JD_TEXT}}", jd_text)

    response = model.generate_content(full_prompt)

    try:
        cleaned = clean_llm_json(response.text)
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return {
            "error": "Invalid JSON from Gemini",
            "raw_output": response.text
        }
