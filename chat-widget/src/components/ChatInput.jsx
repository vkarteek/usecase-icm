import { useState } from "react";
import VoiceInput from "./VoiceInput";

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
        placeholder="Type or speak your message..."
      />

      <VoiceInput
        onResult={(spokenText) =>
          setText((prev) => (prev ? prev + " " + spokenText : spokenText))
        }
      />
      <button
        onClick={send}
        disabled={!text.trim()}
        className="send-btn"
        title="Send">
        ➤
      </button>
    </div>
  );
}
