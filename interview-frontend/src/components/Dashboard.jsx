const Dashboard = ({ userName, onStartInterview, onViewSessions, onUpload, onLogout }) => {
    return (
      <div style={{ padding: "2rem", textAlign: "center" }}>
        <h2>Hello, {userName}</h2>
        <p>What would you like to do?</p>
        <button onClick={onStartInterview} style={buttonStyle}>Start Interview</button>
        <button onClick={onViewSessions} style={{ ...buttonStyle, background: "#6c757d" }}>View Sessions</button>
        <button onClick={onUpload} style={{ ...buttonStyle, background: "#20c997" }}>Upload Resume + JD</button>
        <button onClick={onLogout} style={{ ...buttonStyle, background: "#dc3545" }}>Logout</button>
      </div>
    );
  };
  
  
  const buttonStyle = {
    margin: "0.5rem",
    padding: "12px 24px",
    background: "#0d6efd",
    color: "#fff",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
  };
  
  export default Dashboard;
  