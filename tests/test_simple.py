# test_simple.py
import os
from dotenv import load_dotenv
import requests

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
print(f"API Key: {api_key[:10]}..." if api_key else "No API key found")

# Test Groq API with free model
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Using llama3-8b-8192 which is available for free
data = {
    "model": "llama3-8b-8192",
    "messages": [
        {"role": "user", "content": "Hello, World!"}
    ],
    "temperature": 0.7,
    "max_tokens": 100
}

try:
    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data, timeout=30)
    response.raise_for_status()
    
    result = response.json()
    print(f"Response: {result['choices'][0]['message']['content']}")
    print("✅ Groq API is working!")
    print(f"Model used: llama3-8b-8192 (Free tier)")
except Exception as e:
    print(f"❌ Groq API error: {e}")
    if "401" in str(e):
        print("Check your GROQ_API_KEY in .env file")
    elif "429" in str(e):
        print("Rate limit exceeded - try again in a moment")