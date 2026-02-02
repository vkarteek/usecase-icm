import { index } from "../lib/pineconeClient.js";
import { embedText } from "../lib/embeddings.js";

export async function vectorSearchIncidentHandler(args) {
  const { query, domain, topK = 3 } = args;

  const vector = await embedText(query);

  const result = await index.query({
    vector,
    topK,
    includeMetadata: true,
    filter: { domain },
  });
  
  console.log(" Pinecone raw matches:", result.matches);
  
  if (!result.matches || result.matches.length === 0) {
    return {
      score: 0,
      solution: null
    };
  }
  // if (!result.matches.length) {
  //   return { matched: false, score: 0 };
  // }

  const best = result.matches[0];

  return {
    score: best.score,
    issue: best.metadata.issue,
    solution: best.metadata.solution,
  };
}
