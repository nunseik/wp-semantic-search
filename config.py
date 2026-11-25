import os

# Where the local database lives. Override with WP_SEARCH_DATA (the eval uses its own snapshot).
DATA_DIR = os.environ.get("WP_SEARCH_DATA", "files")
META_PATH = os.path.join(DATA_DIR, "news_meta.jsonl")
CHUNKS_PATH = os.path.join(DATA_DIR, "chunks.jsonl")
INDEX_PATH = os.path.join(DATA_DIR, "index.faiss")
LAST_ID_PATH = os.path.join(DATA_DIR, "last_id.txt")
DB_FILES = [INDEX_PATH, CHUNKS_PATH, LAST_ID_PATH, META_PATH]

# Embedding model. Changing it requires a --refresh, since the index stores its vectors.
MODEL_NAME = os.environ.get("WP_SEARCH_MODEL", "all-MiniLM-L6-v2")

# Chunking: paragraphs are packed into chunks of up to CHUNK_WORDS words;
# longer paragraphs are split into windows that overlap by CHUNK_OVERLAP words.
CHUNK_WORDS = 120
CHUNK_OVERLAP = 20
