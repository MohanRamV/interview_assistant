import React, { useState, useEffect, useRef, useCallback } from "react";
import useVoiceInput from "../hooks/useVoiceInput";
import BackButton from "./BackButton";

function InterviewChat({ sessionId, onComplete }) {
  console.log("InterviewChat component rendered with sessionId:", sessionId);

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [questionIndex, setQuestionIndex] = useState(0);
  const [isSessionStarted, setIsSessionStarted] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showWarning, setShowWarning] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [greeting, setGreeting] = useState("");
  const [isVoiceActive, setIsVoiceActive] = useState(false);
  const [tabSwitchCount, setTabSwitchCount] = useState(0);
  const [interviewStartTime, setInterviewStartTime] = useState(null);
  const [fullscreenUsed, setFullscreenUsed] = useState(false);
  const hasSpokenFirst = useRef(false);

  const handleVoiceInput = useCallback((spokenText) => {
    console.log("Voice input received:", spokenText);
    if (isVoiceActive) {
      // Append to existing text when voice is active
      setAnswer(prev => prev ? prev + " " + spokenText : spokenText);
    } else {
      // Replace text when starting new voice input
      setAnswer(spokenText);
    }
  }, [isVoiceActive]);

  const handleListeningStop = useCallback(() => {
    setIsVoiceActive(false);
  }, []);

  const { isListening, startListening } = useVoiceInput(handleVoiceInput, handleListeningStop, 10000);

  const handleStartListening = () => {
    if (!isVoiceActive) {
      setIsVoiceActive(true);
    }
    startListening();
  };

  // Browser lock functionality
  const handleBeforeUnload = useCallback((e) => {
    if (isSessionStarted) {
      e.preventDefault();
      e.returnValue = "Are you sure you want to leave? Your interview progress will be lost.";
      return "Are you sure you want to leave? Your interview progress will be lost.";
    }
  }, [isSessionStarted]);

  const handleVisibilityChange = useCallback(() => {
    if (document.hidden && isSessionStarted) {
      setShowWarning(true);
      setTabSwitchCount(prev => prev + 1);
      // Report tab switching
      console.log("User switched tabs during interview");
      
      // Send tab switch data to backend
      fetch("http://localhost:8000/interview/tab-switch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          session_id: sessionId,
          tab_switch_count: tabSwitchCount + 1
        }),
      }).catch(error => console.error("Failed to log tab switch:", error));
    }
  }, [isSessionStarted, sessionId, tabSwitchCount]);

  const requestFullscreen = () => {
    if (document.documentElement.requestFullscreen) {
      document.documentElement.requestFullscreen();
    } else if (document.documentElement.webkitRequestFullscreen) {
      document.documentElement.webkitRequestFullscreen();
    } else if (document.documentElement.msRequestFullscreen) {
      document.documentElement.msRequestFullscreen();
    }
  };

  const exitFullscreen = () => {
    if (document.exitFullscreen) {
      document.exitFullscreen();
    } else if (document.webkitExitFullscreen) {
      document.webkitExitFullscreen();
    } else if (document.msExitFullscreen) {
      document.msExitFullscreen();
    }
  };

  const handleFullscreenChange = useCallback(() => {
    const isCurrentlyFullscreen = !!document.fullscreenElement;
    setIsFullscreen(isCurrentlyFullscreen);
    if (isCurrentlyFullscreen) {
      setFullscreenUsed(true);
    }
  }, []);

  // Set up event listeners
  useEffect(() => {
    window.addEventListener('beforeunload', handleBeforeUnload);
    document.addEventListener('visibilitychange', handleVisibilityChange);
    document.addEventListener('fullscreenchange', handleFullscreenChange);
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
    document.addEventListener('mozfullscreenchange', handleFullscreenChange);
    document.addEventListener('MSFullscreenChange', handleFullscreenChange);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
      document.removeEventListener('webkitfullscreenchange', handleFullscreenChange);
      document.removeEventListener('mozfullscreenchange', handleFullscreenChange);
      document.removeEventListener('MSFullscreenChange', handleFullscreenChange);
    };
  }, [handleBeforeUnload, handleVisibilityChange, handleFullscreenChange]);

  useEffect(() => {
    console.log("InterviewChat useEffect triggered - sessionId:", sessionId, "isSessionStarted:", isSessionStarted);
    
    async function startSession() {
      if (isSessionStarted) return; // Prevent multiple session starts
      
      console.log("Starting session with ID:", sessionId);
      try {
        setIsSessionStarted(true);
        setInterviewStartTime(Date.now()); // Record start time
        const res = await fetch("http://localhost:8000/interview/start", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ session_id: sessionId }),
        });
  
        const data = await res.json();
        console.log("Received first question:", data.question);
        setQuestion(data.question);
        setGreeting(data.greeting || "Welcome to your interview!");
        // Speak the greeting first, then the question
        speakText(data.greeting || "Welcome to your interview!");
        setTimeout(() => speakText(data.question), 3000); // Wait 3 seconds after greeting
      } catch (error) {
        console.error("startSession error:", error);
        setIsSessionStarted(false); // Reset on error so user can retry
      }
    }
  
    if (sessionId && !isSessionStarted) startSession();
  }, [sessionId, isSessionStarted]);

  // Add cleanup effect to detect unmounting
  useEffect(() => {
    return () => {
      console.log("InterviewChat component unmounting");
    };
  }, []);
  

  const speakText = (text) => {
    // Stop any ongoing speech before starting new one
    window.speechSynthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US";
    utterance.rate = 1; // Moderate pace
    utterance.pitch = 1;
    window.speechSynthesis.speak(utterance);
  };

  const handleNext = async () => {
    if (!answer.trim()) return; // Prevent submission of empty answers
    
    try {
      setIsLoading(true);
      
      // Create a timeout promise
      const timeoutPromise = new Promise((_, reject) =>
        setTimeout(() => reject(new Error('Request timeout')), 60000) // 60 second timeout
      );
      
      const fetchPromise = fetch("http://localhost:8000/interview/next", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          answer: answer,
        }),
      });

      const res = await Promise.race([fetchPromise, timeoutPromise]);
      const data = await res.json();
      setAnswer("");
      setQuestionIndex((prev) => prev + 1);

      if (!data.question || data.question.trim() === "") {
        // Interview completed - send security metrics
        const interviewDuration = interviewStartTime ? Math.round((Date.now() - interviewStartTime) / 60000) : 0;
        
        fetch("http://localhost:8000/interview/security-metrics", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            session_id: sessionId,
            tab_switch_count: tabSwitchCount,
            fullscreen_used: fullscreenUsed,
            interview_duration_minutes: interviewDuration
          }),
        }).catch(error => console.error("Failed to send security metrics:", error));
        
        onComplete(); // move to summary screen
      } else {
        setQuestion(data.question);
        // Reduced delay for faster response
        setTimeout(() => speakText(data.question), 50);
      }
    } catch (error) {
      console.error("handleNext error:", error);
      if (error.message === 'Request timeout') {
        alert('Request timed out. Please try again. The system is generating your next question.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const dismissWarning = () => {
    setShowWarning(false);
  };

  return (
    <div style={styles.container}>
      {showWarning && (
        <div style={styles.warningOverlay}>
          <div style={styles.warningModal}>
            <h3>⚠️ Interview Security Warning</h3>
            <p>You switched away from the interview screen. This may be reported.</p>
            <p>Please stay on this page during your interview.</p>
            <button onClick={dismissWarning} style={styles.warningButton}>
              I Understand
            </button>
          </div>
        </div>
      )}

      <div style={styles.card}>
        <div style={styles.header}>
          <BackButton 
            onBack={() => window.location.reload()} 
            text="Stop" 
            customStyle={styles.stopButton}
          />
          <div style={styles.securityControls}>
            <button 
              onClick={isFullscreen ? exitFullscreen : requestFullscreen}
              style={styles.fullscreenButton}
            >
              {isFullscreen ? "🖥️ Exit Fullscreen" : "🖥️ Enter Fullscreen"}
            </button>
          </div>
        </div>

        <div style={styles.securityNotice}>
          <p>🔒 Interview Mode Active - Please do not switch tabs or close this window</p>
        </div>

        {greeting && (
          <div style={styles.greetingBox}>
            <p style={styles.greetingText}>{greeting}</p>
          </div>
        )}

        <h2>Interview Question {questionIndex + 1}</h2>
        <p style={styles.questionText}>{question}</p>

        <textarea
          style={styles.textarea}
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          placeholder="Type your answer or use the mic"
        />

        <div style={styles.buttonRow}>
          <button onClick={handleStartListening} disabled={isLoading}>
            {isListening ? "Listening..." : "Speak"}
          </button>
          <button onClick={handleNext} disabled={!answer.trim() || isLoading}>
            {isLoading ? "⏳ Processing..." : "Submit Answer"}
          </button>
        </div>
        
        {isLoading && (
          <div style={styles.loadingIndicator}>
            <p>⏳ Generating next question...</p>
            <p style={styles.loadingSubtext}>This may take up to 60 seconds. Please wait.</p>
            <p style={styles.loadingSubtext}>If rate limited, system will automatically retry with different models.</p>
          </div>
        )}
      </div>
    </div>
  );
}

const styles = {
  container: {
    padding: "20px",
    fontFamily: "Segoe UI, sans-serif",
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    color: "white",
    minHeight: "100vh",
  },
  card: {
    backgroundColor: "rgba(0, 0, 0, 0.6)",
    padding: "30px",
    borderRadius: "15px",
    maxWidth: "600px",
    margin: "auto",
    boxShadow: "0 0 20px rgba(0,0,0,0.3)",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "15px",
  },
  securityControls: {
    display: "flex",
    gap: "10px",
  },
  fullscreenButton: {
    backgroundColor: "#4CAF50",
    color: "white",
    padding: "8px 12px",
    borderRadius: "8px",
    border: "none",
    cursor: "pointer",
    fontSize: "0.9rem",
    fontWeight: "bold",
    transition: "background-color 0.3s ease",
  },
  securityNotice: {
    backgroundColor: "#ff6b6b",
    color: "white",
    padding: "10px",
    borderRadius: "8px",
    marginBottom: "15px",
    textAlign: "center",
    fontWeight: "bold",
    opacity: 0.9,
  },
  questionText: {
    fontSize: "1.1rem",
    marginBottom: "10px",
  },
  textarea: {
    width: "100%",
    height: "100px",
    marginTop: "10px",
    padding: "10px",
    fontSize: "1rem",
    borderRadius: "8px",
    border: "none",
    resize: "none",
  },
  buttonRow: {
    marginTop: "15px",
    display: "flex",
    gap: "10px",
  },
  warningOverlay: {
    position: "fixed",
    top: 0,
    left: 0,
    width: "100%",
    height: "100%",
    background: "rgba(0,0,0,0.7)",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    zIndex: 1000,
  },
  warningModal: {
    backgroundColor: "white",
    padding: "30px",
    borderRadius: "15px",
    textAlign: "center",
    boxShadow: "0 0 20px rgba(0,0,0,0.3)",
    color: "#333", // Dark text color for better readability
  },
  warningButton: {
    backgroundColor: "#4CAF50",
    color: "white",
    padding: "10px 20px",
    borderRadius: "8px",
    border: "none",
    cursor: "pointer",
    fontSize: "1rem",
    fontWeight: "bold",
    marginTop: "20px",
  },
  loadingIndicator: {
    marginTop: "15px",
    textAlign: "center",
    color: "white",
    fontSize: "1rem",
  },
  loadingSubtext: {
    fontSize: "0.9rem",
    opacity: 0.8,
    marginTop: "5px",
  },
  greetingBox: {
    backgroundColor: "rgba(255, 255, 255, 0.2)",
    padding: "15px",
    borderRadius: "10px",
    marginBottom: "15px",
    textAlign: "center",
  },
  greetingText: {
    fontSize: "1.2rem",
    color: "white",
    fontWeight: "bold",
  },
  stopButton: {
    backgroundColor: "#ff4444", // A distinct color for the Stop button
    color: "white",
    padding: "8px 12px",
    borderRadius: "8px",
    border: "none",
    cursor: "pointer",
    fontSize: "0.9rem",
    fontWeight: "bold",
    transition: "background-color 0.3s ease",
  },
};

export default InterviewChat;
