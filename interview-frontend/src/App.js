import { useState } from "react";
import Login from "./components/Login";
import Signup from "./components/Signup";
import Dashboard from "./components/Dashboard";
import InterviewChat from "./components/InterviewChat";
import InterviewSummary from "./components/InterviewSummary";
import SessionList from "./components/SessionList";
import CompareUpload from "./components/CompareUpload";

function App() {
  const [userEmail, setUserEmail] = useState(null);
  const [authPage, setAuthPage] = useState("login"); // "login" or "signup"
  const [page, setPage] = useState("auth");          // "auth", "dashboard", "interview", "summary", "sessions"
  const [sessionId, setSessionId] = useState(null);

  const handleLogin = (email) => {
    setUserEmail(email);
    setPage("dashboard");
  };

  const handleLogout = () => {
    setUserEmail(null);
    setSessionId(null);
    setPage("auth");
    setAuthPage("login");
  };

  return (
    <div style={{ fontFamily: "Arial, sans-serif" }}>
      {page === "auth" && authPage === "login" && (
        <Login
          onLogin={handleLogin}
          onSignupClick={() => setAuthPage("signup")}
        />
      )}

      {page === "auth" && authPage === "signup" && (
        <Signup onSuccess={() => setAuthPage("login")} />
      )}

      {page === "dashboard" && (
        <Dashboard
          userName={userEmail}
          onStartInterview={() => setPage("interview")}
          onViewSessions={() => setPage("sessions")}
          onUpload={() => setPage("upload")} // add this
          onLogout={handleLogout}
        />
      )}

      {page === "upload" && <CompareUpload />}


      {page === "interview" && (
        <InterviewChat
          setSessionId={setSessionId}
          onComplete={() => setPage("summary")}
        />
      )}

      {page === "summary" && (
        <InterviewSummary sessionId={sessionId} />
      )}

      {page === "sessions" && (
        <SessionList userEmail={userEmail} onBack={() => setPage("dashboard")} />
      )}

    </div>
  );
}

export default App;
