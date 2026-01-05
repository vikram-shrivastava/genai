import streamlit as st
from pathlib import Path
from langchain_community.document_loaders import (
    PyPDFLoader, TextLoader, CSVLoader, Docx2txtLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from google.genai import types
from google import genai
from dotenv import load_dotenv
import getpass
import os

# ----------------- Setup -----------------
st.set_page_config(page_title="📚 Document ChatBot", layout="wide")

load_dotenv()
if not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google API key: ")

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# ----------------- Tool Definitions -----------------
def pdfeditor(pdfpath: str):
    """Stub: Edit PDF document (merge, annotate, extract pages, etc.)."""
    return f"PDF editor called on {pdfpath}"

def docxeditor(docxpath: str):
    """Stub: Edit DOCX document (extract, update content, etc.)."""
    return f"Docx editor called on {docxpath}"

def csvreader(csvpath: str):
    """Stub: Read and summarize CSV file."""
    return f"CSV reader called on {csvpath}"

def textextractor(filepath: str):
    """Stub: Extract plain text from any file."""
    return f"Text extractor called on {filepath}"

# Map extensions to loaders
loader_mapping = {
    "pdf": PyPDFLoader,
    "docx": Docx2txtLoader,
    "txt": TextLoader,
    "csv": CSVLoader
}

# Available tools for system prompt
available_tools = {
    "pdfeditor": pdfeditor,
    "docxeditor": docxeditor,
    "csvreader": csvreader,
    "textextractor": textextractor
}

# ----------------- Sidebar -----------------
st.sidebar.header("⚙️ Controls")
st.sidebar.write("Upload a document and start chatting.")

# ----------------- File Upload -----------------
file = st.file_uploader("📂 Upload your file", type=["pdf", "docx", "csv", "txt"])

if file is not None:
    file_path = Path.cwd() / file.name
    with open(file_path, "wb") as f:
        f.write(file.getbuffer())

    # Load docs
    loader = loader_mapping[file.name.split(".")[-1]](file_path=str(file_path))
    docs = loader.load()

    # Split docs
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(docs)

    # Vector store
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vector_store = QdrantVectorStore.from_documents(
        documents=docs,
        url="http://localhost:6333",
        collection_name="chatbot",
        embedding=embeddings,
    )

    st.success("✅ Document indexed successfully. You can now chat with it.")

    # ----------------- Chat UI -----------------
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    query = st.chat_input("Ask something about your document...")

    if query:
        st.chat_message("user").write(query)
        st.session_state.messages.append({"role": "user", "content": query})

        # Similarity search
        search_result = vector_store.similarity_search(query=query)

        context = "\n\n".join([
            f"Page Number: {doc.metadata.get('page_label','?')}\n"
            f"Content: {doc.page_content}\n"
            f"File Location: {doc.metadata.get('source','')}"
            for doc in search_result
        ])

        # ----------------- System Prompt -----------------
        system_prompt = f"""
        You are a helpful AI assistant. 
        Always answer based only on the context below. 
        If you cannot find the answer in the context, reply with "I don’t know".

        Follow these steps before giving the result:
        1. Analyze: Break down and understand the user query.
        2. Think: Reflect on how the query can be solved, considering multiple angles.
        3. Tool Planning: If the query requires a tool, select one from the available list.
        4. Tool Call: Call the tool with correct parameters (example: pdfeditor(pdfpath)).
        5. Observe: Check the output, calculate inaccuracy (loss score: 0=perfect, 10=bad).
        6. Re-evaluate: If loss > 2, restart from step 1.
        7. Result: If loss <= 2, present the final result.

        Available Tools: {list(available_tools.keys())}

        Context:
        {context}
        """

        # ----------------- Model Response -----------------
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(system_instruction=system_prompt),
            contents=[query],
        )

        answer = response.text
        st.chat_message("assistant").write(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
