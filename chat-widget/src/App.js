import ChatWidget from "./components/ChatWidget";
import "./index.css";

function App() {
  return (
    <div style={{ minHeight: "100vh" }}>
      <h1 style={{ padding: "20px" }}>My Bot</h1>

      {/* Chat icon will appear bottom-right */}
      <ChatWidget />
    </div>
  );
}

export default App;
