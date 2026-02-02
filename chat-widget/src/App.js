import ChatWidget from "./components/ChatWidget";
import "./index.css";

function App() {
  return (
    <div style={{ minHeight: "100vh", position: "relative" }}>
      <img
        src="/company-logo.jpg"
        alt="Company Logo"
        style={{
          width: "100%",
          height: "100vh",
          objectFit: "cover"
        }}
      />
  
      {/* Floating chat widget */}
      <div style={{ position: "absolute", bottom: 20, right: 20 }}>
        <ChatWidget />
      </div>
    </div>
  );
  
  
}

export default App;
