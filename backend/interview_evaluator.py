import json
import re
from typing import Dict, List, Tuple, Any
from backend.llm_client import model
from backend.scoring_engine import score_candidate_answer
from backend.feedback_generator import generate_feedback
from datetime import datetime

class InterviewEvaluator:
    """
    Comprehensive evaluation framework for AI interview system output.
    """
    
    def __init__(self):
        self.evaluation_results = {}
    
    def evaluate_question_consistency(self, questions: List[str], resume_text: str, jd_text: str) -> Dict[str, Any]:
        """
        Evaluate if questions are consistent with resume and job description.
        """
        try:
            prompt = f"""Evaluate the consistency of these interview questions with the provided resume and job description.

Resume: {resume_text[:1000]}...
Job Description: {jd_text[:1000]}...

Questions:
{chr(10).join([f"{i+1}. {q}" for i, q in enumerate(questions)])}

Rate each question on:
1. Relevance to job role (1-5)
2. Alignment with candidate's background (1-5)
3. Appropriateness for interview level (1-5)

Return JSON format:
{{
    "overall_consistency_score": 4.2,
    "question_ratings": [
        {{"question": "Q1", "relevance": 4, "alignment": 5, "appropriateness": 4, "comments": "Good question"}},
        ...
    ],
    "consistency_issues": ["List any issues found"],
    "recommendations": ["Suggestions for improvement"]
}}"""

            response = model.generate_content(prompt)
            
            # Clean the response - handle various formats
            json_text = response.text.strip()
            
            # Remove markdown code blocks
            if json_text.startswith("```json"):
                json_text = json_text[7:]
            elif json_text.startswith("```"):
                json_text = json_text[3:]
            if json_text.endswith("```"):
                json_text = json_text[:-3]
            
            # Find the first occurrence of { and last occurrence of }
            start_idx = json_text.find('{')
            end_idx = json_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_text = json_text[start_idx:end_idx + 1]
            else:
                raise ValueError("No valid JSON object found in response")
            
            json_text = json_text.strip()
            result = json.loads(json_text)
            return result
        except Exception as e:
            return {"error": f"Consistency evaluation failed: {str(e)}"}
    
    def detect_hallucinations(self, ai_output: str, source_materials: Dict[str, str]) -> Dict[str, Any]:
        """
        Detect potential hallucinations in AI-generated content.
        """
        try:
            prompt = f"""Analyze this AI-generated content for potential hallucinations or fabricated information.

When checking if a claim is supported by the source materials (resume, job description):
- Use case-insensitive and fuzzy/semantic matching.
- Consider synonyms, abbreviations, and minor variations as matches.
- For example, “Lead Engineer at FIS Global” is supported if the resume mentions “lead engineer at FIS” or “FIS Global, Lead Engineer.”
- Only flag as “unsupported_claim” if you are confident the claim is not present in any form.

AI Output:
{ai_output}

Source Materials:
Resume: {source_materials.get('resume', '')[:800]}...
Job Description: {source_materials.get('jd', '')[:800]}...

Check for:
1. Claims not supported by source materials
2. Specific details not mentioned in sources
3. Inconsistent information
4. Fabricated company names, dates, or facts

Return JSON:
{{
    "hallucination_score": 0.2,
    "detected_issues": [
        {{"type": "unsupported_claim", "text": "specific claim", "severity": "low/medium/high"}}
    ],
    "confidence": 0.8,
    "recommendations": ["How to improve"]
}}"""

            response = model.generate_content(prompt)
            
            # Clean the response - handle various formats
            json_text = response.text.strip()
            
            # Remove markdown code blocks
            if json_text.startswith("```json"):
                json_text = json_text[7:]
            elif json_text.startswith("```"):
                json_text = json_text[3:]
            if json_text.endswith("```"):
                json_text = json_text[:-3]
            
            # Find the first occurrence of { and last occurrence of }
            start_idx = json_text.find('{')
            end_idx = json_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_text = json_text[start_idx:end_idx + 1]
            else:
                raise ValueError("No valid JSON object found in response")
            
            json_text = json_text.strip()
            result = json.loads(json_text)
            return result
        except Exception as e:
            return {"error": f"Hallucination detection failed: {str(e)}"}
    
    def evaluate_scoring_consistency(self, qa_pairs: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Evaluate if scoring is consistent across similar answers.
        """
        try:
            # Score all answers
            scores = []
            for qa in qa_pairs:
                score = score_candidate_answer(qa['question'], qa['answer'])
                scores.append({
                    'question': qa['question'],
                    'answer': qa['answer'],
                    'score': score
                })
            
            # Analyze consistency
            clarity_scores = [s['score']['clarity'] for s in scores]
            relevance_scores = [s['score']['relevance'] for s in scores]
            technical_scores = [s['score']['technical_depth'] for s in scores]
            confidence_scores = [s['score']['confidence'] for s in scores]
            
            # Calculate variance and consistency metrics
            from statistics import mean, stdev
            
            consistency_analysis = {
                'clarity': {
                    'mean': mean(clarity_scores),
                    'std': stdev(clarity_scores) if len(clarity_scores) > 1 else 0,
                    'variance': stdev(clarity_scores) ** 2 if len(clarity_scores) > 1 else 0
                },
                'relevance': {
                    'mean': mean(relevance_scores),
                    'std': stdev(relevance_scores) if len(relevance_scores) > 1 else 0,
                    'variance': stdev(relevance_scores) ** 2 if len(relevance_scores) > 1 else 0
                },
                'technical_depth': {
                    'mean': mean(technical_scores),
                    'std': stdev(technical_scores) if len(technical_scores) > 1 else 0,
                    'variance': stdev(technical_scores) ** 2 if len(technical_scores) > 1 else 0
                },
                'confidence': {
                    'mean': mean(confidence_scores),
                    'std': stdev(confidence_scores) if len(confidence_scores) > 1 else 0,
                    'variance': stdev(confidence_scores) ** 2 if len(confidence_scores) > 1 else 0
                }
            }
            
            # Flag potential inconsistencies
            inconsistencies = []
            for metric, data in consistency_analysis.items():
                if data['std'] > 1.5:  # High variance threshold
                    inconsistencies.append(f"High variance in {metric} scoring: {data['std']:.2f}")
            
            return {
                'scores': scores,
                'consistency_analysis': consistency_analysis,
                'inconsistencies': inconsistencies,
                'overall_consistency_score': 5 - min(len(inconsistencies), 5)
            }
        except Exception as e:
            return {"error": f"Scoring consistency evaluation failed: {str(e)}"}
    
    def evaluate_feedback_quality(self, feedback_list: List[str]) -> Dict[str, Any]:
        """
        Evaluate the quality and usefulness of generated feedback.
        """
        try:
            prompt = f"""Evaluate the quality of these AI-generated feedback responses.

Feedback Samples:
{chr(10).join([f"{i+1}. {feedback}" for i, feedback in enumerate(feedback_list[:5])])}

Rate each feedback on:
1. Specificity (1-5): How specific and actionable is the feedback?
2. Constructiveness (1-5): Is the feedback helpful and positive?
3. Relevance (1-5): Does it address the actual answer given?
4. Clarity (1-5): Is the feedback clear and understandable?

Return JSON:
{{
    "overall_quality_score": 4.1,
    "feedback_ratings": [
        {{"feedback": "F1", "specificity": 4, "constructiveness": 5, "relevance": 4, "clarity": 4}},
        ...
    ],
    "quality_issues": ["List any issues"],
    "improvement_suggestions": ["How to improve feedback quality"]
}}"""

            response = model.generate_content(prompt)
            
            # Clean the response - handle various formats
            json_text = response.text.strip()
            
            # Remove markdown code blocks
            if json_text.startswith("```json"):
                json_text = json_text[7:]
            elif json_text.startswith("```"):
                json_text = json_text[3:]
            if json_text.endswith("```"):
                json_text = json_text[:-3]
            
            # Find the first occurrence of { and last occurrence of }
            start_idx = json_text.find('{')
            end_idx = json_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_text = json_text[start_idx:end_idx + 1]
            else:
                raise ValueError("No valid JSON object found in response")
            
            json_text = json_text.strip()
            result = json.loads(json_text)
            return result
        except Exception as e:
            return {"error": f"Feedback quality evaluation failed: {str(e)}"}
    
    def run_comprehensive_evaluation(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a comprehensive evaluation of the entire interview session.
        """
        try:
            results = {
                'session_id': session_data.get('session_id'),
                'evaluation_timestamp': str(datetime.utcnow()),
                'overall_score': 0,
                'component_scores': {},
                'issues_found': [],
                'recommendations': []
            }
            # Initialize all result variables to avoid UnboundLocalError
            consistency_result = {}
            hallucination_result = {}
            scoring_result = {}
            feedback_result = {}
            
            # Extract data
            transcript = session_data.get('transcript', [])
            resume_text = session_data.get('resume_text', '')
            jd_text = session_data.get('jd_text', '')
            
            # 1. Question Consistency Evaluation
            questions = [item['question'] for item in transcript if 'question' in item]
            if questions and resume_text and jd_text:
                consistency_result = self.evaluate_question_consistency(questions, resume_text, jd_text)
                if 'error' not in consistency_result:
                    results['component_scores']['question_consistency'] = consistency_result.get('overall_consistency_score', 0)
                else:
                    results['component_scores']['question_consistency'] = 0
                    results['issues_found'].append(f"Question consistency evaluation failed: {consistency_result['error']}")
            else:
                results['component_scores']['question_consistency'] = 0
                if not resume_text or not jd_text:
                    results['issues_found'].append("Cannot evaluate question consistency: Missing resume or JD text")
                if not questions:
                    results['issues_found'].append("Cannot evaluate question consistency: No questions found in transcript")
            
            # 2. Hallucination Detection
            source_materials = {'resume': resume_text, 'jd': jd_text}
            if resume_text and jd_text:
                hallucination_result = self.detect_hallucinations(str(transcript), source_materials)
                if 'error' not in hallucination_result:
                    results['component_scores']['hallucination_score'] = hallucination_result.get('hallucination_score', 0)
                else:
                    results['component_scores']['hallucination_score'] = 0
                    results['issues_found'].append(f"Hallucination detection failed: {hallucination_result['error']}")
            else:
                results['component_scores']['hallucination_score'] = 0
                results['issues_found'].append("Cannot detect hallucinations: Missing resume or JD text")
            
            # 3. Scoring Consistency
            qa_pairs = [{'question': item['question'], 'answer': item['answer']} 
                       for item in transcript if 'question' in item and 'answer' in item]
            if qa_pairs:
                scoring_result = self.evaluate_scoring_consistency(qa_pairs)
                if 'error' not in scoring_result:
                    results['component_scores']['scoring_consistency'] = scoring_result.get('overall_consistency_score', 0)
                else:
                    results['component_scores']['scoring_consistency'] = 0
                    results['issues_found'].append(f"Scoring consistency evaluation failed: {scoring_result['error']}")
            else:
                results['component_scores']['scoring_consistency'] = 0
                results['issues_found'].append("Cannot evaluate scoring consistency: No Q&A pairs found")
            
            # 4. Feedback Quality
            feedback_list = [item.get('feedback', '') for item in transcript if 'feedback' in item and item.get('feedback')]
            if feedback_list:
                feedback_result = self.evaluate_feedback_quality(feedback_list)
                if 'error' not in feedback_result:
                    results['component_scores']['feedback_quality'] = feedback_result.get('overall_quality_score', 0)
                else:
                    results['component_scores']['feedback_quality'] = 0
                    results['issues_found'].append(f"Feedback quality evaluation failed: {feedback_result['error']}")
            else:
                results['component_scores']['feedback_quality'] = 0
                results['issues_found'].append("Cannot evaluate feedback quality: No feedback found in transcript")
            
            # Calculate overall score
            scores = list(results['component_scores'].values())
            results['overall_score'] = sum(scores) / len(scores) if scores else 0
            
            # Compile issues and recommendations
            if consistency_result.get('consistency_issues'):
                results['issues_found'].extend(consistency_result['consistency_issues'])
            if hallucination_result.get('detected_issues'):
                results['issues_found'].extend([f"Hallucination: {issue}" for issue in hallucination_result['detected_issues']])
            if scoring_result.get('inconsistencies'):
                results['issues_found'].extend(scoring_result['inconsistencies'])
            if feedback_result.get('quality_issues'):
                results['issues_found'].extend(feedback_result['quality_issues'])
            
            # Compile recommendations
            if consistency_result.get('recommendations'):
                results['recommendations'].extend(consistency_result['recommendations'])
            if hallucination_result.get('recommendations'):
                results['recommendations'].extend(hallucination_result['recommendations'])
            if feedback_result.get('improvement_suggestions'):
                results['recommendations'].extend(feedback_result['improvement_suggestions'])
            
            return results
            
        except Exception as e:
            # Always return a valid results dict with error info
            return {
                'session_id': session_data.get('session_id'),
                'evaluation_timestamp': str(datetime.utcnow()),
                'overall_score': 'N/A',
                'component_scores': {
                    'question_consistency': 'N/A',
                    'hallucination_score': 'N/A',
                    'scoring_consistency': 'N/A',
                    'feedback_quality': 'N/A',
                },
                'issues_found': [f'Comprehensive evaluation failed: {str(e)}'],
                'recommendations': []
            }

# Global evaluator instance
evaluator = InterviewEvaluator() 