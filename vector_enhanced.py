from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import pandas as pd
from dotenv import load_dotenv

EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
# Load financial data
try:
    df = pd.read_csv("Financial-Literacy-Compilation.csv")
    print(f"✅ Successfully loaded {len(df)} financial records")
except FileNotFoundError:
    print("❌ Error: Financial-Literacy-Compilation.csv not found!")
    raise

embeddings = OllamaEmbeddings(model=EMBED_MODEL)

db_location = "./chrome_langchain_db"
add_documents = not os.path.exists(db_location)

if add_documents:
    print("🔄 Building vector database for the first time...")
    documents = []
    ids = []

    for i, row in df.iterrows():
        # Combine ALL columns into one text block
        row_text = "\n".join([f"{col}: {row[col]}" for col in df.columns])

        document = Document(
            page_content=row_text,
            metadata={"row_index": i},
            id=str(i)
        )
        documents.append(document)
        ids.append(str(i))

vector_store = Chroma(
    collection_name="finguide_financial_data",
    persist_directory=db_location,
    embedding_function=embeddings
)

if add_documents:
    print(f"📚 Adding {len(documents)} documents to vector store...")
    vector_store.add_documents(documents=documents, ids=ids)
    print("✅ Vector database created successfully!")
else:
    print("✅ Loading existing vector database...")

retriever = vector_store.as_retriever(search_kwargs={"k": 5})

def get_retriever():
    """Return the retriever for use in views"""
    return retriever

