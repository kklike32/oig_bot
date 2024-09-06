import oci
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.config import model_name, index_dir, index_dirv2
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings  # Update import as per the deprecation warning
from langchain_core.prompts import PromptTemplate  # Update import as per the deprecation warning

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Load OCI Config and Generative AI Client
compartment_id = "ocid1.compartment.oc1..aaaaaaaagvtl2poaovkpbtndd4fzi4ro5qx3bwcwlqzmqcgcjuzujelrjq2q"
CONFIG_PROFILE = "DEFAULT"
config = oci.config.from_file('~/.oci/config', CONFIG_PROFILE)
endpoint = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"
generative_ai_inference_client = oci.generative_ai_inference.GenerativeAiInferenceClient(
    config=config, service_endpoint=endpoint, retry_strategy=oci.retry.NoneRetryStrategy(), timeout=(10, 240)
)

# Function to get LLM response from Oracle GenAI
def get_llm_response(input_text: str, context_docs: list) -> str:
    chat_detail = oci.generative_ai_inference.models.ChatDetails()
    chat_request = oci.generative_ai_inference.models.CohereChatRequest()
    chat_request.message = input_text
    chat_request.max_tokens = 1200 # 600
    chat_request.temperature = 0.8 # 1
    chat_request.frequency_penalty = 0.1 # 0
    chat_request.top_p = 0.85 # 0.75
    chat_request.top_k = 0
    chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(
        model_id="ocid1.generativeaimodel.oc1.us-chicago-1.amaaaaaask7dceyawk6mgunzodenakhkuwxanvt6wo3jcpf72ln52dymk4wq"
    )
    chat_detail.chat_request = chat_request
    chat_detail.compartment_id = compartment_id
    chat_response = generative_ai_inference_client.chat(chat_detail)
    response_text = chat_response.data.chat_response.text
    
    # Post-process to suggest possible page numbers or sections
    pages = [doc.metadata.get("page") for doc in context_docs if "page" in doc.metadata]
    if pages:
        page_ref = f" (Possible references: Pages {', '.join(map(str, pages))})"
        response_text += page_ref
    else:
        response_text += " (Please refer to the document index for detailed location.)"
    
    return response_text

def get_llm_responsev2(input_text: str, context_docs: list) -> str:
    chat_detail = oci.generative_ai_inference.models.ChatDetails()
    chat_request = oci.generative_ai_inference.models.CohereChatRequest()
    chat_request.message = input_text
    chat_request.max_tokens = 600
    chat_request.temperature = 1
    chat_request.frequency_penalty = 0
    chat_request.top_p = 0.75
    chat_request.top_k = 0
    chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(
        model_id="ocid1.generativeaimodel.oc1.us-chicago-1.amaaaaaask7dceyawk6mgunzodenakhkuwxanvt6wo3jcpf72ln52dymk4wq"
    )
    chat_detail.chat_request = chat_request
    chat_detail.compartment_id = compartment_id
    chat_response = generative_ai_inference_client.chat(chat_detail)
    response_text = chat_response.data.chat_response.text
    
    # Limit the number of references and format them clearly
    references = []
    for doc in context_docs[:2]:  # Limit to top 2 documents
        doc_name = doc.metadata.get("document")
        doc_url = doc.metadata.get("url")
        if doc_name:
            references.append(f"Document: {doc_name}\nURL: {doc_url}")
    
    if references:
        response_text += "\n\nReferences:\n" + "\n\n".join(references)
    
    return response_text



# Function to load FAISS vector store and run the chatbot interactively
def load_faiss_and_run_chatbot():
    faiss_store = FAISS.load_local(index_dirv2, HuggingFaceEmbeddings(model_name=model_name), allow_dangerous_deserialization=True)
    template = """You are a knowledgeable assistant who provides detailed and accurate answers to questions. When responding, aim to fully explain the process or concept asked about, including steps, examples, and relevant details. If additional information is available in specific documents, include a reference to these documents and the relevant sections.

    Context:
    {context}

    Question: {question}

    Answer comprehensively and clearly. After giving a full answer, include references to specific documents and sections where the user can find more detailed information."""
    
    prompt = PromptTemplate.from_template(template)
    retriever = faiss_store.as_retriever()

    print("Welcome to the RAG Chatbot! Type your question below (or type 'exit' to quit):")
    
    while True:
        query = input("You: ")
        if query.lower() == "exit":
            print("Goodbye!")
            break
        
        retrieved_docs = retriever.invoke(query)
        context = "\n".join([doc.page_content for doc in retrieved_docs])

        # Generate input for Oracle GenAI
        input_text = prompt.format(context=context, question=query)

        # Get response from Oracle GenAI with context information
        answer = get_llm_responsev2(input_text, retrieved_docs)

        print(f"Chatbot: {answer}\n")


if __name__ == "__main__":
    load_faiss_and_run_chatbot()
