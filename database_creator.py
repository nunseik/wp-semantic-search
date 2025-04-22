from csv_reader import get_csv_content, get_new_entries_content
import json
from sentence_transformers import SentenceTransformer
import faiss
import os

model = SentenceTransformer('all-MiniLM-L6-v2')  # Or another model

def get_new_contents(new_entries=None):
    if not new_entries:
        return None
    
    new_list_contents = get_new_entries_content(new_entries)
    return [row['content'] for row in new_list_contents]

def save_clean_contents(new_entries=None):
    if os.path.exists("files/news_content.jsonl"):
        if not new_entries:
            return
        new_clean_contents = get_new_contents(new_entries)

        with open("files/news_content.jsonl", "a", encoding="utf-8") as f:
            for text in new_clean_contents:
                f.write(text.strip() + "\n")

    else:
        list_contents = get_csv_content()

        if list_contents == []:
            return []
        
        clean_contents = [row['content'] for row in list_contents]
        
        with open("files/news_content.jsonl", "w", encoding="utf-8") as f:
            for text in clean_contents:
                f.write(text.strip() + "\n")

def get_clean_contents():
    with open("files/news_content.jsonl", "r", encoding="utf-8") as f:
        return [line.strip() for line in f]


def save_metadata_dicts(new_entries=None):
    if os.path.exists("files/news_meta.jsonl"):
        if not new_entries:
            return
        new_list_contents = get_new_entries_content(new_entries)

        new_metadata_dicts = [{'id':row['id'], 'modified':row['modified'],'title':row['title'], 'slug':row['slug']} for row in new_list_contents]

        with open("files/news_meta.jsonl", "a", encoding="utf-8") as outfile:
            for row in new_metadata_dicts:
                json.dump(row, outfile, ensure_ascii=False)
                outfile.write("\n")
    else:
        list_contents = get_csv_content()
        
        metadata_dicts = [{'id':row['id'], 'modified':row['modified'],'title':row['title'], 'slug':row['slug']} for row in list_contents]

        with open("files/news_meta.jsonl", "w", encoding="utf-8") as outfile:
            for row in metadata_dicts:
                json.dump(row, outfile, ensure_ascii=False)
                outfile.write("\n")

def get_metadata_dicts():
    metadata_dicts = []

    with open("files/news_meta.jsonl", "r", encoding="utf-8") as infile:
        for line in infile:
            metadata_dicts.append(json.loads(line))

    return metadata_dicts

def get_faiss_index(new_entries = None):
    new_contents = get_new_contents(new_entries)
    if os.path.exists("files/news_index.faiss") and not new_contents:
        index = faiss.read_index("files/news_index.faiss")
    elif os.path.exists("files/news_index.faiss") and new_contents:
        embeddings = model.encode(new_contents, normalize_embeddings=True)
        # Adding the embeddings to the index
        index = faiss.read_index("files/news_index.faiss")
        index.add(embeddings)
        faiss.write_index(index, "files/news_index.faiss")
    else:
        clean_contents = get_clean_contents()
        embeddings = model.encode(clean_contents, normalize_embeddings=True)

        # Dimensions of our embeddings
        d = embeddings.shape[1]

        # Creating an index for our dense vectors
        index = faiss.IndexFlatL2(d)

        # Adding the embeddings to the index
        index.add(embeddings)

        # write index to file
        faiss.write_index(index, "files/news_index.faiss")

        print(f"Total sentences indexed: {index.ntotal}")
    return index

def querying_index(query_sentence, new_entries=None):
    #get faiss index
    index = get_faiss_index(new_entries)

    # Define a query sentence
    query_embedding = model.encode([query_sentence])

    # Perform the search
    k = 3  # Number of nearest neighbors to retrieve
    distances, indices = index.search(query_embedding, k)

    # Display the results
    print(f"Query: {query_sentence}")
        
    metadata_dicts = get_metadata_dicts()
    clean_contents = get_clean_contents()

    return [
    {
        "content": clean_contents[idx],
        "metadata": metadata_dicts[idx],
        "distance": distances[0][i]
    }
    for i, idx in enumerate(indices[0])
]