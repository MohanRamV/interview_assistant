import { useEffect, useState } from "react";

const SessionList = ({ userEmail, onBack }) => {
  const [sessions, setSessions] = useState([]);
  const API_URL = process.env.REACT_APP_API_URL;
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    const fetchSessions = async () => {
      const res = await fetch(`${API_URL}/sessions/${userEmail}`);
      const data = await res.json();
      setSessions(data);
    };
    fetchSessions();
  }, [API_URL, userEmail]);

  return (
    <div style={{ padding: "2rem" }}>
      <h2>Your Past Interviews</h2>
      <button onClick={onBack} style={{ marginBottom: "1rem" }}>⬅ Back to Dashboard</button>
      {sessions.map((s, idx) => (
        <div key={idx} style={{ border: "1px solid #ccc", padding: "1rem", marginBottom: "1rem" }}>
          <p><strong>Session ID:</strong> {s.session_id}</p>
          <p><strong>Recommendation:</strong> {s.recommendation}</p>
          <p><strong>Date:</strong> {new Date(s.created_at).toLocaleString()}</p>
        </div>
      ))}
    </div>
  );
};

export default SessionList;
