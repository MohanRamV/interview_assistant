# AI Interview Evaluation Framework

This framework provides comprehensive evaluation capabilities for AI interview systems, including consistency checks, hallucination detection, and quality assessment.

## 🎯 Evaluation Capabilities

### 1. **Question Consistency Evaluation**
- **Purpose**: Ensures interview questions are relevant to the job role and candidate background
- **Metrics**: Relevance, alignment, appropriateness
- **Output**: Consistency score and specific recommendations

### 2. **Hallucination Detection**
- **Purpose**: Identifies AI-generated content that contains fabricated or unsupported information
- **Detection**: Claims not in source materials, inconsistent information, fabricated facts
- **Output**: Hallucination score and flagged issues

### 3. **Scoring Consistency Analysis**
- **Purpose**: Validates that similar quality answers receive consistent scores
- **Metrics**: Variance analysis, statistical consistency
- **Output**: Consistency metrics and flagged inconsistencies

### 4. **Feedback Quality Assessment**
- **Purpose**: Evaluates the usefulness and constructiveness of AI-generated feedback
- **Metrics**: Specificity, constructiveness, relevance, clarity
- **Output**: Quality score and improvement suggestions

## 🚀 Quick Start

### 1. Run the Test Script
```bash
python test_evaluation.py
```

This will demonstrate all evaluation capabilities with sample data.

### 2. Use the API Endpoints

#### Evaluate Interview Quality
```bash
curl -X POST http://localhost:8000/evaluate/interview/{session_id}
```

#### Get Evaluation Results
```bash
curl -X GET http://localhost:8000/evaluations/{session_id}
```

## 📊 Evaluation Metrics

### Question Consistency Score (1-5)
- **5**: All questions highly relevant and appropriate
- **4**: Most questions relevant with minor issues
- **3**: Mixed relevance, some questions need improvement
- **2**: Several irrelevant or inappropriate questions
- **1**: Poor question selection

### Hallucination Score (0-1)
- **0**: No hallucinations detected
- **0.3**: Minor hallucinations
- **0.7**: Significant hallucinations
- **1.0**: Extensive hallucinations

### Scoring Consistency Score (1-5)
- **5**: Highly consistent scoring
- **4**: Mostly consistent with minor variance
- **3**: Moderate consistency issues
- **2**: Significant inconsistencies
- **1**: Poor scoring consistency

### Feedback Quality Score (1-5)
- **5**: Excellent, specific, actionable feedback
- **4**: Good feedback with minor improvements needed
- **3**: Adequate feedback
- **2**: Poor quality feedback
- **1**: Unhelpful or generic feedback

## 🔍 Example Usage

### Python Script Example
```python
import requests

# Evaluate an interview session
response = requests.post(f"http://localhost:8000/evaluate/interview/test_session_123")
evaluation = response.json()

print(f"Overall Score: {evaluation['evaluation']['overall_score']}")
print(f"Question Consistency: {evaluation['evaluation']['component_scores']['question_consistency']}")
print(f"Hallucination Score: {evaluation['evaluation']['component_scores']['hallucination_score']}")
```

### Expected Output
```json
{
  "message": "Evaluation completed successfully",
  "evaluation": {
    "session_id": "test_session_123",
    "overall_score": 4.1,
    "component_scores": {
      "question_consistency": 4.2,
      "hallucination_score": 0.1,
      "scoring_consistency": 4.5,
      "feedback_quality": 4.2
    },
    "issues_found": [
      "One question could be more specific to the role"
    ],
    "recommendations": [
      "Improve question specificity for better role alignment"
    ]
  }
}
```

## 🛠️ Implementation Details

### Database Collections
- `interview_evaluations`: Stores evaluation results
- `parsed_resumes`: Cached resume parsing results
- `parsed_jds`: Cached job description parsing results

### Key Components
1. **InterviewEvaluator Class**: Main evaluation logic
2. **API Endpoints**: RESTful interface for evaluations
3. **Test Script**: Comprehensive demonstration
4. **Database Integration**: Persistent storage of results

## 📈 Benefits

### For Developers
- **Quality Assurance**: Ensure AI output meets standards
- **Debugging**: Identify specific issues in AI responses
- **Improvement**: Get actionable recommendations

### For Users
- **Reliability**: Trust in AI interview quality
- **Consistency**: Fair and consistent evaluations
- **Transparency**: Clear understanding of AI performance

### For Business
- **Cost Reduction**: Identify and fix issues early
- **Risk Mitigation**: Prevent poor AI outputs
- **Compliance**: Ensure fair and unbiased interviews

## 🔧 Customization

### Adding New Evaluation Metrics
1. Add new method to `InterviewEvaluator` class
2. Update `run_comprehensive_evaluation` method
3. Add corresponding API endpoint

### Modifying Thresholds
- Adjust scoring thresholds in evaluation methods
- Update consistency thresholds in `evaluate_scoring_consistency`
- Modify hallucination detection sensitivity

## 🚨 Troubleshooting

### Common Issues
1. **API Connection Error**: Ensure backend is running
2. **Session Not Found**: Check session ID validity
3. **Evaluation Failed**: Review session data completeness

### Debug Mode
Enable detailed logging by setting environment variable:
```bash
export DEBUG_EVALUATION=true
```

## 📝 Best Practices

1. **Regular Evaluation**: Run evaluations after each interview session
2. **Monitor Trends**: Track evaluation scores over time
3. **Act on Recommendations**: Implement suggested improvements
4. **Document Issues**: Keep records of identified problems
5. **Continuous Improvement**: Use evaluation results to enhance the system

## 🤝 Contributing

To add new evaluation capabilities:
1. Fork the repository
2. Add new evaluation methods
3. Update tests and documentation
4. Submit pull request

---

**Note**: This evaluation framework is designed to work with the AI interview system and provides comprehensive quality assessment capabilities. 