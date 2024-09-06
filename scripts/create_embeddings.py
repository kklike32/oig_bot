from utils.document_helpers import create_docs
import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

def create_and_save_faiss_index(docs, model_name, index_dir):
    model_4db = HuggingFaceEmbeddings(model_name=model_name)
    faiss_store = FAISS.from_documents(docs, model_4db)
    faiss_store.save_local(index_dir)

if __name__ == "__main__":
    # Assume texts have been extracted and chunked
    docs = create_docs(chunks)
    create_and_save_faiss_index(docs, "sentence-transformers/all-MiniLM-L12-v2", "data/faiss_index")

