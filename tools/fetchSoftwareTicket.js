import dotenv from "dotenv";
dotenv.config();

export async function fetchSoftwareTicketHandler({ ticketId }) {
  const url = `${process.env.SOFTWARE_TICKET_API}/${ticketId}`;

  const res = await fetch(url);
  if (!res.ok) {
    return {
      content: [{ type: "text", text: "Software ticket not found." }]
    };
  }

  const ticket = await res.json();

  return {
    content: [
      {
        type: "text",
        text: `Software Ticket Details:TicketID: ${ticket.id} Type: ${ticket.type} Status: ${ticket.status}`
      }
    ]
  };
}
