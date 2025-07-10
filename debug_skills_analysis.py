#!/usr/bin/env python3
"""
Debug script to test skills matching and scoring functionality.
Run this script to test the improvements made to scoring and skills matching.
"""

import requests
import json

# Backend URL
BASE_URL = "http://localhost:8000"

def test_skills_matching():
    """Test skills matching with sample data"""
    print("Testing skills matching...")
    
    # Sample resume text
    resume_text = """
    Software Engineer with 5 years of experience in Python, Java, and JavaScript.
    Proficient in React, Node.js, AWS, Docker, and Git.
    Experience with MySQL, MongoDB, and Redis databases.
    Strong background in Agile methodologies and CI/CD pipelines.
    """
    
    # Sample job description
    jd_text = """
    We are looking for a Full Stack Developer with expertise in:
    - Python programming
    - JavaScript and React
    - AWS cloud services
    - Docker containerization
    - Git version control
    - MySQL database management
    - Agile development practices
    """
    
    payload = {
        "resume_text": resume_text,
        "jd_text": jd_text
    }
    
    try:
        response = requests.post(f"{BASE_URL}/debug/test-skills-matching", json=payload)
        result = response.json()
        
        print("Skills Matching Results:")
        print(f"Matched Skills: {result.get('matched_skills', [])}")
        print(f"Missing Skills: {result.get('missing_skills', [])}")
        print(f"Summary: {result.get('summary', '')}")
        print(f"Matched Count: {result.get('matched_count', 0)}")
        print(f"Missing Count: {result.get('missing_count', 0)}")
        
        if result.get('error'):
            print(f"Error: {result['error']}")
            
    except Exception as e:
        print(f"Error testing skills matching: {e}")

def test_scoring():
    """Test scoring with sample Q&A"""
    print("\nTesting scoring...")
    
    # Sample question and answer
    question = "Can you explain your experience with Python programming?"
    answer = "I have been working with Python for about 3 years. I've used it for web development with Django and Flask, data analysis with pandas and numpy, and automation scripts. I'm comfortable with object-oriented programming and have experience with testing frameworks like pytest."
    
    payload = {
        "question": question,
        "answer": answer
    }
    
    try:
        response = requests.post(f"{BASE_URL}/debug/test-scoring", json=payload)
        result = response.json()
        
        print("Scoring Results:")
        print(f"Clarity: {result.get('clarity', 0)}/5")
        print(f"Relevance: {result.get('relevance', 0)}/5")
        print(f"Technical Depth: {result.get('technical_depth', 0)}/5")
        print(f"Confidence: {result.get('confidence', 0)}/5")
        print(f"Average Score: {result.get('average_score', 0):.2f}/5")
        print(f"Comment: {result.get('comment', '')}")
        
        if result.get('error'):
            print(f"Error: {result['error']}")
            
    except Exception as e:
        print(f"Error testing scoring: {e}")

def test_scoring_edge_cases():
    """Test scoring with edge cases"""
    print("\nTesting scoring edge cases...")
    
    test_cases = [
        {
            "question": "What is your experience with machine learning?",
            "answer": "I don't have much experience with machine learning yet, but I'm interested in learning it."
        },
        {
            "question": "Tell me about a challenging project you worked on.",
            "answer": "I worked on a project where we had to migrate a legacy system to a new platform. It was challenging because we had to maintain data integrity while ensuring zero downtime."
        },
        {
            "question": "What are your strengths?",
            "answer": "I'm good at problem-solving and I work well in teams. I also learn new technologies quickly."
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Q: {test_case['question']}")
        print(f"A: {test_case['answer']}")
        
        try:
            response = requests.post(f"{BASE_URL}/debug/test-scoring", json=test_case)
            result = response.json()
            
            print(f"Score: {result.get('average_score', 0):.2f}/5")
            print(f"Comment: {result.get('comment', '')}")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    print("=== Skills Matching and Scoring Debug Tool ===\n")
    
    # Test skills matching
    test_skills_matching()
    
    # Test scoring
    test_scoring()
    
    # Test edge cases
    test_scoring_edge_cases()
    
    print("\n=== Debug Complete ===")
    print("If you see reasonable scores (2-4 range) and skills matches, the improvements are working!")
    print("If you still see 0 scores or no skills matches, there may be an issue with the LLM service.") 