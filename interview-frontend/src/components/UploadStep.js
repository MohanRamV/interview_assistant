import React, { useState } from "react";
import BackButton from "./BackButton";

function UploadStep({ onUploadComplete, userEmail }) {
  const [resume, setResume] = useState(null);
  const [jd, setJd] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!resume || !jd) return;
    setLoading(true);

    const formData = new FormData();
    formData.append("resume", resume);
    formData.append("jd", jd);
    formData.append("user_email", userEmail || ""); // Add user email to form

    try {
      const res = await fetch("http://localhost:8000/upload/resume-jd", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
    
      if (data.error) {
        console.error("Server error:", data.error);
        alert("Upload failed: " + data.error);
        return;
      }
    
      setLoading(false);
      onUploadComplete(data.session_id);
    } catch (err) {
      console.error("Fetch error:", err);
      alert("Something went wrong. Check backend console.");
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <BackButton onBack={() => window.location.reload()} />

      <h2>Upload Resume & Job Description</h2>

      <div style={styles.field}>
        <label>Upload Resume (PDF):</label>
        <input type="file" accept=".pdf" onChange={(e) => setResume(e.target.files[0])} />
      </div>

      <div style={styles.field}>
        <label>Upload Job Description (PDF):</label>
        <input type="file" accept=".pdf" onChange={(e) => setJd(e.target.files[0])} />
      </div>

      <button onClick={handleUpload} disabled={!resume || !jd}>
        {loading ? "Uploading..." : "Start Interview"}
      </button>
    </div>
  );
}

const styles = {
  container: {
    padding: "30px",
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    color: "white",
    minHeight: "100vh",
    textAlign: "center",
  },
  field: {
    margin: "20px 0",
  },
};

export default UploadStep;
