from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
import os

CHROMA_ROOT = os.environ.get("CHROMA_ROOT", "./chroma_db")

def load_collection_as_retriever(collection_name: str, k: int = 4):
    embeddings = OpenAIEmbeddings()
    db = Chroma(collection_name=collection_name, persist_directory=CHROMA_ROOT, embedding_function=embeddings)
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": k})
    return retriever

def answer_query(collection_name: str, question: str, chat_history: list = None, model_name: str = "gpt-4o-mini"):
    retriever = load_collection_as_retriever(collection_name)
    chat_model = ChatOpenAI(temperature=0, model_name=model_name)
    qa = ConversationalRetrievalChain.from_llm(chat_model, retriever=retriever, return_source_documents=True)
    resp = qa({"question": question, "chat_history": chat_history or []})
    return resp
