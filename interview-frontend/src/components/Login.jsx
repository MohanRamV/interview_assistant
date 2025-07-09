import { useState } from "react";

const Login = ({ onLogin, onSignupClick }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const API_URL = process.env.REACT_APP_API_URL;

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const res = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (res.ok && data.message === "Login successful") {
        onLogin(email); // Go to dashboard
      } else {
        alert(data.error || "Login failed. Please try again.");
      }
    } catch (error) {
      alert("Error connecting to the server.");
      console.error(error);
    }
  };

  return (
    <div style={{ padding: "2rem", maxWidth: "400px", margin: "auto", textAlign: "center" }}>
      <h2>Sign In</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={inputStyle}
        />
        <input
          type="password"
          placeholder="Password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={inputStyle}
        />
        <button type="submit" style={buttonStyle}>Login</button>
      </form>
      <p style={{ marginTop: "1rem" }}>
        Don’t have an account?{" "}
        <button onClick={onSignupClick} style={linkButton}>Sign Up</button>
      </p>
    </div>
  );
};

const inputStyle = {
  width: "100%",
  padding: "10px",
  marginBottom: "1rem",
  border: "1px solid #ccc",
  borderRadius: "5px",
};

const buttonStyle = {
  padding: "10px 20px",
  backgroundColor: "#0d6efd",
  color: "#fff",
  border: "none",
  borderRadius: "5px",
  cursor: "pointer",
};

const linkButton = {
  background: "none",
  border: "none",
  color: "#0d6efd",
  textDecoration: "underline",
  cursor: "pointer",
};

export default Login;
