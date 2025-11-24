from dotenv import load_dotenv
import os

load_dotenv()

OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "chrome_langchain_db")
