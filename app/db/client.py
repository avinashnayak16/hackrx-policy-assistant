from sqlalchemy import create_engine, Column, String, Integer, JSON, DateTime, Table, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from datetime import datetime

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Document(Base):
    __tablename__ = 'documents'
    id = Column(String, primary_key=True)
    url = Column(String)
    meta = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def save_document_metadata(url, meta):
    db = SessionLocal()
    from uuid import uuid4
    doc = Document(id=uuid4().hex, url=url, meta=meta)
    db.add(doc)
    db.commit()
    db.close()