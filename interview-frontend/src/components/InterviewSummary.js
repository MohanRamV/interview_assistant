import React, { useEffect, useState } from "react";

function InterviewSummary({ sessionId, userEmail, onBackToDashboard }) {
  const [summary, setSummary] = useState(null);
  const [evaluation, setEvaluation] = useState(null);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [evaluationError, setEvaluationError] = useState(null);
  
  useEffect(() => {
    if (!sessionId) return;
    
    async function fetchSummary() {
      try {
        const res = await fetch(`http://localhost:8000/interview/summary/${sessionId}?user_email=${encodeURIComponent(userEmail || "")}`);
        const data = await res.json();
        setSummary(data);
      } catch (err) {
        console.error("Summary fetch failed:", err);
      }
    }
  
    fetchSummary();
  }, [sessionId]);

  const downloadReport = () => {
    if (!summary) return;

    const reportContent = generateReportContent(summary);
    const blob = new Blob([reportContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `interview_report_${summary.session_id.slice(0, 8)}_${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const runEvaluation = async () => {
    if (!sessionId) return;
    
    setIsEvaluating(true);
    setEvaluationError(null);
    
    try {
      const res = await fetch(`http://localhost:8000/evaluate/interview/${sessionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      const data = await res.json();
      
      if (data.error) {
        setEvaluationError(data.error);
      } else {
        setEvaluation(data.evaluation);
      }
    } catch (err) {
      setEvaluationError('Failed to run evaluation. Please try again.');
      console.error('Evaluation failed:', err);
    } finally {
      setIsEvaluating(false);
    }
  };

  const generateReportContent = (summary) => {
    const { transcript, average_score, overall_score, recommendation, matched_skills, missing_skills, resume_jd_summary, created_at, security_metrics } = summary;
    
    let content = `INTERVIEW REPORT
${'='.repeat(50)}

Session ID: ${summary.session_id}
Date: ${new Date(created_at).toLocaleString()}
User: ${userEmail}

OVERALL ASSESSMENT
${'-'.repeat(30)}
Overall Score: ${overall_score}/5
Recommendation: ${recommendation}

DETAILED SCORES
${'-'.repeat(30)}
🟢 Clarity: ${average_score.clarity}/5
🔵 Relevance: ${average_score.relevance}/5
🟡 Technical Depth: ${average_score.technical_depth}/5
🟠 Confidence: ${average_score.confidence}/5

SECURITY & INTEGRITY METRICS
${'-'.repeat(30)}
📱 Tab Switches: ${security_metrics?.tab_switch_count || 0} times
🖥️ Fullscreen Mode: ${security_metrics?.fullscreen_used ? 'Used' : 'Not Used'}
⏱️ Interview Duration: ${security_metrics?.interview_duration_minutes || 0} minutes

${security_metrics?.tab_switch_count > 0 ? `⚠️ SECURITY ALERT: User switched tabs ${security_metrics.tab_switch_count} time(s) during interview\n` : ''}

SKILLS ANALYSIS
${'-'.repeat(30)}
Matched Skills (${matched_skills.length}): ${matched_skills.length > 0 ? matched_skills.join(', ') : 'None identified'}
Missing Skills (${missing_skills.length}): ${missing_skills.length > 0 ? missing_skills.join(', ') : 'None identified'}

RESUME-JD SUMMARY
${'-'.repeat(30)}
${resume_jd_summary || 'No summary available'}

INTERVIEW TRANSCRIPT
${'-'.repeat(30)}
`;

    transcript.forEach((item, index) => {
      content += `\nQuestion ${index + 1}:\n${item.question}\n\n`;
      if (item.answer) {
        content += `Answer:\n${item.answer}\n\n`;
      }
      if (item.feedback) {
        content += `Feedback:\n${item.feedback}\n\n`;
      }
      content += `${'-'.repeat(30)}\n`;
    });

    content += `\nReport generated on: ${new Date().toLocaleString()}`;
    return content;
  };

  if (!summary) return <p>Loading summary...</p>;

  // Add null checks for summary data
  if (summary.error) {
    return (
      <div style={styles.container}>
        <h2>Error Loading Summary</h2>
        <p>{summary.error}</p>
        <button onClick={onBackToDashboard}>← Back to Dashboard</button>
      </div>
    );
  }

  const { transcript, average_score, overall_score, recommendation } = summary;
  
  // Add safety checks for required data
  if (!average_score || !transcript) {
    return (
      <div style={styles.container}>
        <h2>Summary Not Ready</h2>
        <p>The interview summary is still being generated. Please wait a moment and try again.</p>
        <button onClick={onBackToDashboard}>← Back to Dashboard</button>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <h2>Interview Summary</h2>
      <p><strong>Session ID:</strong> {summary.session_id}</p>
      <div style={styles.buttonRow}>
        <button onClick={onBackToDashboard}>← Back to Dashboard</button>
        <div style={styles.rightButtons}>
          <button 
            onClick={runEvaluation} 
            disabled={isEvaluating}
            style={styles.evaluateButton}
          >
            {isEvaluating ? "🔍 Evaluating..." : "🔍 Evaluate Quality"}
          </button>
          <button onClick={downloadReport} style={styles.downloadButton}>
            📄 Download Report
          </button>
        </div>
      </div>

      <div style={styles.box}>
        <h3>Overall Assessment</h3>
        <p style={styles.overallScore}>Overall Score: <strong>{overall_score}/5</strong></p>
        <p style={styles.recommendation}>{recommendation}</p>
      </div>

      <div style={styles.box}>
        <h3>Average Scores</h3>
        <p>🟢 Clarity: {average_score.clarity}/5</p>
        <p>🔵 Relevance: {average_score.relevance}/5</p>
        <p>🟡 Technical Depth: {average_score.technical_depth}/5</p>
        <p>🟠 Confidence: {average_score.confidence}/5</p>
      </div>

      {summary.matched_skills && summary.missing_skills && (
        <div style={styles.box}>
          <h3>🔍 Skills Analysis</h3>
          <div style={styles.skillsSection}>
            <div style={styles.skillCategory}>
              <h4 style={{color: "#4CAF50", marginBottom: "10px"}}>✅ Matched Skills ({summary.matched_skills.length})</h4>
              {summary.matched_skills.length > 0 ? (
                <div style={styles.skillsList}>
                  {summary.matched_skills.map((skill, index) => (
                    <span key={index} style={styles.skillTag}>🏷️ {skill}</span>
                  ))}
                </div>
              ) : (
                <p style={styles.noSkills}>No matching skills identified</p>
              )}
            </div>
            
            <div style={styles.skillCategory}>
              <h4 style={{color: "#ff6b6b", marginBottom: "10px"}}>❌ Missing Skills ({summary.missing_skills.length})</h4>
              {summary.missing_skills.length > 0 ? (
                <div style={styles.skillsList}>
                  {summary.missing_skills.map((skill, index) => (
                    <span key={index} style={styles.skillTag}>⚠️ {skill}</span>
                  ))}
                </div>
              ) : (
                <p style={styles.noSkills}>No missing skills identified</p>
              )}
            </div>
          </div>
          
          {summary.resume_jd_summary && (
            <div style={styles.summarySection}>
              <h4 style={{color: "#ffd700", marginBottom: "10px"}}>📋 Resume-JD Summary</h4>
              <p style={styles.summaryText}>{summary.resume_jd_summary}</p>
            </div>
          )}
        </div>
      )}

      {summary.security_metrics && (
        <div style={styles.box}>
          <h3>🔒 Security & Integrity Metrics</h3>
          <p>📱 Tab Switches: {summary.security_metrics.tab_switch_count} times</p>
          {summary.security_metrics.fullscreen_used && (
            <p>🖥️ Fullscreen Mode: Used</p>
          )}
          {summary.security_metrics.interview_duration_minutes > 0 && (
            <p>⏱️ Interview Duration: {summary.security_metrics.interview_duration_minutes} minutes</p>
          )}
          {summary.security_metrics.tab_switch_count > 0 && (
            <div style={styles.securityWarning}>
              <p>⚠️ Security Alert: User switched tabs {summary.security_metrics.tab_switch_count} time(s) during interview</p>
            </div>
          )}
        </div>
      )}

      {evaluationError && (
        <div style={styles.box}>
          <h3>❌ Evaluation Error</h3>
          <p style={styles.errorText}>{evaluationError}</p>
        </div>
      )}

      {evaluation && (
        <div style={styles.box}>
          <h3>🔍 Interview Quality Evaluation</h3>
          <p><strong>Overall Quality Score:</strong> {evaluation.overall_score}/5</p>
          
          {evaluation.component_scores && (
            <div style={styles.evaluationScores}>
              <h4 style={{color: "#ffd700", marginBottom: "10px"}}>Component Scores:</h4>
              <p>📊 Question Consistency: {evaluation.component_scores.question_consistency || 'N/A'}/5</p>
              <p>🎯 Scoring Consistency: {evaluation.component_scores.scoring_consistency || 'N/A'}/5</p>
              <p>💡 Feedback Quality: {evaluation.component_scores.feedback_quality || 'N/A'}/5</p>
            </div>
          )}
          
          {evaluation.issues_found && evaluation.issues_found.length > 0 && (
            <div style={styles.evaluationIssues}>
              <h4 style={{color: "#ff6b6b", marginBottom: "10px"}}>Issues Found:</h4>
              <ul>
                {evaluation.issues_found.map((issue, index) => (
                  <li key={index} style={styles.issueItem}>⚠️ {issue}</li>
                ))}
              </ul>
            </div>
          )}
          
          {evaluation.recommendations && evaluation.recommendations.length > 0 && (
            <div style={styles.evaluationRecommendations}>
              <h4 style={{color: "#4CAF50", marginBottom: "10px"}}>Recommendations:</h4>
              <ul>
                {evaluation.recommendations.map((rec, index) => (
                  <li key={index} style={styles.recommendationItem}>💡 {rec}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      <div style={styles.box}>
        <h3>Transcript</h3>
        {transcript.map((item, index) => (
          <div key={index} style={styles.qaBlock}>
            <p><strong>Q{index + 1}:</strong> {item.question}</p>
            <p><strong>A:</strong> {item.answer}</p>
            {item.feedback && (
              <div style={styles.feedbackBlock}>
                <p style={styles.feedbackLabel}><strong>💡 Feedback:</strong></p>
                <p style={styles.feedbackText}>{item.feedback}</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

const styles = {
  container: {
    padding: "20px",
    fontFamily: "Segoe UI, sans-serif",
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    color: "white",
    minHeight: "100vh",
  },
  box: {
    backgroundColor: "rgba(0, 0, 0, 0.6)",
    padding: "20px",
    borderRadius: "12px",
    marginBottom: "20px",
  },
  qaBlock: {
    marginBottom: "15px",
    padding: "10px",
    backgroundColor: "#ffffff11",
    borderRadius: "6px",
  },
  feedbackBlock: {
    marginTop: "10px",
    padding: "10px",
    backgroundColor: "#ffffff22",
    borderRadius: "6px",
  },
  feedbackLabel: {
    color: "#ffd700", // Gold color for feedback label
    marginBottom: "5px",
  },
  feedbackText: {
    color: "#e0e0e0", // Lighter gray for feedback text
  },
  buttonRow: {
    display: "flex",
    justifyContent: "space-between",
    marginBottom: "20px",
  },
  rightButtons: {
    display: "flex",
    gap: "10px",
  },
  evaluateButton: {
    backgroundColor: "#2196F3", // Blue color for evaluate
    color: "white",
    padding: "10px 20px",
    borderRadius: "8px",
    border: "none",
    cursor: "pointer",
    fontSize: "16px",
    fontWeight: "bold",
    transition: "background-color 0.3s ease",
  },
  downloadButton: {
    backgroundColor: "#4CAF50", // A green color for download
    color: "white",
    padding: "10px 20px",
    borderRadius: "8px",
    border: "none",
    cursor: "pointer",
    fontSize: "16px",
    fontWeight: "bold",
    transition: "background-color 0.3s ease",
  },
  overallScore: {
    fontSize: "24px",
    fontWeight: "bold",
    color: "#ffd700", // Gold color for overall score
    marginBottom: "10px",
  },
  recommendation: {
    fontSize: "18px",
    color: "#e0e0e0",
    marginBottom: "15px",
  },
  securityWarning: {
    marginTop: "15px",
    padding: "10px",
    backgroundColor: "#ff6b6b", // Red color for security warning
    borderRadius: "6px",
    color: "white",
    fontWeight: "bold",
  },
  errorText: {
    color: "#ff6b6b",
    fontWeight: "bold",
  },
  evaluationScores: {
    marginTop: "15px",
  },
  evaluationIssues: {
    marginTop: "15px",
  },
  issueItem: {
    marginBottom: "5px",
    color: "#ff6b6b",
  },
  evaluationRecommendations: {
    marginTop: "15px",
  },
  recommendationItem: {
    marginBottom: "5px",
    color: "#4CAF50",
  },
  skillsSection: {
    display: "flex",
    flexDirection: "column",
    gap: "20px",
  },
  skillCategory: {
    backgroundColor: "rgba(255, 255, 255, 0.1)",
    padding: "15px",
    borderRadius: "8px",
  },
  skillsList: {
    display: "flex",
    flexWrap: "wrap",
    gap: "8px",
  },
  skillTag: {
    backgroundColor: "rgba(255, 255, 255, 0.2)",
    padding: "5px 10px",
    borderRadius: "15px",
    fontSize: "14px",
    display: "inline-block",
  },
  noSkills: {
    color: "#ccc",
    fontStyle: "italic",
  },
  summarySection: {
    marginTop: "20px",
    padding: "15px",
    backgroundColor: "rgba(255, 255, 255, 0.1)",
    borderRadius: "8px",
  },
  summaryText: {
    color: "#e0e0e0",
    lineHeight: "1.5",
  },
};

export default InterviewSummary;
