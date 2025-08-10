import httpx
import tempfile
from pathlib import Path
import pdfplumber
from docx import Document
import uuid

async def download_file(url: str) -> Path:
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url)
        r.raise_for_status()
        suffix = url.split('?')[0].split('.')[-1]
        tmp = Path(tempfile.gettempdir()) / f"hackrx_{uuid.uuid4().hex}.{suffix}"
        tmp.write_bytes(r.content)
        return tmp

def extract_text_from_pdf(path: Path):
    texts = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            texts.append({"page": i+1, "text": page.extract_text() or ""})
    return texts

def extract_text_from_docx(path: Path):
    doc = Document(path)
    full = []
    for i, para in enumerate(doc.paragraphs):
        full.append({"page": None, "text": para.text})
    return full

async def download_and_extract(url: str):
    path = await download_file(url)
    ext = path.suffix.lower()
    if ext in ['.pdf']:
        texts = extract_text_from_pdf(path)
    elif ext in ['.docx']: 
        texts = extract_text_from_docx(path)
    else:
        # fallback - try to treat as pdf
        texts = extract_text_from_pdf(path)
    metadata = {"source_url": url}
    return texts, metadata
