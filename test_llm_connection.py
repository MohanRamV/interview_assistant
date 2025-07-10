#!/usr/bin/env python3
"""
Test script to check LLM connection and identify issues.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.llm_client import generate_content, model
import json

def test_llm_connection():
    """Test basic LLM connection"""
    print("Testing LLM connection...")
    try:
        # Simple test
        test_prompt = "Say 'Hello World' in JSON format: {\"message\": \"Hello World\"}"
        response = generate_content(test_prompt)
        print(f"✅ LLM test successful: {response[:100]}...")
        return True
    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        return False

def test_scoring_prompt():
    """Test the actual scoring prompt"""
    print("\nTesting scoring prompt...")
    try:
        prompt = """Rate this interview answer (0-5 each): clarity, relevance, technical_depth, confidence.

SCORING GUIDELINES:
- Clarity (0-5): How well the answer is communicated and structured
- Relevance (0-5): How well the answer addresses the question asked
- Technical_depth (0-5): Level of technical detail and expertise shown
- Confidence (0-5): How confidently and assertively the answer is delivered

ONLY assign 0 scores if the answer is completely irrelevant, contains only filler words, or is clearly a placeholder (like 'asdf', 'lorem ipsum', or repeated characters).

For any reasonable attempt to answer, start with at least 1-2 points and adjust based on quality.

Return JSON only:
{
    "clarity": 4,
    "relevance": 3,
    "technical_depth": 4,
    "confidence": 3,
    "comment": "Brief comment"
}

Q: What is your experience with Python?
A: I have been working with Python for 3 years, using it for web development with Django and data analysis with pandas."""

        response = generate_content(prompt)
        print(f"✅ Scoring prompt response: {response[:200]}...")
        
        # Try to parse as JSON
        try:
            import re
            cleaned = re.sub(r"^```json|^```|```$", "", response.strip(), flags=re.MULTILINE)
            result = json.loads(cleaned)
            print(f"✅ JSON parsing successful: {result}")
            return True
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"Raw response: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Scoring prompt test failed: {e}")
        return False

def test_model_object():
    """Test the model object used by scoring engine"""
    print("\nTesting model object...")
    try:
        test_prompt = "Say 'Test' in JSON: {\"result\": \"test\"}"
        response = model.generate_content(test_prompt)
        print(f"✅ Model object test successful: {response.text[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Model object test failed: {e}")
        return False

if __name__ == "__main__":
    print("=== LLM Connection Debug Tool ===\n")
    
    # Test 1: Basic LLM connection
    llm_ok = test_llm_connection()
    
    # Test 2: Model object
    model_ok = test_model_object()
    
    # Test 3: Scoring prompt
    scoring_ok = test_scoring_prompt()
    
    print("\n=== Summary ===")
    print(f"LLM Connection: {'✅ Working' if llm_ok else '❌ Failed'}")
    print(f"Model Object: {'✅ Working' if model_ok else '❌ Failed'}")
    print(f"Scoring Prompt: {'✅ Working' if scoring_ok else '❌ Failed'}")
    
    if not llm_ok:
        print("\n🔧 Troubleshooting:")
        print("1. Check if GROQ_API_KEY is set correctly")
        print("2. Verify internet connection")
        print("3. Check if Groq service is available")
    elif not scoring_ok:
        print("\n🔧 Scoring Issue:")
        print("The LLM is working but scoring prompt is failing")
        print("This might be due to prompt format or JSON parsing issues") 