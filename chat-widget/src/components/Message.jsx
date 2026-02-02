export default function Message({ sender, text, options, onOptionClick }) {
  const parts = text?.split(/(\*\*.*?\*\*)/g) || [];

  return (
    <div className={`message-wrapper ${sender}`}>
      {/* Sender label */}
      <div className="sender-label">
        {sender === "user" ? "USER" : "BOT"}
      </div>

      {/* Message bubble */}
      {/* <div className={`message ${sender}`}> */}
      <div className={`message ${sender}`} style={{ whiteSpace: "pre-line" }}>

        {parts.map((part, index) => {
          if (part.startsWith("**") && part.endsWith("**")) {
            return <strong key={index}>{part.slice(2, -2)}</strong>;
          }
          return <span key={index}>{part}</span>;
        })}

        {/* Buttons (ONLY for bot welcome message) */}
        {sender === "bot" && options && (
          <div className="option-buttons">
            {options.map((opt, i) => (
              <button
                key={i}
                className="option-btn"
                onClick={() => onOptionClick(opt.value)}
              >
                {opt.label}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
