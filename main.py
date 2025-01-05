from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

model_name = "jinaai/jina-embeddings-v3"  
model_kwargs = {'device': 'cpu',
"trust_remote_code": True}  
encode_kwargs = {'normalize_embeddings': False}

embeddings = HuggingFaceEmbeddings(
model_name = model_name,
model_kwargs = model_kwargs,
encode_kwargs = encode_kwargs
)

vector_store = FAISS.load_local("vectorstores/jina_embds_vectorstore/jina_embds_vectorstore", embeddings=embeddings, allow_dangerous_deserialization=True)
llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)

prompt_template = PromptTemplate(
    input_variables=["question", "context"],
    template="""
Jesteś asystentem AI pomagającym kandydatom w wyborze kierunku studiów. Użyj poniższych odnalezionych dokumentów, aby dostarczyć odpowiednią odpowiedź.

Pytanie: {question}

Kontekst:
{context}

Udziel szczegółowej odpowiedzi korzystając z dostarczonego kontekstu. Jeśli kontekst nie dostarcza pełnej odpowiedzi, dodaj ogólną sugestię na podstawie swojej wiedzy, ale zaznacz, że jest to ogólna rada.
"""
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vector_store.as_retriever(),
    return_source_documents=True,  # Include source documents in the response
    chain_type_kwargs={"prompt": prompt_template}
)

question = "Czego uczą się studenci logistyki i gdzie mogą pracować?"
result = qa_chain.invoke({"query": question})


print("Odpowiedź:", result["result"])

print("Źródła:")
for source in result["source_documents"]:
    print(f"- {source.metadata['title']} (Strona {source.metadata['page']}), Tekst: {source.page_content}")