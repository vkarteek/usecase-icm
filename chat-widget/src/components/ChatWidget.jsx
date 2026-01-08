import { useState } from "react";
import ChatPopup from "./ChatPopup";

export default function ChatWidget() {
  const [open, setOpen] = useState(false);

  return (
    <>
      {open && <ChatPopup onClose={() => setOpen(false)} />}
      <div className="chat-icon" onClick={() => setOpen(!open)}>
        💬
      </div>
    </>
  );
}
