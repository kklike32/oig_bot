from PyPDF2 import PdfReader
import os

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_all_texts(pdf_dir):
    pdf_files = [os.path.join(pdf_dir, f) for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    all_texts = [extract_text_from_pdf(pdf) for pdf in pdf_files]
    return all_texts

