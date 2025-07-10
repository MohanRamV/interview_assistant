import React from "react";

function BackButton({ onBack, text = "⬅ Back", customStyle = {} }) {
  return (
    <button onClick={onBack} style={{...styles.button, ...customStyle}}>
      {text}
    </button>
  );
}

const styles = {
  button: {
    backgroundColor: "#333",
    color: "#fff",
    padding: "10px 16px",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    marginBottom: "20px",
  },
};

export default BackButton;
