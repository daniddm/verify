from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
from transformers import AutoTokenizer, AutoModel
from torch.utils.data import DataLoader, TensorDataset
import joblib
import re

app = FastAPI()
app.add_middleware(
   CORSMiddleware,
   allow_origins=["http://localhost:4200"],
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"],
)

MODEL_NAME = "microsoft/deberta-v3-base"
MAX_LENGTH = 512
BATCH_SIZE = 1

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

logistic_model = joblib.load("logistic_regression_model.pkl")

class NewsText(BaseModel):
   text: str

def clean_text(text):
   text = re.sub(r"\s+", " ", text).strip()
   return text.lower()

def create_dataloader(tokens):
   dataset = TensorDataset(tokens['input_ids'], tokens['attention_mask'])
   return DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=False)

def generate_embeddings(dataloader):
   embeddings = []
   model.eval()
   with torch.no_grad():
       for batch in dataloader:
           input_ids, attention_mask = [t.to(device) for t in batch]
           outputs = model(input_ids=input_ids, attention_mask=attention_mask)
           embeddings.append(outputs.last_hidden_state[:, 0, :])
   return torch.cat(embeddings, dim=0)

@app.post("/api/analyze")
async def analyze_news(news: NewsText):
   try:
       text_clean = clean_text(news.text)
       tokens = tokenizer(text_clean, padding=True, truncation=True, 
                        max_length=MAX_LENGTH, return_tensors="pt")
       dataloader = create_dataloader(tokens)
       embeddings = generate_embeddings(dataloader)
       prediction = logistic_model.predict_proba(embeddings.cpu().numpy())[:, 1][0]
       return {"probability": float(prediction)}
   except Exception as e:
       raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
   import uvicorn
   uvicorn.run(app, host="0.0.0.0", port=8080)