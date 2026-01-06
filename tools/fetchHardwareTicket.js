import dotenv from "dotenv";
dotenv.config();
import fs from 'fs';

export async function fetchHardwareTicketHandler({ ticketId }) {
  const url = `${process.env.HARDWARE_TICKET_API}/${ticketId}`;

  // Use local data when API is down
  // const data = JSON.parse(fs.readFileSync('./tools/data.json', 'utf8'));
  // const ticket = data.find(t => t.id === ticketId);
  
  // Call the mock hardware API
  const res = await fetch(url);

  if (!res.ok) {
    return {
      content: [
        {
          type: "text",
          text: `Hardware ticket not found with ID ${ticketId}.`
        }
      ]
    };
  }

  const ticket = await res.json(); 

  return {
    content: [
      {
        type: "text",
        text: `Hardware Ticket Details: TicketID: ${ticket.id} Type: ${ticket.type} Status: ${ticket.status}`
      }
    ]
  };
}
