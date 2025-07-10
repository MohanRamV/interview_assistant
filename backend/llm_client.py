import os
import json
import re
import requests
import time
import random
from dotenv import load_dotenv

# Commented out Gemini implementation
# import google.generativeai as genai
# load_dotenv()
# api_key = os.getenv("GOOGLE_API_KEY")
# if not api_key:
#     raise ValueError("GOOGLE_API_KEY environment variable is required")
# genai.configure(api_key=api_key)

# Groq implementation
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = "https://api.groq.com/openai/v1/chat/completions"

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is required")

# Available Groq models (all free tier)
GROQ_MODELS = [
    "llama3-8b-8192",      # Fast, good balance
    "llama3-70b-8192",     # More capable
    "mixtral-8x7b-32768",  # Very fast
    "gemma2-9b-it"         # Good for coding
]

# Rate limiting variables
last_request_time = 0
min_request_interval = 0.2  # 200ms between requests (increased for safety)

def clean_llm_json(text: str) -> str:
    """
    Removes code fences and extracts JSON string from Groq output.
    """
    # First, remove code fences
    cleaned = re.sub(r"^```json|^```|```$", "", text.strip(), flags=re.MULTILINE)
    cleaned = cleaned.strip()
    
    # Find the first occurrence of { and last occurrence of }
    start_idx = cleaned.find('{')
    end_idx = cleaned.rfind('}')
    
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        # Extract just the JSON part
        json_part = cleaned[start_idx:end_idx + 1]
        return json_part.strip()
    
    # If no JSON braces found, return the cleaned text as is
    return cleaned

def make_groq_request(data, max_retries=3):
    """
    Make a request to Groq API with retry logic and rate limiting.
    """
    global last_request_time
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    for attempt in range(max_retries):
        try:
            # Rate limiting
            current_time = time.time()
            time_since_last = current_time - last_request_time
            if time_since_last < min_request_interval:
                sleep_time = min_request_interval - time_since_last
                time.sleep(sleep_time)
            
            last_request_time = time.time()
            
            response = requests.post(GROQ_BASE_URL, headers=headers, json=data, timeout=60)
            
            if response.status_code == 429:
                # Rate limit hit - exponential backoff
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Rate limit hit, waiting {wait_time:.2f} seconds...")
                time.sleep(wait_time)
                continue
            elif response.status_code == 500:
                # Server error - retry with backoff
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Server error, retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
                continue
            else:
                response.raise_for_status()
                return response.json()
                
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise e
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            print(f"Request failed, retrying in {wait_time:.2f} seconds...")
            time.sleep(wait_time)
    
    raise Exception(f"Failed after {max_retries} attempts")

def generate_content(prompt: str) -> str:
    """
    Generate content using Groq API with rate limiting, retry logic, and model fallback.
    """
    # Try different models if one fails
    for model_name in GROQ_MODELS:
        data = {
            "model": model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        try:
            print(f"Trying model: {model_name}")
            result = make_groq_request(data)
            print(f"✅ Success with model: {model_name}")
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"❌ Model {model_name} failed: {str(e)[:50]}...")
            if "429" in str(e):
                print(f"Rate limit hit for {model_name}, trying next model...")
                continue
            elif "500" in str(e):
                print(f"Server error for {model_name}, trying next model...")
                continue
            else:
                # For other errors, try next model
                continue
    
    # If all models fail, return error
    return f"Error: All Groq models failed. Please try again later."

def generate_json_content(prompt: str) -> dict:
    """
    Generate content and parse as JSON using Groq.
    """
    try:
        response_text = generate_content(prompt)
        cleaned = clean_llm_json(response_text)
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return {
            "error": "Invalid JSON from Groq",
            "raw_output": response_text if 'response_text' in locals() else "No response"
        }
    except Exception as e:
        print(f"Error generating JSON content: {e}")
        return {
            "error": f"Generation failed: {str(e)}"
        }

# Create a model object for compatibility with existing code
class GroqModel:
    def generate_content(self, prompt: str):
        class Response:
            def __init__(self, text):
                self.text = text
        
        result = generate_content(prompt)
        return Response(result)

model = GroqModel()  
