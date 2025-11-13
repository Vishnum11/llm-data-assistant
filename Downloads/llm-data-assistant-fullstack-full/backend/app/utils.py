import pandas as pd
import io
from langchain.text_splitter import RecursiveCharacterTextSplitter

def read_file_to_df(uploaded_file) -> pd.DataFrame:
    content = uploaded_file.read()
    try:
        return pd.read_csv(io.BytesIO(content))
    except Exception:
        try:
            return pd.read_excel(io.BytesIO(content))
        except Exception as e:
            raise ValueError("Unsupported file type") from e

def df_to_text_rows(df, max_rows: int = 5000):
    df = df.fillna("")
    rows = []
    for i, row in df.iterrows():
        pairs = [f"{col}: {row[col]}" for col in df.columns]
        rows.append(" | ".join(pairs))
        if i+1 >= max_rows:
            break
    return rows

def chunk_texts(texts, chunk_size=800, chunk_overlap=100):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = []
    for t in texts:
        chunks.extend(splitter.split_text(t))
    return chunks
