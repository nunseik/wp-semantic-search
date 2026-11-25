import json
import os

import faiss

from chunking import chunk_text
from config import CHUNKS_PATH, DATA_DIR, INDEX_PATH, LAST_ID_PATH, META_PATH, MODEL_NAME
from html_stripper import get_stripped_content

# WordPress fields that arrive as HTML and are stored as plain text
TEXT_FIELDS = ("title", "excerpt", "content")

_model = None


def get_model():
    # loaded on first use, so importing this module stays cheap
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_passages(texts):
    return get_model().encode(texts, normalize_embeddings=True)


def embed_query(query):
    # normalized like the passages, so inner product == cosine similarity
    return get_model().encode([query], normalize_embeddings=True)


def read_jsonl(path):
    with open(path, "r", encoding="utf-8") as infile:
        return [json.loads(line) for line in infile if line.strip()]


def write_jsonl(path, rows, mode="w"):
    with open(path, mode, encoding="utf-8") as outfile:
        for row in rows:
            json.dump(row, outfile, ensure_ascii=False)
            outfile.write("\n")


def get_entries_dict(new_entries, fieldnames):
    return [{key: entry[key] for key in fieldnames if key in entry} for entry in new_entries]


def create_last_id_file(raw_data):
    with open(LAST_ID_PATH, "w") as txtfile:
        txtfile.write(str(raw_data[0]["id"]))


def save_metadata(raw_data, new_entries=None, fieldnames=None):
    """Store one plain-text row per article in news_meta.jsonl."""
    if fieldnames is None:
        fieldnames = ["id", "modified", "title", "link", "content"]
    os.makedirs(DATA_DIR, exist_ok=True)

    if os.path.exists(META_PATH):
        if not new_entries:
            return
        rows = get_stripped_content(get_entries_dict(new_entries, fieldnames), TEXT_FIELDS)
        write_jsonl(META_PATH, rows, mode="a")
    else:
        rows = get_stripped_content(get_entries_dict(raw_data, fieldnames), TEXT_FIELDS)
        write_jsonl(META_PATH, rows)

    create_last_id_file(raw_data)


def get_metadata():
    return read_jsonl(META_PATH)


def get_chunks():
    return read_jsonl(CHUNKS_PATH)


def build_chunks(articles, field_to_index):
    """One row per chunk; row i of chunks.jsonl is vector i of the index."""
    rows = []
    for article in articles:
        for n, text in enumerate(chunk_text(article.get(field_to_index) or "")):
            rows.append({"id": article["id"], "chunk": n, "title": article.get("title", ""), "text": text})
    return rows


def passage_texts(rows):
    # the title gives every chunk the article's topic, even chunks deep in the text
    return [f"{row['title']}\n{row['text']}" if row["title"] else row["text"] for row in rows]


def get_faiss_index(new_entries=None, field_to_index="content"):
    """Load the index, adding chunks for new_entries; build it from news_meta.jsonl if missing."""
    if os.path.exists(INDEX_PATH):
        if not os.path.exists(CHUNKS_PATH):
            raise SystemExit(
                "files/index.faiss was built by an older version (one vector per article). "
                "Run with --refresh to rebuild it with chunks."
            )
        index = faiss.read_index(INDEX_PATH)
        n_chunks = len(get_chunks())
        if index.ntotal != n_chunks:
            raise SystemExit(
                f"Index has {index.ntotal} vectors but chunks.jsonl has {n_chunks} rows. Run with --refresh."
            )

        if new_entries:
            new_ids = {entry["id"] for entry in new_entries}
            rows = build_chunks([a for a in get_metadata() if a["id"] in new_ids], field_to_index)
            if rows:
                index.add(embed_passages(passage_texts(rows)))
                write_jsonl(CHUNKS_PATH, rows, mode="a")
                faiss.write_index(index, INDEX_PATH)
                print(f"Added {len(rows)} chunks from {len(new_ids)} new articles")
        return index

    articles = get_metadata()
    rows = build_chunks(articles, field_to_index)
    if not rows:
        raise SystemExit(f"No text found in the '{field_to_index}' field of {len(articles)} articles.")

    embeddings = embed_passages(passage_texts(rows))
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    write_jsonl(CHUNKS_PATH, rows)
    faiss.write_index(index, INDEX_PATH)
    print(f"Indexed {len(rows)} chunks from {len(articles)} articles")
    return index


def querying_index(query_sentence, index, k=5, passages_per_article=2):
    """Return the k best articles for the query, each with its best-matching passages.

    Searches over chunks, then groups hits by article: an article ranks by its best chunk.
    """
    chunks = get_chunks()
    articles = {article["id"]: article for article in get_metadata()}

    n_hits = min(index.ntotal, max(10 * k, 50))
    scores, ids = index.search(embed_query(query_sentence), n_hits)

    results = {}
    for score, i in zip(scores[0], ids[0]):
        if i == -1:
            continue
        chunk = chunks[i]
        result = results.get(chunk["id"])
        if result is None:
            if len(results) == k:
                continue
            result = results[chunk["id"]] = {
                "metadata": articles[chunk["id"]],
                "score": float(score),
                "passages": [],
            }
        if len(result["passages"]) < passages_per_article:
            result["passages"].append(chunk["text"])

    return list(results.values())


def debug_check_alignment():
    index = faiss.read_index(INDEX_PATH)
    assert index.ntotal == len(get_chunks()), "Mismatch between FAISS index and chunks.jsonl!"
    print("✅ FAISS and chunks are aligned.")
