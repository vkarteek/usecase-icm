import { index } from "../lib/pineconeClient.js";
import { embedText } from "../lib/embeddings.js";
import { randomUUID } from "crypto";

export async function vectorStoreIncidentHandler(args) {
    try {
      const { issue, solution, domain, ticketId } = args;
  
      console.log("Vector Store Called");
      console.log({ issue, solution, domain });
      const cleanIssue = issue.toLowerCase().replace(/my type of issue is|my urgency is|my affected system is|my impact is/gi, "") .trim();

      // const vector = await embedText(cleanIssue);

  
      const vector = await embedText(
        `Issue:\n${cleanIssue}\n\nSolution:\n${solution}`
      );
  
      console.log(" Embedding created, length:", vector.length);
  
      await index.upsert([
        {
          id: ticketId || randomUUID(),
          values: vector,
          metadata: {
            domain,
            issue,
            solution,
            createdAt: new Date().toISOString(),
          },
        },
      ]);
  
      console.log(" Stored successfully in Pinecone");
  
      return {
        status: "stored",
        message: "Incident stored in vector DB",
      };
    } catch (error) {
      console.error(" Vector store failed:", error);
  
      return {
        status: "failed",
        error: "VECTOR_STORE_FAILED",
        message: error.message,
      };
    }
  }
  
