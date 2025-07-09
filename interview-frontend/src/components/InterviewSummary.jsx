import { useEffect, useState } from "react";

const InterviewSummary = ({ sessionId }) => {
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    const fetchSummary = async () => {
      const API_URL = process.env.REACT_APP_API_URL;
      const res = await fetch(`${API_URL}/interview/summary/${sessionId}`);

      const data = await res.json();
      setSummary(data);
    };
    fetchSummary();
  }, [sessionId]);

  if (!summary) return <div>Loading summary...</div>;

  return (
    <div style={{ padding: "2rem" }}>
      <h2>Interview Summary</h2>
      <p><strong>Recommendation:</strong> {summary.recommendation}</p>

      <h3>Average Scores</h3>
      <ul>
        {Object.entries(summary.average_score).map(([k, v]) => (
          <li key={k}>{k}: {v}</li>
        ))}
      </ul>

      <h3>Transcript</h3>
      {summary.transcript.map((pair, i) => (
        <div key={i} style={{ marginBottom: "1rem" }}>
          <strong>Q:</strong> {pair.question} <br />
          <strong>A:</strong> {pair.answer || "No answer"}
        </div>
      ))}
    </div>
  );
};

export default InterviewSummary;
