import React, { useState, useEffect } from "react";
import BackButton from "./BackButton";

function DataManager({ onDataReady, userEmail }) {
  const [existingData, setExistingData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploadMode, setUploadMode] = useState(false);
  const [resume, setResume] = useState(null);
  const [jd, setJd] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [regeneratingSkills, setRegeneratingSkills] = useState(false);

  useEffect(() => {
    fetchExistingData();
  }, [userEmail]);

  const fetchExistingData = async () => {
    try {
      const res = await fetch(`http://localhost:8000/user/data/${encodeURIComponent(userEmail || "")}`);
      const data = await res.json();
      
      if (data.error) {
        console.log("No existing data found:", data.error);
        setExistingData(null);
      } else {
        setExistingData(data);
      }
    } catch (err) {
      console.log("Error fetching existing data:", err);
      setExistingData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleUseExisting = async () => {
    if (!existingData) return;
    
    setLoading(true);
    try {
      // Create a new session with existing data
      const res = await fetch("http://localhost:8000/create-session-from-existing", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_email: userEmail,
          existing_data_id: existingData._id
        }),
      });
      
      const data = await res.json();
      if (data.error) {
        alert("Error creating session: " + data.error);
        return;
      }
      
      onDataReady(data.session_id);
    } catch (err) {
      console.error("Error creating session:", err);
      alert("Failed to create session. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerateSkills = async () => {
    if (!existingData?._id) return;
    setRegeneratingSkills(true);

    try {
      const res = await fetch(`http://localhost:8000/regenerate-skills/${existingData._id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });
      const data = await res.json();
    
      if (data.error) {
        console.error("Server error:", data.error);
        alert("Skills regeneration failed: " + data.error);
        return;
      }
    
      // Update the existing data with new skills
      setExistingData(prev => ({
        ...prev,
        matched_skills: data.matched_skills || [],
        missing_skills: data.missing_skills || [],
        resume_jd_summary: data.summary || ""
      }));
      
      alert("Skills analysis regenerated successfully!");
    } catch (err) {
      console.error("Fetch error:", err);
      alert("Something went wrong. Check backend console.");
    } finally {
      setRegeneratingSkills(false);
    }
  };

  const handleUpload = async () => {
    if (!resume || !jd) return;
    setUploading(true);

    const formData = new FormData();
    formData.append("resume", resume);
    formData.append("jd", jd);
    formData.append("user_email", userEmail || "");

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
    
      setUploading(false);
      onDataReady(data.session_id);
    } catch (err) {
      console.error("Fetch error:", err);
      alert("Something went wrong. Check backend console.");
      setUploading(false);
    }
  };

  if (loading) {
    return (
      <div style={styles.container}>
        <BackButton onBack={() => window.location.reload()} />
        <div style={styles.loadingContainer}>
          <h2>Loading your data...</h2>
          <p>Checking for existing resume and job description data...</p>
        </div>
      </div>
    );
  }

  if (uploadMode) {
    return (
      <div style={styles.container}>
        <BackButton onBack={() => setUploadMode(false)} />

        <h2>Upload New Resume & Job Description</h2>
        <p style={styles.subtitle}>Upload new files to replace existing data</p>

        <div style={styles.field}>
          <label>Upload Resume (PDF):</label>
          <input type="file" accept=".pdf" onChange={(e) => setResume(e.target.files[0])} />
        </div>

        <div style={styles.field}>
          <label>Upload Job Description (PDF):</label>
          <input type="file" accept=".pdf" onChange={(e) => setJd(e.target.files[0])} />
        </div>

        <button onClick={handleUpload} disabled={!resume || !jd} style={styles.uploadButton}>
          {uploading ? "Uploading..." : "Upload & Start Interview"}
        </button>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <BackButton onBack={() => window.location.reload()} />

      <h2>Resume & Job Description Data</h2>

      {existingData ? (
        <div style={styles.existingDataContainer}>
          <div style={styles.dataCard}>
            <h3>📄 Existing Data Found</h3>
            <p><strong>Resume:</strong> {existingData.resume_filename || "Parsed resume data"}</p>
            <p><strong>Job Description:</strong> {existingData.jd_filename || "Parsed JD data"}</p>
            <p><strong>Last Updated:</strong> {new Date(existingData.updated_at).toLocaleDateString()}</p>
            
            <div style={styles.skillsPreview}>
              <h4>Skills Analysis:</h4>
              <p><strong>Matched Skills:</strong> {existingData.matched_skills?.length || 0} skills</p>
              <p><strong>Missing Skills:</strong> {existingData.missing_skills?.length || 0} skills</p>
              {existingData.matched_skills?.length === 0 && existingData.missing_skills?.length === 0 && (
                <div style={styles.skillsWarning}>
                  <p style={{color: "#ff6b6b", fontSize: "14px"}}>
                    ⚠️ No skills data found. This might be from an older session.
                  </p>
                  <button 
                    onClick={handleRegenerateSkills} 
                    disabled={regeneratingSkills}
                    style={styles.regenerateButton}
                  >
                    {regeneratingSkills ? "🔄 Regenerating..." : "🔄 Regenerate Skills Analysis"}
                  </button>
                </div>
              )}
            </div>

            <div style={styles.buttonContainer}>
              <button onClick={handleUseExisting} disabled={loading} style={styles.useExistingButton}>
                {loading ? "Creating Session..." : "🚀 Use Existing Data"}
              </button>
              
              <button onClick={() => setUploadMode(true)} style={styles.updateButton}>
                📝 Update with New Files
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div style={styles.noDataContainer}>
          <div style={styles.dataCard}>
            <h3>📝 No Existing Data</h3>
            <p>This is your first time. Please upload your resume and job description to get started.</p>
            
            <button onClick={() => setUploadMode(true)} style={styles.uploadButton}>
              📤 Upload Files
            </button>
          </div>
        </div>
      )}
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
  loadingContainer: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    minHeight: "60vh",
  },
  existingDataContainer: {
    maxWidth: "600px",
    margin: "0 auto",
  },
  noDataContainer: {
    maxWidth: "500px",
    margin: "0 auto",
  },
  dataCard: {
    backgroundColor: "rgba(0, 0, 0, 0.6)",
    padding: "30px",
    borderRadius: "15px",
    marginTop: "20px",
    boxShadow: "0 4px 20px rgba(0, 0, 0, 0.3)",
  },
  skillsPreview: {
    backgroundColor: "rgba(255, 255, 255, 0.1)",
    padding: "15px",
    borderRadius: "10px",
    margin: "20px 0",
  },
  buttonContainer: {
    display: "flex",
    flexDirection: "column",
    gap: "15px",
    marginTop: "20px",
  },
  useExistingButton: {
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
  updateButton: {
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
  uploadButton: {
    padding: "15px 30px",
    backgroundColor: "#FF9800",
    color: "white",
    border: "none",
    borderRadius: "10px",
    cursor: "pointer",
    fontSize: "1.1rem",
    fontWeight: "bold",
    transition: "transform 0.2s ease, background-color 0.2s ease",
  },
  regenerateButton: {
    padding: "10px 20px",
    backgroundColor: "#9C27B0",
    color: "white",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "0.9rem",
    fontWeight: "bold",
    marginTop: "10px",
    transition: "transform 0.2s ease, background-color 0.2s ease",
  },
  skillsWarning: {
    marginTop: "10px",
    padding: "10px",
    backgroundColor: "rgba(255, 107, 107, 0.1)",
    borderRadius: "8px",
    border: "1px solid rgba(255, 107, 107, 0.3)",
  },
  field: {
    margin: "20px 0",
  },
  subtitle: {
    color: "#ccc",
    marginBottom: "30px",
  },
};

export default DataManager; 