import fetch from "node-fetch";

export async function embedText(text) {
  const res = await fetch("http://localhost:9001/embed", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });

  const data = await res.json();
  return data.embedding;
}


// import OpenAI from "openai";

// const openai = new OpenAI({
//   apiKey: process.env.OPENAI_API_KEY,
// });

// export async function embedText(text) {
//   const res = await openai.embeddings.create({
//     model: "text-embedding-3-large",
//     input: text,
//   });

//   return res.data[0].embedding;
// }
