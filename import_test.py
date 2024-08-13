import sys
import array
import time
import oci
import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import oracledb
from langchain_community.vectorstores import oraclevs
from langchain_community.vectorstores.oraclevs import OracleVS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from ads.llm import GenerativeAIEmbeddings, GenerativeAI
from sentence_transformers import CrossEncoder
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_core.documents import BaseDocumentTransformer, Document
from langchain_community.llms import OCIGenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import requests
from PyPDF2 import PdfReader
from io import BytesIO
print("Successfully imported libraries and modules")

#oraclevs
#langchain_llm
# pip install HuggingFaceEmbeddings
#shifted LangChain to lowercase