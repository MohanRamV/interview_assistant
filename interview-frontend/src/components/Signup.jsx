import { useState } from "react";
import BackButton from "./BackButton";

const Signup = ({ onSuccess, onBackToLogin }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const res = await fetch(`${API_URL}/auth/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (res.ok && data.message === "Signup successful") {
        onSuccess(); // Switch to login page
      } else {
        alert(data.error || "Signup failed. Please try again.");
      }
    } catch (error) {
      alert("Error connecting to server.");
      console.error(error);
    }
  };

  return (
    <div style={styles.container}>
      <BackButton onBack={onBackToLogin} />
      <div style={styles.card}>
        <h2 style={styles.title}>Create Account</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="email"
            placeholder="Email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={styles.input}
          />
          <input
            type="password"
            placeholder="Password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={styles.input}
          />
          <button type="submit" style={styles.button}>Sign Up</button>
        </form>
        <p style={styles.loginText}>
          Already have an account?{" "}
          <button onClick={onBackToLogin} style={styles.linkButton}>Sign In</button>
        </p>
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
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
  },
  card: {
    backgroundColor: "rgba(0, 0, 0, 0.6)",
    padding: "40px",
    borderRadius: "20px",
    textAlign: "center",
    maxWidth: "400px",
    width: "100%",
    boxShadow: "0 4px 20px rgba(0, 0, 0, 0.3)",
  },
  title: {
    marginBottom: "30px",
    fontSize: "2rem",
  },
  input: {
    width: "100%",
    padding: "12px",
    marginBottom: "15px",
    border: "none",
    borderRadius: "8px",
    fontSize: "1rem",
    backgroundColor: "rgba(255, 255, 255, 0.9)",
  },
  button: {
    width: "100%",
    padding: "12px 20px",
    backgroundColor: "#4CAF50",
    color: "white",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "1rem",
    fontWeight: "bold",
    marginBottom: "20px",
  },
  loginText: {
    margin: 0,
    fontSize: "1rem",
  },
  linkButton: {
    background: "none",
    border: "none",
    color: "#4CAF50",
    textDecoration: "underline",
    cursor: "pointer",
    fontSize: "1rem",
    fontWeight: "bold",
  },
};

export default Signup;
