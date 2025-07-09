import { useState } from "react";

const CompareUpload = () => {
  const [resumeFile, setResumeFile] = useState(null);
  const [jdFile, setJdFile] = useState(null);
  const [report, setReport] = useState(null);
  const API_URL = process.env.REACT_APP_API_URL;

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append("resume", resumeFile);
    formData.append("jd", jdFile);

    const res = await fetch(`${API_URL}/upload/resume-jd`, {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    setReport(data);
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h2>Upload Resume and Job Description</h2>
      <form onSubmit={handleSubmit}>
        <input type="file" accept=".pdf" onChange={(e) => setResumeFile(e.target.files[0])} required />
        <br /><br />
        <input type="file" accept=".pdf" onChange={(e) => setJdFile(e.target.files[0])} required />
        <br /><br />
        <button type="submit">Analyze</button>
      </form>

      {report && (
        <div style={{ marginTop: "2rem", border: "1px solid #ccc", padding: "1rem" }}>
          <h3>Comparison Report</h3>
          <p><strong>Matched Skills:</strong> {report.matched_skills?.join(", ")}</p>
          <p><strong>Missing Skills:</strong> {report.missing_skills?.join(", ")}</p>
          <p><strong>Summary:</strong> {report.summary}</p>
        </div>
      )}
    </div>
  );
};

export default CompareUpload;
