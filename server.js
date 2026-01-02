
// Simple MCP-like HTTP server exposing tools over REST.

import express from "express";
import cors from "cors";
import bodyParser from "body-parser";
import { fileURLToPath } from "url";
import path from "path";
import { createRequire } from "module";

const require = createRequire(import.meta.url);


import * as weatherTool from "./tools/weather.js";
import * as addTool from "./tools/add.js";
import { createSoftwareTicketHandler } from "./tools/createSoftwareTicket.js";
import { fetchSoftwareTicketHandler } from "./tools/fetchSoftwareTicket.js";
import { createHardwareTicketHandler } from "./tools/createHardwareTicket.js";
import { fetchHardwareTicketHandler } from "./tools/fetchHardwareTicket.js";


const toolsRegistry = {

  create_software_ticket: {
    name: "create_software_ticket",
    description: "Use this tool ONLY for software issues. Creates a new software ticket. Required input: { message: string } where message contains the user's software problem.",
    inputSchema: {
      type: "object",
      properties: { message: { type: "string" } },
      required: ["message"]
    }
  },

  fetch_software_ticket: {
    name: "fetch_software_ticket",
    description: "Use this tool ONLY when the user wants to retrieve a SOFTWARE ticket. Input: { ticketId: string }",
    inputSchema: {
      type: "object",
      properties: { ticketId: { type: "string" } },
      required: ["ticketId"]
    }
  },

  create_hardware_ticket: {
    name: "create_hardware_ticket",
    description: "Use this tool ONLY for hardware issues such as laptop, mouse, display, keyboard, charger, etc. Creates a hardware ticket. Required input: { message: string }",
    inputSchema: {
      type: "object",
      properties: { message: { type: "string" } },
      required: ["message"]
    }
  },

  fetch_hardware_ticket: {
    name: "fetch_hardware_ticket",
    description: "Use this tool ONLY when the user wants to retrieve a HARDWARE ticket. Input: { ticketId: string }",
    inputSchema: {
      type: "object",
      properties: { ticketId: { type: "string" } },
      required: ["ticketId"]
    }
  },
  get_weather: {
    name: "get_weather",
    description: "Get current weather for a city. Args: { city: string }",
    inputSchema: {
      type: "object",
      properties: { city: { type: "string" } },
      required: ["city"],
    },
  },

  add_numbers: {
    name: "add_numbers",
    description: "Add two numbers. Args: { a: number, b: number }",
    inputSchema: {
      type: "object",
      properties: { a: { type: "number" }, b: { type: "number" } },
      required: ["a", "b"],
    },
  },
};

const handlers = {
  get_weather: async (args) => await weatherTool.getWeatherHandler(args),
  add_numbers: async (args) => await addTool.addNumbersHandler(args),
  create_software_ticket: async (args)=> await createSoftwareTicketHandler(args),
  create_hardware_ticket:async (args)=> await createHardwareTicketHandler(args),
  fetch_software_ticket:async (args)=> await fetchSoftwareTicketHandler(args),
  fetch_hardware_ticket:async (args)=> await fetchHardwareTicketHandler(args)

};


const app = express();
app.use(cors());
app.use(bodyParser.json());

// health
app.get("/health", (req, res) => {
  res.json({ status: "ok", uptime: process.uptime() });
});

// list tools
app.post("/tools/list", (req, res) => {
  const list = Object.values(toolsRegistry).map((t) => ({
    name: t.name,
    description: t.description,
    inputSchema: t.inputSchema,
  }));
  res.json({ tools: list });
});

// call tool
// POST /tools/call  { name: "get_weather", arguments: { city: "Bengaluru" } }
app.post("/tools/call", async (req, res) => {
  try {
    const { name, arguments: args = {} } = req.body || {};
    if (!name) {
      return res.status(400).json({ error: "missing tool name" });
    }
    const tool = toolsRegistry[name];
    if (!tool) {
      return res.status(404).json({ error: `Tool not found: ${name}` });
    }

    // Basic validation: ensure required params exist
    if (tool.inputSchema && Array.isArray(tool.inputSchema.required)) {
      const missing = (tool.inputSchema.required || []).filter(
        (k) => !(k in args)
      );
      if (missing.length) {
        return res.status(400).json({
          error: "missing required arguments",
          missing,
        });
      }
    }

    const handlerFn = handlers[name];
    if (!handlerFn) {
      return res.status(500).json({ error: `Handler not registered for ${name}` });
    }
    const result = await handlerFn(args);
    // const result = await tool.handler(args);
    // Standardize return: { content: [ { type: "text", text: "..." } ] }
    res.json(result);
  } catch (err) {
    console.error("tool call error:", err);
    res.status(500).json({ error: String(err) });
  }
});

const PORT = process.env.MCP || 3000;
app.listen(PORT, () => {
  console.log(`MCP-like server listening on http://0.0.0.0:${PORT}`);
  console.log("Available tools:", Object.keys(toolsRegistry).join(", "));
});
