import { useState } from "react";
import ChatInput from "./ChatInput";
import Message from "./Message";
import { sendMessage } from "../services/chatApi";

export default function ChatPopup({ onClose }) {
  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "Welcome to Incident Management. I can help you with the below services:",
      options: [
        { label: "Create Ticket", value: "create ticket" },
        { label: "Fetch Ticket Status", value: "fetch ticket status" }
      ]
    }
  ]);
  
  const handleSend = async (text) => {
    const userMsg = { sender: "user", text };
    setMessages((prev) => [...prev, userMsg]);
  
    const botReply = await sendMessage(text);
    setMessages((prev) => [...prev, botReply]);
  };
  

  // const handleSend = async (text) => {
  //   const userMsg = { sender: "user", text };
  //   setMessages((prev) => [...prev, userMsg]);

  //   const botReply = await sendMessage(text);
  //   setMessages((prev) => [...prev, botReply]);
  // };

  return (
    <div className="chat-popup">
      <div className="chat-header">
        Chat Support
        <span onClick={onClose}>✖</span>
      </div>

      <div className="chat-body">
      {messages.map((m, i) => (
  <Message
    key={i}
    {...m}
    onOptionClick={handleSend}
  />
))}

      </div>

      <ChatInput onSend={handleSend} />
    </div>
  );
}
