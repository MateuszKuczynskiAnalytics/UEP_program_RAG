from langchain.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
import os
from langchain.vectorstores import FAISS

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

embeddings = OpenAIEmbeddings(openai_api_key=api_key)

vector_store = FAISS.from_documents(all_chunks, embeddings)
vector_store.save_local("uni_program_vectorstore")




