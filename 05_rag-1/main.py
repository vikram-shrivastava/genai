from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore

from dotenv import load_dotenv
import getpass
import os
load_dotenv()
if not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google API key: ")

#loading the resource
pdf_path =Path(__file__).parent / "ReviewPaper.pdf"
loader= PyPDFLoader(file_path=pdf_path)
docs= loader.load() #Read Pdf File
# print("Docs",docs[0])

#Chuncking the docs
text_splitter= RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
docs= text_splitter.split_documents(docs)
# print(f"Chuncked into {len(docs)} documents")
# print("First Document:",docs[0].page_content)

#Generating Embeddings
embeddings= GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
vector=embeddings.embed_documents([docs[1].page_content])

# vector store
vector_store= QdrantVectorStore.from_documents(
    documents=docs,
    url="http://vector-db:6333",
    collection_name="GENAI",
    embedding=embeddings,
)
print("Indexed the document successfully")
