# naive chunker. For production consider smarter chunkers with sentence boundaries and overlap.
from uuid import uuid4

def chunk_text(pages, metadata, chunk_size=800, overlap=100):
    chunks = []
    for p in pages:
        text = (p.get('text') or '').strip()
        if not text:
            continue
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            snippet = text[start:end]
            chunks.append({
                'id': uuid4().hex,
                'text': snippet,
                'meta': {**metadata, 'page': p.get('page')}
            })
            start = end - overlap
            if start < 0:
                start = 0
    return chunks