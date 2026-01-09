
let contextId = null;

export async function sendMessage(userText) {
  const requestBody = {
    jsonrpc: "2.0",
    id: "1",
    method: "message/send",
    params: {
      message: {
        role: "user",
        messageId: `msg-${Date.now()}`,
        ...(contextId && { contextId }),
        parts: [
          {
            kind: "text",
            text: userText
          }
        ]
      }
    }
  };

  const res = await fetch("http://localhost:9000", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(requestBody)
  });

  const data = await res.json();
  console.log("response from api *****", data);

  // Save contextId for next message
  if (data?.result?.metadata?.context_id) {
    contextId = data.result.metadata.context_id;
  }

  return {
    sender: "bot",
    text: data?.result?.parts?.[0]?.text || ""
  };
}
