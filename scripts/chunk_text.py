from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_text(text, chunk_size=800, chunk_overlap=100):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", "!", "?"]
    )
    return text_splitter.split_text(text)

def chunk_all_texts(texts):
    return [chunk_text(text) for text in texts]

