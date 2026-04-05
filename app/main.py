from fastapi import FastAPI
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel

MODEL_NAME = "sergeyzh/rubert-mini-frida"

app = FastAPI()

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)
model.eval()


def pool(hidden_state, mask, pooling_method="mean"):
    if pooling_method == "mean":
        s = torch.sum(hidden_state * mask.unsqueeze(-1).float(), dim=1)
        d = mask.sum(axis=1, keepdim=True).float()
        return s / d
    elif pooling_method == "cls":
        return hidden_state[:, 0]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/embed")
def embed(payload: dict):
    text = payload["text"]

    tokenized_inputs = tokenizer(
        [text],
        max_length=512,
        padding=True,
        truncation=True,
        return_tensors="pt",
    )

    with torch.no_grad():
        outputs = model(**tokenized_inputs)

    embedding = pool(
        outputs.last_hidden_state,
        tokenized_inputs["attention_mask"],
        pooling_method="mean"
    )

    embedding = F.normalize(embedding, p=2, dim=1)

    return {"embedding": embedding[0].tolist()}
