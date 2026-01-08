import { useState } from "react";

export default function ChatInput({ onSend }) {
  const [text, setText] = useState("");

  const send = () => {
    if (!text.trim()) return;
    onSend(text);
    setText("");
  };

  return (
    <div className="chat-input">
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && send()}
        placeholder="Type a message..."
      />
      <button onClick={send}>Send</button>
    </div>
  );
}
