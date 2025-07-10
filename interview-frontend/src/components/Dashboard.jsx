const Dashboard = ({ userName, onStartInterview, onViewSessions, onUpload, onLogout }) => {
    return (
      <div style={styles.container}>
        <div style={styles.card}>
          <h2 style={styles.title}>Welcome back, {userName}!</h2>
          <p style={styles.subtitle}>What would you like to do today?</p>
          
          <div style={styles.buttonContainer}>
            <button onClick={onStartInterview} style={styles.primaryButton}>
              🚀 Start New Interview
            </button>
            
            <button onClick={onViewSessions} style={styles.secondaryButton}>
              📊 View Past Interviews
            </button>
            
            <button onClick={onLogout} style={styles.logoutButton}>
              🚪 Logout
            </button>
          </div>
        </div>
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
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  },
  card: {
    backgroundColor: "rgba(0, 0, 0, 0.6)",
    padding: "40px",
    borderRadius: "20px",
    textAlign: "center",
    maxWidth: "500px",
    width: "100%",
    boxShadow: "0 4px 20px rgba(0, 0, 0, 0.3)",
  },
  title: {
    marginBottom: "10px",
    fontSize: "2.2rem",
    fontWeight: "bold",
  },
  subtitle: {
    marginBottom: "40px",
    fontSize: "1.1rem",
    color: "#ccc",
  },
  buttonContainer: {
    display: "flex",
    flexDirection: "column",
    gap: "15px",
  },
  primaryButton: {
    padding: "15px 30px",
    backgroundColor: "#4CAF50",
    color: "white",
    border: "none",
    borderRadius: "10px",
    cursor: "pointer",
    fontSize: "1.1rem",
    fontWeight: "bold",
    transition: "transform 0.2s ease, background-color 0.2s ease",
  },
  secondaryButton: {
    padding: "15px 30px",
    backgroundColor: "#2196F3",
    color: "white",
    border: "none",
    borderRadius: "10px",
    cursor: "pointer",
    fontSize: "1.1rem",
    fontWeight: "bold",
    transition: "transform 0.2s ease, background-color 0.2s ease",
  },
  logoutButton: {
    padding: "15px 30px",
    backgroundColor: "#f44336",
    color: "white",
    border: "none",
    borderRadius: "10px",
    cursor: "pointer",
    fontSize: "1.1rem",
    fontWeight: "bold",
    transition: "transform 0.2s ease, background-color 0.2s ease",
  },
};
  
export default Dashboard;
  