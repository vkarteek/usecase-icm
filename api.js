// api.js
import express from "express";
import cors from "cors";
import bodyParser from "body-parser";
import dotenv from "dotenv";
import fetch from "node-fetch";
import OpenAI from "openai";
import path from "path";
import { fileURLToPath } from "url";

dotenv.config();

const PORT = process.env.PORT || 4000;
const SERVER_URL = process.env.MCP_SERVER_URL;
const OPENAI_KEY = process.env.OPENAI_API_KEY;

const openai = new OpenAI({ apiKey: OPENAI_KEY });

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();   

app.use(cors());
app.use(bodyParser.json());

// Serve frontend folder (this works for frontend.html)
app.use(express.static(__dirname));

async function callMcpTool(name, args) {
  const res = await fetch(`${SERVER_URL}/tools/call`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ name, arguments: args })
  });
  return res.json();
}

async function getMcpTools() {
  const res = await fetch(`${SERVER_URL}/tools/list`, {
    method: "POST",
    headers: { "content-type": "application/json" }
  });
  return res.json();
}
app.post("/ask", async (req, res) => {
    const userMessage = req.body.question;
  
    try {
      console.log("USER QUESTION:", userMessage);
  
      //  Load MCP tools for LLM
      const toolList = await getMcpTools();
  
      const tools = toolList.tools.map(t => ({
        type: "function",
        function: {
          name: t.name,
          description: t.description,
          parameters: t.inputSchema,
        }
      }));
  
      console.log("\nTOOLS SENT TO LLM:", tools.map(t => t.function.name));
  
      // First LLM call → ask model whether it needs a tool
      const step1 = await openai.chat.completions.create({
        model: "gpt-4o",
        messages: [{ role: "user", content: userMessage }],
        tools,
        tool_choice: "auto",
      });
  
      const assistant = step1.choices?.[0]?.message;
  
      // NO TOOL SELECTED → Return LLM answer directly
      if (!assistant || !assistant.tool_calls) {
        console.log("\nLLM DID NOT REQUEST ANY TOOL.");
        console.log("DEFAULT LLM ANSWER:", assistant?.content);
  
        return res.json({
          answer: assistant?.content || "I'm sorry, I couldn't understand your question."
        });
      }
  
      // 4TOOL SELECTED → run tool
      const toolCall = assistant.tool_calls[0];
      const toolName = toolCall.function.name;
  
      console.log("\nLLM SELECTED TOOL:", toolName);
  
      let args = {};
      try {
        args = JSON.parse(toolCall.function.arguments || "{}");
      } catch {
        console.log("Invalid tool arguments from LLM.");
      }
  
      const toolOutput = await callMcpTool(toolName, args);
  
      //  Send tool output back to LLM for final reasoning
      const step2 = await openai.chat.completions.create({
        model: "gpt-4o",
        messages: [
          {
            role: "system",
            content: `
      IMPORTANT RULES FOR TICKET SYSTEM:
      
      1) FOR TICKET CREATION (POST tools like create_software_ticket, create_hardware_ticket):
         - ALWAYS say: "Please keep your ticket ID safely for future reference."
         - Clearly show the Ticket ID returned by the tool.
         - Provide a friendly confirmation message.
      
      2) FOR TICKET STATUS / FETCH (GET tools like fetch_software_ticket, fetch_hardware_ticket):
         - Show the ticket ID, type, and current status.
         - If status is "completed":
             - Also explain: "This ticket was resolved by the assigned team. If you need further help, please raise a new ticket."
         - If status is NOT "completed":
             - Do NOT include the resolution line.
      
      3) NEVER ask the user unnecessary questions after the tool returns data.
      4) ALWAYS respond in a clear and human-friendly message.
      `
          },
      
          
          { role: "user", content: userMessage },
          assistant,
          {
            role: "tool",
            tool_call_id: toolCall.id,
            content: JSON.stringify(toolOutput)
          }
        ],

      });
  
      const finalAnswer = step2.choices[0].message.content;
  
      console.log("\nFINAL LLM ANSWER:", finalAnswer);
  
      res.json({ answer: finalAnswer });
  
    } catch (err) {
      console.error("ERROR:", err);
      res.status(500).json({ error: String(err) });
    }
  });
  
app.listen(PORT, () => console.log(`API server running on http://localhost:${PORT}`));
