import { useState } from "react";
import Login from "./components/Login";
import Signup from "./components/Signup";
import Dashboard from "./components/Dashboard";
import InterviewChat from "./components/InterviewChat";
import SessionList from "./components/SessionList";
import LandingPage from "./components/LandingPage";
import InterviewSummary from "./components/InterviewSummary";
import DataManager from "./components/DataManager";



function App() {
  
  const [userEmail, setUserEmail] = useState(() => {
    // Try to restore user email from localStorage
    const saved = localStorage.getItem('userEmail');
    return saved || null;
  });
  const [authPage, setAuthPage] = useState("login"); // "login" or "signup"
  const [page, setPage] = useState(() => {
    // If user is logged in, start at dashboard, otherwise at landing
    const saved = localStorage.getItem('userEmail');
    return saved ? "dashboard" : "landing";
  });
  const [sessionId, setSessionId] = useState(null);

  const handleLogin = (email) => {
    console.log("User logging in:", email);
    setUserEmail(email);
    localStorage.setItem('userEmail', email);
    setPage("dashboard");
  };

  const handleLogout = () => {
    console.log("Logging out user:", userEmail);
    setUserEmail(null);
    localStorage.removeItem('userEmail');
    setSessionId(null);
    setPage("auth");
    setAuthPage("login");
  };

  console.log("App render - page:", page, "userEmail:", userEmail, "sessionId:", sessionId);
  
  return (
    <div style={{ fontFamily: "Arial, sans-serif" }}>
      {page === "landing" && (
        <LandingPage onLoginClick={() => setPage("auth")} />
      )}
      {page === "auth" && authPage === "login" && (
        <Login
          onLogin={handleLogin}
          onSignupClick={() => setAuthPage("signup")}
        />
      )}

      {page === "auth" && authPage === "signup" && (
        <Signup 
          onSuccess={() => setAuthPage("login")} 
          onBackToLogin={() => setAuthPage("login")}
        />
      )}

      {page === "dashboard" && (
        <Dashboard
          userName={userEmail}
          onStartInterview={() => setPage("upload")}
          onViewSessions={() => setPage("sessions")}
          onUpload={() => setPage("upload")} // add this
          onLogout={handleLogout}
        />
      )}
      {page === "upload" && (
          <DataManager
            userEmail={userEmail}
            onDataReady={(sid) => {
              setSessionId(sid);
              setPage("interview");
            }}
          />
        )}
        




      {page === "interview" && (
        <InterviewChat
          sessionId={sessionId}
          onComplete={() => setPage("summary")}
        />
      )}

      {page === "summary" && (
        <InterviewSummary 
          sessionId={sessionId} 
          userEmail={userEmail}
          onBackToDashboard={() => {
            console.log("Back to dashboard clicked, userEmail:", userEmail);
            setPage("dashboard");
          }}
        />
      )}

      {page === "sessions" && (
        <SessionList userEmail={userEmail} onBack={() => setPage("dashboard")} />
      )}

    </div>
  );
}

export default App;
