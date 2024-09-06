from scripts.extract_text import extract_all_texts
from scripts.chunk_text import chunk_all_texts
from scripts.create_embeddings import create_and_save_faiss_index
from utils.document_helpers import create_docs, create_docsv2
import os

def main1():
    print("Starting v1")
    texts = extract_all_texts("data/PDFs")
    print("First one done")
    chunks = chunk_all_texts(texts)
    print("Chunking done")
    docs = create_docs(chunks)
    print("Docs done")
    create_and_save_faiss_index(docs, "sentence-transformers/all-MiniLM-L12-v2", "data/faiss_index")
    print("Faiss done")

def main2():
    print("Starting v2")
    texts = extract_all_texts("data/PDFs")
    print("First one done")
    chunks = chunk_all_texts(texts)
    print("Chunking done")
    
    pdf_files = [os.path.basename(f) for f in os.listdir("data/PDFs") if f.endswith('.pdf')]
    print(pdf_files)
    pdf_urls = [
    # Administering Oracle Identity Governance 
    "https://docs.oracle.com/en/middleware/idm/identity-governance/12.2.1.4/omadm/administering-oracle-identity-governance.pdf",

    # Developing and Customizing Applications for Oracle Identity Governance
    "https://docs.oracle.com/en/middleware/idm/identity-governance/12.2.1.4/omdev/developing-and-customizing-applications-oracle-identity-governance.pdf",

    # Help Topics for Oracle Identity Governance
    "https://docs.oracle.com/en/middleware/idm/identity-governance/12.2.1.4/omhlp/help-topics-oracle-identity-governance.pdf",

    # Performing Self Service Tasks with Oracle Identity Governance
    "https://docs.oracle.com/en/middleware/idm/identity-governance/12.2.1.4/omusg/performing-self-service-tasks-oracle-identity-governance.pdf",

    # Reference Oracle Identity Governance Docker and Kubernetes
    "https://docs.oracle.com/en/middleware/idm/identity-governance/12.2.1.4/oigdk/reference-oracle-identity-governance-docker-and-kubernetes.pdf",

    # Release Notes for Oracle Identity Management
    "https://docs.oracle.com/en/middleware/idm/suite/12.2.1.4/idmrn/release-notes-oracle-identity-management.pdf",

    # Upgrading Oracle Identity Manager
    "https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/iamup/upgrading-oracle-identity-manager.pdf"
    ]
    
    docs = create_docsv2(chunks, pdf_files, pdf_urls)
    print("Docs done")
    
    # Consider saving the FAISS index under a new name to avoid overwriting
    create_and_save_faiss_index(docs, "sentence-transformers/all-MiniLM-L12-v2", "data/faiss_index_v2")
    print("Faiss done")

if __name__ == "__main__":
    main2()
