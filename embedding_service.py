from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

app = FastAPI()

# model = SentenceTransformer("all-MiniLM-L6-v2")  # very popular it gives threshold value upto 0.78
model = SentenceTransformer("all-mpnet-base-v2")

class EmbedRequest(BaseModel):
    text: str

@app.post("/embed")
def embed(req: EmbedRequest):
    vector = model.encode(req.text).tolist()
    return {"embedding": vector}
