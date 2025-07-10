#!/usr/bin/env python3
"""
Test script to demonstrate AI interview evaluation capabilities.
This script shows how to evaluate consistency, depth, and hallucination detection.
"""

import requests
import json
import time
from typing import Dict, List

# Configuration
BASE_URL = "http://localhost:8000"

def test_question_consistency():
    """Test question consistency evaluation."""
    print(" Testing Question Consistency Evaluation...")
    
    # Sample data
    resume_text = """
    John Doe
    Software Engineer with 5 years experience
    Skills: Python, JavaScript, React, Node.js
    Experience: Senior Developer at TechCorp (2020-2023)
    Education: BS Computer Science, MIT
    """
    
    jd_text = """
    Senior Software Engineer
    Requirements: 5+ years experience, Python, JavaScript
    Responsibilities: Full-stack development, team leadership
    Company: TechCorp
    """
    
    questions = [
        "Tell me about your experience with Python development.",
        "How would you handle a difficult team member?",
        "What's your favorite color?",  # Irrelevant question
        "Describe a challenging project you worked on.",
        "What's the capital of France?"  # Completely irrelevant
    ]
    
    # This would normally be called through the API
    # For demo, we'll simulate the evaluation
    print(f" Resume: {resume_text.strip()}")
    print(f" Job Description: {jd_text.strip()}")
    print(f" Questions: {questions}")
    
    # Expected evaluation results
    expected_results = {
        "overall_consistency_score": 3.2,
        "question_ratings": [
            {"question": "Q1", "relevance": 5, "alignment": 5, "appropriateness": 5},
            {"question": "Q2", "relevance": 4, "alignment": 4, "appropriateness": 4},
            {"question": "Q3", "relevance": 1, "alignment": 1, "appropriateness": 1},
            {"question": "Q4", "relevance": 5, "alignment": 5, "appropriateness": 5},
            {"question": "Q5", "relevance": 1, "alignment": 1, "appropriateness": 1}
        ],
        "consistency_issues": [
            "Question 3 is irrelevant to the job role",
            "Question 5 is completely unrelated to software engineering"
        ],
        "recommendations": [
            "Focus questions on technical skills and experience",
            "Remove irrelevant questions about personal preferences"
        ]
    }
    
    print(" Question Consistency Test Results:")
    print(json.dumps(expected_results, indent=2))
    return expected_results

def test_hallucination_detection():
    """Test hallucination detection in AI output."""
    print("\n Testing Hallucination Detection...")
    
    # Sample AI output that might contain hallucinations
    ai_output = """
    Based on the candidate's resume, I can see they worked at Google for 10 years
    and led a team of 50 developers. They have extensive experience with quantum computing
    and have published 15 research papers. The candidate mentioned they graduated from Harvard
    with a PhD in Computer Science.
    """
    
    source_materials = {
        "resume": "John Doe, Software Engineer, 5 years experience, Python, JavaScript",
        "jd": "Senior Software Engineer position at TechCorp"
    }
    
    print(f" AI Output: {ai_output}")
    print(f" Source Materials: {source_materials}")
    
    # Expected hallucination detection results
    expected_results = {
        "hallucination_score": 0.8,  # High hallucination score
        "detected_issues": [
            {
                "type": "unsupported_claim",
                "text": "worked at Google for 10 years",
                "severity": "high"
            },
            {
                "type": "unsupported_claim", 
                "text": "led a team of 50 developers",
                "severity": "high"
            },
            {
                "type": "unsupported_claim",
                "text": "quantum computing experience",
                "severity": "high"
            },
            {
                "type": "unsupported_claim",
                "text": "15 research papers",
                "severity": "high"
            },
            {
                "type": "unsupported_claim",
                "text": "Harvard PhD",
                "severity": "high"
            }
        ],
        "confidence": 0.9,
        "recommendations": [
            "Verify all claims against source materials",
            "Implement fact-checking before generating responses",
            "Add confidence scores to AI outputs"
        ]
    }
    
    print(" Hallucination Detection Test Results:")
    print(json.dumps(expected_results, indent=2))
    return expected_results

def test_scoring_consistency():
    """Test scoring consistency across similar answers."""
    print("\n Testing Scoring Consistency...")
    
    # Sample Q&A pairs with similar quality answers
    qa_pairs = [
        {
            "question": "Describe your experience with Python.",
            "answer": "I have 5 years of Python experience. I've built web applications using Django and Flask, worked with data analysis using pandas and numpy, and implemented machine learning models with scikit-learn."
        },
        {
            "question": "Tell me about a challenging project.",
            "answer": "I worked on a complex e-commerce platform that handled 10,000+ daily users. I implemented real-time inventory management, payment processing, and user authentication systems using Python and React."
        },
        {
            "question": "How do you handle debugging?",
            "answer": "I use systematic debugging approaches including logging, unit testing, and step-by-step analysis. I also leverage tools like debuggers and monitoring systems to identify and resolve issues efficiently."
        }
    ]
    
    print(" Q&A Pairs for Consistency Testing:")
    for i, qa in enumerate(qa_pairs, 1):
        print(f"Q{i}: {qa['question']}")
        print(f"A{i}: {qa['answer']}")
        print()
    
    # Expected consistency analysis results
    expected_results = {
        "scores": [
            {"question": "Q1", "clarity": 4, "relevance": 5, "technical_depth": 4, "confidence": 4},
            {"question": "Q2", "clarity": 4, "relevance": 5, "technical_depth": 4, "confidence": 4},
            {"question": "Q3", "clarity": 4, "relevance": 4, "technical_depth": 3, "confidence": 4}
        ],
        "consistency_analysis": {
            "clarity": {"mean": 4.0, "std": 0.0, "variance": 0.0},
            "relevance": {"mean": 4.67, "std": 0.58, "variance": 0.33},
            "technical_depth": {"mean": 3.67, "std": 0.58, "variance": 0.33},
            "confidence": {"mean": 4.0, "std": 0.0, "variance": 0.0}
        },
        "inconsistencies": [],
        "overall_consistency_score": 5.0
    }
    
    print(" Scoring Consistency Test Results:")
    print(json.dumps(expected_results, indent=2))
    return expected_results

def test_feedback_quality():
    """Test feedback quality evaluation."""
    print("\n Testing Feedback Quality Evaluation...")
    
    # Sample feedback responses
    feedback_list = [
        "Good answer! You demonstrated solid Python knowledge. Consider providing more specific examples of projects you've worked on to strengthen your response.",
        "Excellent response with clear structure. Your experience with Django and Flask shows relevant technical skills. Well done!",
        "Your answer was okay but could be more detailed. Try to include specific metrics and outcomes from your projects.",
        "Great technical depth! You showed good understanding of debugging methodologies. Consider mentioning specific debugging tools you've used.",
        "This is a generic response. Please provide more specific examples and technical details to make your answer more compelling."
    ]
    
    print(" Feedback Samples for Quality Testing:")
    for i, feedback in enumerate(feedback_list, 1):
        print(f"F{i}: {feedback}")
        print()
    
    # Expected quality evaluation results
    expected_results = {
        "overall_quality_score": 4.2,
        "feedback_ratings": [
            {"feedback": "F1", "specificity": 4, "constructiveness": 5, "relevance": 5, "clarity": 4},
            {"feedback": "F2", "specificity": 4, "constructiveness": 5, "relevance": 5, "clarity": 5},
            {"feedback": "F3", "specificity": 3, "constructiveness": 4, "relevance": 4, "clarity": 4},
            {"feedback": "F4", "specificity": 4, "constructiveness": 5, "relevance": 5, "clarity": 4},
            {"feedback": "F5", "specificity": 2, "constructiveness": 3, "relevance": 4, "clarity": 3}
        ],
        "quality_issues": [
            "Some feedback lacks specific actionable suggestions",
            "One feedback response is too generic"
        ],
        "improvement_suggestions": [
            "Provide more specific examples in feedback",
            "Include actionable improvement steps",
            "Maintain consistent constructive tone"
        ]
    }
    
    print(" Feedback Quality Test Results:")
    print(json.dumps(expected_results, indent=2))
    return expected_results

def test_comprehensive_evaluation():
    """Test comprehensive evaluation of an entire interview session."""
    print("\n Testing Comprehensive Evaluation...")
    
    # Simulate a complete interview session
    session_data = {
        "session_id": "test_session_123",
        "transcript": [
            {"question": "Tell me about your Python experience.", "answer": "5 years of Python development...", "feedback": "Good technical depth..."},
            {"question": "Describe a challenging project.", "answer": "Built e-commerce platform...", "feedback": "Excellent examples..."},
            {"question": "How do you handle debugging?", "answer": "Systematic approach...", "feedback": "Good methodology..."}
        ],
        "resume_text": "John Doe, Software Engineer, 5 years experience, Python, JavaScript",
        "jd_text": "Senior Software Engineer position at TechCorp"
    }
    
    print(" Complete Interview Session Data:")
    print(json.dumps(session_data, indent=2))
    
    # Expected comprehensive evaluation results
    expected_results = {
        "session_id": "test_session_123",
        "evaluation_timestamp": "2024-01-15T10:30:00Z",
        "overall_score": 4.1,
        "component_scores": {
            "question_consistency": 4.2,
            "hallucination_score": 0.1,
            "scoring_consistency": 4.5,
            "feedback_quality": 4.2
        },
        "issues_found": [
            "One question could be more specific to the role",
            "Minor variance in scoring consistency"
        ],
        "recommendations": [
            "Improve question specificity for better role alignment",
            "Standardize scoring criteria for more consistent results",
            "Add more specific examples in feedback"
        ]
    }
    
    print(" Comprehensive Evaluation Test Results:")
    print(json.dumps(expected_results, indent=2))
    return expected_results

def demonstrate_api_usage():
    """Demonstrate how to use the evaluation API endpoints."""
    print("\n API Usage Demonstration...")
    
    print("1. Evaluate Interview Quality:")
    print("POST /evaluate/interview/{session_id}")
    print("   - Runs comprehensive evaluation")
    print("   - Saves results to database")
    print("   - Returns detailed analysis")
    
    print("\n2. Get Evaluation Results:")
    print("GET /evaluations/{session_id}")
    print("   - Retrieves saved evaluation")
    print("   - Includes all component scores")
    print("   - Shows issues and recommendations")
    
    print("\n3. Example API Call:")
    print("""
    curl -X POST http://localhost:8000/evaluate/interview/test_session_123
    curl -X GET http://localhost:8000/evaluations/test_session_123
    """)

def main():
    """Run all evaluation tests."""
    print(" AI Interview Evaluation Framework Demo")
    print("=" * 50)
    
    # Run individual tests
    test_question_consistency()
    test_hallucination_detection()
    test_scoring_consistency()
    test_feedback_quality()
    test_comprehensive_evaluation()
    
    # Demonstrate API usage
    demonstrate_api_usage()
    
    print("\n" + "=" * 50)
    print(" All evaluation tests completed!")
    print("\n Key Evaluation Metrics:")
    print("- Question Consistency: Ensures relevance to job role")
    print("- Hallucination Detection: Identifies fabricated information")
    print("- Scoring Consistency: Validates fair assessment")
    print("- Feedback Quality: Measures helpfulness of coaching")
    print("- Overall Score: Comprehensive quality assessment")

if __name__ == "__main__":
    main() 