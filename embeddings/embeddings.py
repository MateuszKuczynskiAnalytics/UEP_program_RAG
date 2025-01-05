from langchain.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
import os
from langchain.vectorstores import FAISS

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

embeddings = OpenAIEmbeddings(openai_api_key=api_key)

vector_store = FAISS.from_documents(all_chunks, embeddings)
vector_store.save_local("uni_program_vectorstore")

from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# Initialize GPT-4o-mini model
llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key) # Use correct model name for GPT-4o-mini

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
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt_template}
)

question = "Opowiedz mi w szczegółach czego uczyłbym się na kierunku prawno-ekonomicznym?"
result = qa_chain.invoke({"query": question})

print("Odpowiedź:", result["result"])

print("Źródła:")
for source in result["source_documents"]:
    print(f"- {source.metadata['program_title']} (Strona {source.metadata['page']})")