import os
import openai
import pinecone
from dotenv import load_dotenv
load_dotenv()

OPENAI_KEY = os.getenv('OPENAI_API_KEY')
PINECONE_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENV = os.getenv('PINECONE_ENVIRONMENT')
INDEX_NAME = os.getenv('PINECONE_INDEX_NAME','hackrx-index')

openai.api_key = OPENAI_KEY
pinecone.init(api_key=PINECONE_KEY, environment=PINECONE_ENV)

# create index if not exists
def ensure_index(dim=1536):
    if INDEX_NAME not in pinecone.list_indexes():
        pinecone.create_index(name=INDEX_NAME, dimension=dim)

index = pinecone.Index(INDEX_NAME)

# Get embeddings from OpenAI (text-embedding-3-small or text-embedding-3-large)
def get_embedding(text: str):
    resp = openai.Embedding.create(model='text-embedding-3-small', input=text)
    return resp['data'][0]['embedding']

# Upsert chunks
def embed_and_upsert(chunks):
    batch = []
    for c in chunks:
        emb = get_embedding(c['text'])
        meta = c['meta']
        batch.append((c['id'], emb, meta))
    # Pinecone upsert expects list of tuples
    index.upsert(vectors=batch)
    return True

# Query index
def query_index(query: str, top_k=5):
    emb = get_embedding(query)
    resp = index.query(emb, top_k=top_k, include_metadata=True, include_values=False)
    # resp.matches is list of matches with id, score, metadata
    return resp['matches']