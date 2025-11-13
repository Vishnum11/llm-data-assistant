import pytest
from fastapi import UploadFile
from io import BytesIO
from app.ingest import ingest_file_to_collection
import pandas as pd
import os

@pytest.fixture
def small_csv_file():
    df = pd.DataFrame({"a":[1,2,3],"b":["x","y","z"]})
    bio = BytesIO()
    df.to_csv(bio, index=False)
    bio.seek(0)
    file = UploadFile(filename="sample.csv", file=bio)
    return file

def test_ingest_small_csv(small_csv_file, monkeypatch):
    os.environ["OPENAI_API_KEY"] = "test"
    res = ingest_file_to_collection(small_csv_file.file, collection_name="test_collection_local", max_rows=10)
    assert "n_chunks" in res
    assert res["collection"] == "test_collection_local"
