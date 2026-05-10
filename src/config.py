import os
from dotenv import load_dotenv

load_dotenv()

# MiniMax API (Anthropic-compatible) - using unique env var names to avoid conflicts
MINIMAX_API_KEY = os.getenv("APP_LLM_API_KEY", "")
MINIMAX_BASE_URL = os.getenv("APP_LLM_BASE_URL", "https://api.minimaxi.com/anthropic")
MINIMAX_MODEL = os.getenv("APP_LLM_MODEL", "MiniMax-M2.7")

EMBEDDING_MODEL = "BAAI/bge-small-zh-v1.5"
EMBEDDING_SIMILARITY_THRESHOLD = 0.85
LLM_CONFIDENCE_THRESHOLD = 0.7

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
RAG_TOP_K = 5

COMPRESSION_TARGET = 0.30

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(UPLOAD_DIR, exist_ok=True)
