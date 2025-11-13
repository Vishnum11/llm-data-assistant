import os
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from .utils import read_file_to_df, df_to_text_rows, chunk_texts
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

CHROMA_ROOT = os.environ.get("CHROMA_ROOT", "./chroma_db")

def ensure_chroma_dir():
    os.makedirs(CHROMA_ROOT, exist_ok=True)

def ingest_file_to_collection(uploaded_file, collection_name: str, max_rows: int = 2000):
    ensure_chroma_dir()
    df = read_file_to_df(uploaded_file)
    texts = df_to_text_rows(df, max_rows=max_rows)
    chunks = chunk_texts(texts, chunk_size=800, chunk_overlap=100)
    embeddings = OpenAIEmbeddings()
    collection = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        metadatas=[{"collection": collection_name} for _ in chunks],
        collection_name=collection_name,
        persist_directory=CHROMA_ROOT
    )
    collection.persist()
    return {"n_chunks": len(chunks), "collection": collection_name}
