import React from "react";
import logo from "../assets/logo.png"; 

function LandingPage({ onLoginClick }) {
  return (
    <div style={styles.container}>
      <div style={styles.card}>
        {/* Logo Image */}
        <img src={logo} alt="AI Interview Agent" style={styles.logoImage} />

        {/* Intro Text */}
        <h2 style={styles.title}>AI Interview Agent</h2>
        <p style={styles.intro}>
          Welcome to your personalized AI Interview experience.
          Upload your resume, simulate dynamic interviews, and get instant feedback – powered by AI.
        </p>

        {/* Login Button */}
        <button style={styles.button} onClick={onLoginClick}>
          Login to Begin
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: {
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    height: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    fontFamily: "Segoe UI, sans-serif",
  },
  card: {
    backgroundColor: "rgba(0, 0, 0, 0.6)",
    padding: "40px",
    borderRadius: "20px",
    textAlign: "center",
    maxWidth: "500px",
    color: "white",
    boxShadow: "0 4px 20px rgba(0, 0, 0, 0.3)",
  },
  logoImage: {
    width: "120px",
    height: "auto",
    marginBottom: "20px",
  },
  title: {
    fontSize: "1.8rem",
    marginBottom: "10px",
  },
  intro: {
    fontSize: "1.1rem",
    marginBottom: "30px",
  },
  button: {
    backgroundColor: "#61dafb",
    border: "none",
    padding: "12px 24px",
    fontSize: "1rem",
    fontWeight: "bold",
    borderRadius: "8px",
    cursor: "pointer",
    color: "#000",
  },
};

export default LandingPage;
