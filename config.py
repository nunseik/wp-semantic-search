import os

# Where the local database lives. Override with WP_SEARCH_DATA (the eval uses its own snapshot).
DATA_DIR = os.environ.get("WP_SEARCH_DATA", "files")
META_PATH = os.path.join(DATA_DIR, "news_meta.jsonl")
CHUNKS_PATH = os.path.join(DATA_DIR, "chunks.jsonl")
INDEX_PATH = os.path.join(DATA_DIR, "index.faiss")
LAST_ID_PATH = os.path.join(DATA_DIR, "last_id.txt")
INDEX_MODEL_PATH = os.path.join(DATA_DIR, "index_model.txt")  # model that built the index
DB_FILES = [INDEX_PATH, CHUNKS_PATH, LAST_ID_PATH, META_PATH, INDEX_MODEL_PATH]

# Embedding model. Changing it requires a --refresh, since the index stores its vectors.
# Multilingual, because the indexed sites are in Portuguese: on eval/ it scores recall@5 0.989
# against 0.700 for the English all-MiniLM-L6-v2 (see README).
MODEL_NAME = os.environ.get("WP_SEARCH_MODEL", "intfloat/multilingual-e5-base")

# Chunking: paragraphs are packed into chunks of up to CHUNK_WORDS words;
# longer paragraphs are split into windows that overlap by CHUNK_OVERLAP words.
CHUNK_WORDS = 120
CHUNK_OVERLAP = 20
