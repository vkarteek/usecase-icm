import dotenv from "dotenv";
dotenv.config();

export async function createSoftwareTicketHandler({ message }) {
  const url = process.env.SOFTWARE_TICKET_API;

  const body = {
    type: message,
    status: "pending"
  };

  const res = await fetch(url, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body)
  });

  const result = await res.json();

  return {
    content: [
      {
        type: "text",
        text: `Software Ticket Created with Ticket ID: ${result.id} and Type: ${result.type}`
      }
    ]
  };
}
