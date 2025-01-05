from langchain.embeddings import HuggingFaceEmbeddings
from scrapers.utils import logger, setup_logging
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
import faiss

model_name = "jinaai/jina-embeddings-v3"  
model_kwargs = {'device': 'cpu',
"trust_remote_code": True}  
encode_kwargs = {'normalize_embeddings': False}

embeddings = HuggingFaceEmbeddings(
model_name = model_name,
model_kwargs = model_kwargs,
encode_kwargs = encode_kwargs
)

setup_logging("logs/jina_embedding_logs.log")
from scrapers.utils import logger
embeddings_list = []

for idx, chunk in enumerate(all_chunks, start=1):
    try:
        embedding = embeddings.embed_query(chunk.page_content)
        embeddings_list.append(embedding)
        logger.info(f"Processed chunk {idx}/{len(all_chunks)}")
    except Exception as e:
        logger.error(f"Error processing chunk {idx}: {e}")

metadatas = [doc.metadata for doc in all_chunks]
contents = [doc.page_content for doc in all_chunks]

dimension = len(embeddings_list[0])  
index = faiss.IndexFlatL2(dimension)  

vector_store = FAISS(
    embedding_function=embeddings, 
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={}  
)

vector_store.add_embeddings(
    text_embeddings=zip(contents, embeddings_list),
    metadatas=metadatas
)

vector_store.save_local("jina_embds_vectorstore")
