import dotenv from "dotenv";
dotenv.config();

export async function createHardwareTicketHandler({ message }) {
  const url = process.env.HARDWARE_TICKET_API;

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
  console.log("createHradwareTicket mockAPI called *******",res);
  console.log("result from",result);

  return {
    content: [
      {
        type: "text",
        text: `Hardware Ticket Created with Ticket ID: ${result.id} and Type: ${result.type}`
      }
    ]
  };
}
