from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def load_faiss_index(index_dir, model_name):
    return FAISS.load_local(index_dir, HuggingFaceEmbeddings(model_name=model_name))

