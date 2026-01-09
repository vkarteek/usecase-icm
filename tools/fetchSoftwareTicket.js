import dotenv from "dotenv";
dotenv.config();
import fs from 'fs';

export async function fetchSoftwareTicketHandler({ ticketId }) {
  const url = `${process.env.SOFTWARE_TICKET_API}/${ticketId}`;

  // Use local data when API is down
  // const data = JSON.parse(fs.readFileSync('./tools/data.json', 'utf8'));
  // const ticket = data.find(t => t.id === ticketId);

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
