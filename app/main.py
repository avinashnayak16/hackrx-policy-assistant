import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List
import requests
from pinecone import Pinecone, ServerlessSpec
from pinecone.exceptions import PineconeApiException
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import io
import pdfplumber
import re

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-east-1")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "hackrx-index")
TEAM_TOKEN = os.getenv("TEAM_TOKEN")

if not all([GEMINI_API_KEY, PINECONE_API_KEY, TEAM_TOKEN]):
    raise RuntimeError("Missing one or more required environment variables.")

pc = Pinecone(api_key=PINECONE_API_KEY)

def ensure_index(name: str, dimension: int, metric: str, region: str):
    try:
        existing_indexes = pc.list_indexes()  # List of index names
    except Exception as e:
        raise RuntimeError(f"Error fetching Pinecone indexes: {str(e)}")

    if name in existing_indexes:
        try:
            index_description = pc.describe_index(name)
            if getattr(index_description, "dimension", None) != dimension:
                raise RuntimeError(
                    f"Pinecone index '{name}' dimension mismatch: "
                    f"existing {index_description.dimension} vs required {dimension}. "
                    f"Please delete the index manually and restart."
                )
        except Exception as e:
            raise RuntimeError(f"Error describing index '{name}': {str(e)}")
        return  # ✅ Skip creation if it already exists
    else:
        try:
            pc.create_index(
                name=name,
                dimension=dimension,
                metric=metric,
                spec=ServerlessSpec(
                    cloud="aws",
                    region=region
                ),
            )
        except PineconeApiException as e:
            if e.status == 409:  # Already exists — safe to ignore
                return
            raise

ensure_index(PINECONE_INDEX_NAME, 384, "cosine", PINECONE_ENV)
index = pc.Index(PINECONE_INDEX_NAME)

app = FastAPI()
security = HTTPBearer()

model = SentenceTransformer('all-MiniLM-L6-v2')

class HackrxRequest(BaseModel):
    documents: str
    questions: List[str]

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    expected = TEAM_TOKEN.strip()
    received = credentials.credentials.strip()
    if received != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return received

GEMINI_API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

def gemini_chat(prompt: str) -> str:
    url = f"{GEMINI_API_BASE_URL}/models/gemini-2.0-flash:generateContent"
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY
    }
    json_data = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }
    resp = requests.post(url, headers=headers, json=json_data)
    resp.raise_for_status()
    data = resp.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError, TypeError):
        raise RuntimeError(f"Unexpected Gemini API response: {data}")

def get_embedding(text: str):
    return model.encode(text).tolist()

@app.post("/api/v1/hackrx/run")
def run_submission(data: HackrxRequest, token: str = Depends(verify_token)):
    try:
        response = requests.get(data.documents)
        response.raise_for_status()
        pdf_bytes = response.content

        # Extract text from PDF
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            chunks = []
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                for para in re.split(r'(?m)^\s*\d+\.\d+\.\d+', text):  # splits on clause numbers like 3.1.14
                    para = para.strip()
                    if para:
                        chunks.append({"text": para, "page": page_num})

        # Upsert each chunk as a separate vector
        vectors = []
        for i, chunk in enumerate(chunks):
            embedding = get_embedding(chunk["text"])
            vectors.append((f"doc1_chunk{i}", embedding, {"text_snippet": chunk["text"], "page": chunk["page"]}))
        index.upsert(vectors=vectors)

        answers = []
        for question in data.questions:
            q_embedding = get_embedding(question)
            search_results = index.query(vector=q_embedding, top_k=7, include_metadata=True)
            context = "\n".join(match.metadata.get("text_snippet", "") for match in search_results.matches)

            # Improved prompt for Gemini
            prompt = (
                f"You are an expert insurance policy assistant. "
                f"Given the following policy excerpts:\n{context}\n\n"
                f"Answer the user's question using only the provided excerpts. "
                f"Quote the relevant clause(s) verbatim if possible. "
                f"If the answer is not found, say so. "
                f"Question: {question}\n\n"
                f"Return only the answer, no extra text."
            )
            answer = gemini_chat(prompt)
            answers.append(answer.strip())

        return {"answers": answers}

    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch document: {str(e)}")
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    except Exception as e:
        err_msg = str(e).lower()
        if "quota" in err_msg or "rate limit" in err_msg:
            raise HTTPException(status_code=429, detail="Gemini API quota exceeded. Please try again later.")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
