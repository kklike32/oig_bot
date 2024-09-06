from langchain_core.documents import Document

def create_docs(chunks):
    docs = [Document(page_content=text, metadata={"id": page_num, "link": f"Page {page_num}"}) 
            for page_num, sublist in enumerate(chunks) for text in sublist]
    return docs

def create_docsv2(chunks, doc_names, doc_urls):
    docs = []
    for doc_name, doc_url, chunk_list in zip(doc_names, doc_urls, chunks):
        for page_num, text in enumerate(chunk_list):
            doc = Document(
                page_content=text,
                metadata={
                    "id": page_num,
                    "document": doc_name,
                    "url": doc_url,
                    "page": page_num
                }
            )
            docs.append(doc)
    return docs
