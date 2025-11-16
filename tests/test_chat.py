import pytest
from app.chat import load_collection_as_retriever
import os

def test_load_retriever_no_collection():
    with pytest.raises(Exception):
        _ = load_collection_as_retriever("this_collection_does_not_exist_12345")
