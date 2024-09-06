import oci
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.config import model_name, index_dir, index_dirv2
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings  # Update import as per the deprecation warning
from langchain_core.prompts import PromptTemplate  # Update import as per the deprecation warning

# Load OCI Config and Generative AI Client
compartment_id = "COMP"
CONFIG_PROFILE = "DEFAULT"
config = oci.config.from_file('~/.oci/config', CONFIG_PROFILE)
endpoint = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"
generative_ai_inference_client = oci.generative_ai_inference.GenerativeAiInferenceClient(
    config=config, service_endpoint=endpoint, retry_strategy=oci.retry.NoneRetryStrategy(), timeout=(10, 240)
)

# Function to get LLM response from Oracle GenAI
def get_llm_response(input_text: str) -> str:
    chat_detail = oci.generative_ai_inference.models.ChatDetails()
    chat_request = oci.generative_ai_inference.models.CohereChatRequest()
    chat_request.message = input_text
    chat_request.max_tokens = 600
    chat_request.temperature = 1
    chat_request.frequency_penalty = 0
    chat_request.top_p = 0.75
    chat_request.top_k = 0
    chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(
        model_id="MODEL"
    )
    chat_detail.chat_request = chat_request
    chat_detail.compartment_id = compartment_id
    chat_response = generative_ai_inference_client.chat(chat_detail)
    response_text = chat_response.data.chat_response.text
    return response_text

# Function to load FAISS vector store and run the chatbot interactively
def load_faiss_and_run_chatbot():
    faiss_store = FAISS.load_local(index_dir, HuggingFaceEmbeddings(model_name=model_name), allow_dangerous_deserialization=True)
    template = """You are a helpful assistant. Provide a concise answer to the question based on the following context.
    Also, provide a reference to the section or page number of the document where the information can be found.

    Context:
    {context}

    Question: {question}

    Answer in 2-3 sentences and include the reference."""

    prompt = PromptTemplate.from_template(template)
    retriever = faiss_store.as_retriever()

    print("Welcome to the RAG Chatbot! Type your question below (or type 'exit' to quit):")
    
    while True:
        query = input("You: ")
        if query.lower() == "exit":
            print("Goodbye!")
            break
        
        retrieved_docs = retriever.invoke(query, k=3)
        context = "\n".join([doc.page_content for doc in retrieved_docs])

        # Generate input for Oracle GenAI
        input_text = prompt.format(context=context, question=query)

        # Get response from Oracle GenAI
        answer = get_llm_response(input_text)

        print(f"Chatbot: {answer}\n")

if __name__ == "__main__":
    load_faiss_and_run_chatbot()
