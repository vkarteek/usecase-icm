import OpenAI from "openai";

const client = new OpenAI({
  apiKey:"",
});

async function test() {
    try {
      const res = await client.embeddings.create({
        model: "text-embedding-3-small",
        input: "hello world",
      });
      console.log("Embedding length:", res.data[0].embedding.length);
    } catch (err) {
      console.error("Embedding failed:");
      console.error(err.message || err);
    }
  }
  
  test();

// async function listModels() {
//   const models = await client.models.list();

//   // Show only embedding models
//   const embeddingModels = models.data
//     .map(m => m.id)
//     .filter(id => id.includes("embedding"));

//   console.log("Embedding models you have access to:");
//   embeddingModels.forEach(m => console.log(" -", m));
// }

// listModels().catch(console.error);
