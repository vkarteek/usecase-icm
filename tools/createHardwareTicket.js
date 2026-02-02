import dotenv from "dotenv";
dotenv.config();

export async function createHardwareTicketHandler({ message,solution }) {
  const url = process.env.HARDWARE_TICKET_API;

  // const body = {
  //   type: message,
  //   status: "pending"
  // };

  const res = await fetch(url, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      type: "hardware",
      description: message,
      solution: solution,
      status:"pending"
    }),
  });

  const result = await res.json();
  const steps = result.solution
  .split(/\d+\.\s*/).filter(Boolean);

const formattedSteps = steps
  .map((step, i) => `${i + 1}. ${step.trim()}`)
  .join("\n");

  return {
    content: [
      {
        type: "text",
        text: `**Hardware Ticket Created**
        with Ticket ID: **${result.id}**
        and Type: **${result.type}**
        mean while follow below solutions steps: ${formattedSteps}`
      }
    ]
  };
}

