import { useEffect, useRef, useState } from "react";

export default function useVoiceInput(onFinalTranscript, onListeningStop, silenceMs = 10000) {
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);
  const silenceTimer = useRef(null);
  const accumulatedTranscript = useRef("");

  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      console.error("SpeechRecognition is not supported.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.continuous = true;

    recognition.onstart = () => {
      setIsListening(true);
      accumulatedTranscript.current = ""; // Reset accumulated transcript
      console.log("Listening started...");
    };

    recognition.onresult = (event) => {
      const transcript = event.results[event.results.length - 1][0].transcript;
      
      // Accumulate the transcript instead of overwriting
      if (accumulatedTranscript.current) {
        accumulatedTranscript.current += " " + transcript;
      } else {
        accumulatedTranscript.current = transcript;
      }
      
      // Reset silence timer after each result
      clearTimeout(silenceTimer.current);
      silenceTimer.current = setTimeout(() => {
        recognition.stop(); // Stop if user goes silent
      }, silenceMs);
    };

    recognition.onend = () => {
      setIsListening(false);
      clearTimeout(silenceTimer.current);
      console.log("Listening stopped.");
      
      // Send the complete accumulated transcript when listening stops
      if (accumulatedTranscript.current.trim()) {
        onFinalTranscript(accumulatedTranscript.current.trim());
      }
      
      // Notify parent component that listening has stopped
      if (onListeningStop) {
        onListeningStop();
      }
    };

    recognitionRef.current = recognition;
  }, [onFinalTranscript, onListeningStop, silenceMs]);

  const startListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.start();
    }
  };

  return {
    isListening,
    startListening,
  };
}
