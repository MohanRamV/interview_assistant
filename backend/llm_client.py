import os
import json
import re
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("models/gemini-2.0-flash")

def clean_llm_json(text: str) -> str:
    """
    Removes code fences and extracts JSON string from Gemini output.
    """
    cleaned = re.sub(r"^```json|^```|```$", "", text.strip(), flags=re.MULTILINE)
    return cleaned.strip()

def generate_content(prompt: str) -> str:
    """
    Generate content using the configured model.
    """
    response = model.generate_content(prompt)
    return response.text.strip()

def generate_json_content(prompt: str) -> dict:
    """
    Generate content and parse as JSON.
    """
    response = model.generate_content(prompt)
    try:
        cleaned = clean_llm_json(response.text)
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return {
            "error": "Invalid JSON from Gemini",
            "raw_output": response.text
        }  
