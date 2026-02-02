import dotenv from "dotenv";
dotenv.config();

export async function createSoftwareTicketHandler({ message,solution }) {
  const url = process.env.SOFTWARE_TICKET_API;

  // const body = {
  //   type: message,
  //   status: "pending"
  // };

  const res = await fetch(process.env.SOFTWARE_TICKET_API, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      type: "software",
      status:"pending",
      description: message,
      solution: solution
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
      text: `**Software Ticket Created**
              with Ticket ID: **${result.id}**
              and Type: **${result.type}**
              mean while follow below solutions steps: ${formattedSteps}`
    }
  ]
};


  // return {
  //   content: [
  //     {
  //       type: "text",
  //       text: `Software Ticket Created with Ticket ID: ${result.id} and Type: ${result.type} mean while follow below solutions steps: ${result.solution}`
  //     }
  //   ]
  // };
}
