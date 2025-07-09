import { useEffect, useState } from "react";

const InterviewChat = ({ setSessionId, onComplete }) => {
  const [messages, setMessages] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState("");
  const [recording, setRecording] = useState(false);
  const [sessionIdLocal, setSessionIdLocal] = useState(null);

  const API_URL = process.env.REACT_APP_API_URL;

  //  Voice input
  const startVoiceInput = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Your browser does not support voice input.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.onresult = (event) => {
      const text = event.results[0][0].transcript;
      handleAnswer(text);
    };
    recognition.onerror = (event) => {
      alert("Voice recognition error: " + event.error);
    };
    recognition.onend = () => setRecording(false);
    recognition.start();
    setRecording(true);
  };

  //  Voice output
  const speak = (text) => {
    const utter = new SpeechSynthesisUtterance(text);
    speechSynthesis.speak(utter);
  };

  //  Send answer to backend and get next question
  const handleAnswer = async (answer) => {
    const updated = [...messages, { type: "candidate", text: answer }];
    setMessages(updated);

    const res = await fetch(`${API_URL}/interview/next`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answer, session_id: sessionIdLocal }),
    });

    const data = await res.json();

    if (data.question.toLowerCase().includes("thanks for completing")) {
      onComplete();  //  notify App to show summary
    }

    setCurrentQuestion(data.question);
    setMessages([
      ...updated,
      { type: "ai", text: data.question },
      ...(data.feedback ? [{ type: "feedback", text: data.feedback }] : []),
    ]);

    speak(data.question);
  };

  //  Start interview on load
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    const begin = async () => {
      const res = await fetch(`${API_URL}/interview/start`, { method: "POST" });
      const data = await res.json();

      const firstQ = data.question;
      const sid = data.session_id;

      setSessionIdLocal(sid);
      setSessionId(sid);


      setMessages([{ type: "ai", text: data.intro }, { type: "ai", text: firstQ }]);
      setCurrentQuestion(firstQ);
      speak(firstQ);
    };

    begin();
  }, [API_URL, setSessionId]);

  return (
    <div style={{ padding: "2rem", maxWidth: "700px", margin: "auto" }}>
      <h2>AI Interview Assistant</h2>
      {currentQuestion && (
          <div style={{
            margin: "1rem 0",
            padding: "1rem",
            backgroundColor: "#f0f8ff",
            border: "1px solid #0d6efd",
            borderRadius: "6px",
            fontWeight: "bold"
          }}>
            Current Question: {currentQuestion}
          </div>
        )}

      <div style={{
        height: "400px",
        overflowY: "auto",
        border: "1px solid #ccc",
        padding: "1rem",
        borderRadius: "6px",
        marginBottom: "1rem",
        backgroundColor: "#f9f9f9"
      }}>
        {messages.map((msg, idx) => (
          <div key={idx} style={{ marginBottom: "1rem", color: msg.type === "candidate" ? "#198754" : msg.type === "feedback" ? "#6c757d" : "#0d6efd" }}>
            <strong>{msg.type === "candidate" ? "You" : msg.type === "feedback" ? "Coach" : "Agent"}:</strong> {msg.text}
          </div>
        ))}
      </div>

      <button
        onClick={startVoiceInput}
        style={{
          padding: "10px 20px",
          backgroundColor: recording ? "#6c757d" : "#0d6efd",
          color: "white",
          border: "none",
          borderRadius: "5px"
        }}
      >
        {recording ? "Listening..." : "Speak Answer "}
      </button>
    </div>
  );
};

export default InterviewChat;
