import os

pdf_files = [os.path.basename(f) for f in os.listdir("data/PDFs") if f.endswith('.pdf')]
print(pdf_files)