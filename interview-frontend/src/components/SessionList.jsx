import { useEffect, useState } from "react";
import BackButton from "./BackButton";

const SessionList = ({ userEmail, onBack }) => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [cleaningUp, setCleaningUp] = useState(false);
  const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        setLoading(true);
        const res = await fetch(`${API_URL}/sessions/${userEmail}`);
        const data = await res.json();
        setSessions(data);
      } catch (error) {
        console.error("Failed to fetch sessions:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchSessions();
  }, [API_URL, userEmail]);

  const handleCleanup = async () => {
    if (!window.confirm("This will delete all but the 6 most recent interviews. Continue?")) {
      return;
    }
    
    setCleaningUp(true);
    try {
      const res = await fetch(`${API_URL}/cleanup-sessions/${userEmail}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });
      const data = await res.json();
      
      if (data.error) {
        alert("Cleanup failed: " + data.error);
        return;
      }
      
      alert(`Cleanup completed! ${data.sessions_deleted} old sessions deleted.`);
      // Refresh the sessions list
      const refreshRes = await fetch(`${API_URL}/sessions/${userEmail}`);
      const refreshData = await refreshRes.json();
      setSessions(refreshData);
    } catch (error) {
      console.error("Cleanup failed:", error);
      alert("Failed to cleanup sessions. Please try again.");
    } finally {
      setCleaningUp(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return {
      fullDate: date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      }),
      time: date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true 
      }),
      relative: getRelativeTime(date)
    };
  };

  const getRelativeTime = (date) => {
    const now = new Date();
    
    // Reset time to start of day for accurate day comparison
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const targetDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    
    const diffInMs = today - targetDate;
    const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));
    
    if (diffInDays === 0) return "Today";
    if (diffInDays === 1) return "Yesterday";
    if (diffInDays < 7) return `${diffInDays} days ago`;
    if (diffInDays < 30) return `${Math.floor(diffInDays / 7)} weeks ago`;
    if (diffInDays < 365) return `${Math.floor(diffInDays / 30)} months ago`;
    return `${Math.floor(diffInDays / 365)} years ago`;
  };

  if (loading) {
    return (
      <div style={styles.container}>
        <BackButton onBack={onBack} />
        <div style={styles.loadingContainer}>
          <h2>Loading your interviews...</h2>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <BackButton onBack={onBack} />
      
      <div style={styles.header}>
        <h2 style={styles.title}>Your Interview History</h2>
        {sessions.length > 6 && (
          <button 
            onClick={handleCleanup} 
            disabled={cleaningUp}
            style={styles.cleanupButton}
          >
            {cleaningUp ? "🧹 Cleaning..." : "🧹 Cleanup Old Sessions"}
          </button>
        )}
      </div>
      
      {sessions.length === 0 ? (
        <div style={styles.emptyState}>
          <h3>No interviews yet</h3>
          <p>Start your first interview to see your history here!</p>
        </div>
      ) : (
        <div style={styles.sessionsGrid}>
          {sessions.map((session, idx) => {
            const dateInfo = formatDate(session.created_at);
            return (
              <div key={session._id || idx} style={styles.sessionCard}>
                <div style={styles.sessionHeader}>
                  <h3 style={styles.sessionTitle}>
                    Interview #{idx + 1}
                  </h3>
                  <span style={styles.recommendationBadge}>
                    {session.recommendation}
                  </span>
                </div>
                
                <div style={styles.dateInfo}>
                  <p style={styles.dateText}>
                    <strong>📅 {dateInfo.fullDate}</strong>
                  </p>
                  <p style={styles.timeText}>
                    <strong>🕐 {dateInfo.time}</strong>
                  </p>
                  <p style={styles.relativeText}>
                    {dateInfo.relative}
                  </p>
                </div>

                <div style={styles.scoresContainer}>
                  <h4>Average Scores:</h4>
                  <div style={styles.scoresGrid}>
                    <div style={styles.scoreItem}>
                      <span style={styles.scoreLabel}>Clarity</span>
                      <span style={styles.scoreValue}>{session.average_score?.clarity || 0}/5</span>
                    </div>
                    <div style={styles.scoreItem}>
                      <span style={styles.scoreLabel}>Relevance</span>
                      <span style={styles.scoreValue}>{session.average_score?.relevance || 0}/5</span>
                    </div>
                    <div style={styles.scoreItem}>
                      <span style={styles.scoreLabel}>Technical</span>
                      <span style={styles.scoreValue}>{session.average_score?.technical_depth || 0}/5</span>
                    </div>
                    <div style={styles.scoreItem}>
                      <span style={styles.scoreLabel}>Confidence</span>
                      <span style={styles.scoreValue}>{session.average_score?.confidence || 0}/5</span>
                    </div>
                  </div>
                </div>

                <div style={styles.sessionFooter}>
                  <small style={styles.sessionId}>
                    Session: {session.session_id?.slice(0, 8)}...
                  </small>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    padding: "20px",
    fontFamily: "Segoe UI, sans-serif",
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    color: "white",
    minHeight: "100vh",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "30px",
  },
  title: {
    margin: 0,
    fontSize: "2rem",
  },
  cleanupButton: {
    backgroundColor: "#f44336",
    color: "white",
    padding: "8px 15px",
    borderRadius: "8px",
    border: "none",
    cursor: "pointer",
    fontSize: "0.9rem",
    fontWeight: "bold",
    transition: "background-color 0.2s ease",
  },
  loadingContainer: {
    textAlign: "center",
    padding: "50px",
  },
  emptyState: {
    textAlign: "center",
    padding: "50px",
    backgroundColor: "rgba(0, 0, 0, 0.3)",
    borderRadius: "15px",
    margin: "20px auto",
    maxWidth: "400px",
  },
  sessionsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(350px, 1fr))",
    gap: "20px",
    maxWidth: "1200px",
    margin: "0 auto",
  },
  sessionCard: {
    backgroundColor: "rgba(0, 0, 0, 0.6)",
    borderRadius: "15px",
    padding: "20px",
    boxShadow: "0 4px 15px rgba(0, 0, 0, 0.3)",
    transition: "transform 0.2s ease",
    cursor: "pointer",
  },
  sessionHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "15px",
  },
  sessionTitle: {
    margin: 0,
    fontSize: "1.2rem",
  },
  recommendationBadge: {
    backgroundColor: "#4CAF50",
    color: "white",
    padding: "4px 8px",
    borderRadius: "12px",
    fontSize: "0.8rem",
    fontWeight: "bold",
  },
  dateInfo: {
    marginBottom: "15px",
    padding: "10px",
    backgroundColor: "rgba(255, 255, 255, 0.1)",
    borderRadius: "8px",
  },
  dateText: {
    margin: "5px 0",
    fontSize: "0.9rem",
  },
  timeText: {
    margin: "5px 0",
    fontSize: "0.9rem",
  },
  relativeText: {
    margin: "5px 0",
    fontSize: "0.8rem",
    color: "#ccc",
    fontStyle: "italic",
  },
  scoresContainer: {
    marginBottom: "15px",
  },
  scoresGrid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "8px",
    marginTop: "8px",
  },
  scoreItem: {
    display: "flex",
    justifyContent: "space-between",
    padding: "4px 0",
  },
  scoreLabel: {
    fontSize: "0.85rem",
  },
  scoreValue: {
    fontSize: "0.85rem",
    fontWeight: "bold",
    color: "#4CAF50",
  },
  sessionFooter: {
    borderTop: "1px solid rgba(255, 255, 255, 0.2)",
    paddingTop: "10px",
  },
  sessionId: {
    color: "#ccc",
    fontSize: "0.75rem",
  },
};

export default SessionList;
