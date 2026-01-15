import dotenv from "dotenv";
dotenv.config();

function validateMarkdown(content) {
  const errors = [];

  if (!content || content.trim().length === 0) {
    errors.push("Markdown content is empty");
  }

  if (content.length > 1000) {
    errors.push("Markdown content exceeds 1000 characters");
  }

  if (!content.includes("## Issue")) {
    errors.push('Markdown must include a "## Issue" section');
  }

  if (content.toLowerCase().includes("test")) {
    errors.push('Markdown must not contain the word "test"');
  }

  return {
    valid: errors.length === 0,
    errors
  };
}

export async function createHardwareTicketHandler({ content }) {
  // content is expected to be markdown text from .md
  const validation = validateMarkdown(content);

  if (!validation.valid) {
    return {
      content: [
        {
          type: "text",
          text: `Validation failed:\n- ${validation.errors.join("\n- ")}`
        }
      ]
    };
  }

  const url = process.env.HARDWARE_TICKET_API;

  const body = {
    type: "hardware",
    status: "pending",
    description: content
  };

  const res = await fetch(url, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body)
  });

  const result = await res.json();

  console.log("createHardwareTicket API called", res.status);
  console.log("result", result);

  return {
    content: [
      {
        type: "text",
        text: `Hardware Ticket Created with Ticket ID: ${result.id}`
      }
    ]
  };
}
