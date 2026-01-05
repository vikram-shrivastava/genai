from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
# Initialize embeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

# vector_db
vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning_vectors",
    embedding=embeddings,
)
message_history = []

# take user query
query = input(">")
# vector Similarity search in DB
search_result = vector_db.similarity_search(
    query=query
)
# print("Search Result:",search_result)

context = "\n\n".join(
    [f"Page Number: {doc.metadata['page_label']}\nContent: {doc.page_content}\nFile Location {doc.metadata['source']}" for doc in search_result])

SYSTEM_PROMPT = f"""
    You are a helpful AI assistant, who answers the user query based on the context provided retrieved from the document along with the page_contents and page number.
    You should answer user based on this context only and navigate user to the page number for more information.
    After the AI response always add "For more information refer to page number <page_number>".
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Context: 
    {context}
    This is the message history of the conversation so far if the user has asked any previous questions or any query which has relevance to the current question. use the message history to answer the question:
    {message_history}

    Before giving the final answer, always check if the answer is not violating any of the above instructions.
    If the answer is violating any of the above instructions, reply with "I'm sorry, but I can't assist with that request."
    """
message_history.append({"role": "user", "content": query})
# chat completion
response = client.models.generate_content(
    model='gemini-2.5-flash',
    config=types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT),
    contents=[message_history[-1]['content']],
)
print("Response:", response.text)
