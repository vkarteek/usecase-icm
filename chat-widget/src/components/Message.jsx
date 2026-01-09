export default function Message({ sender, text }) {
  // Split text by **bold**
  const parts = text.split(/(\*\*.*?\*\*)/g);

  return (
    <div className={`message ${sender}`}>
      {parts.map((part, index) => {
        if (part.startsWith("**") && part.endsWith("**")) {
          return (
            <strong key={index}>
              {part.slice(2, -2)}
            </strong>
          );
        }
        return <span key={index}>{part}</span>;
      })}
    </div>
  );
}
