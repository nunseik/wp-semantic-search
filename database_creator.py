from html_stripper import get_stripped_content
import json
from sentence_transformers import SentenceTransformer
import faiss
import os

model = SentenceTransformer('all-MiniLM-L6-v2')  # Or another model

def get_entries_dict(new_entries, fieldnames):
    return [{key: entry[key] for key in fieldnames} for entry in new_entries]

def create_last_id_file(raw_data):
    with open('files/last_id.txt', 'w') as txtfile:
            txtfile.write(str(raw_data[0]['id']))

def get_new_contents(new_entries=None, field_to_index=""):
    if not new_entries:
        return None
    
    new_list_contents = get_stripped_content(new_entries, field_to_index)
    return [row[field_to_index] for row in new_list_contents]

def save_metadata(raw_data, new_entries=None, field_to_index="", fieldnames=None):
    if fieldnames is None:
        fieldnames = ["id", "modified", "title", "slug"]  # default fallback

    if os.path.exists("files/news_meta.jsonl"):
        if not new_entries:
            return
        
        new_list_contents = get_stripped_content(get_entries_dict(new_entries, fieldnames),field_to_index)

        with open("files/news_meta.jsonl", "a", encoding="utf-8") as outfile:
            for row in new_list_contents:
                json.dump(row, outfile, ensure_ascii=False)
                outfile.write("\n")
    else:
        list_contents = get_stripped_content(get_entries_dict(raw_data, fieldnames), field_to_index)

        with open("files/news_meta.jsonl", "w", encoding="utf-8") as outfile:
            for row in list_contents:
                json.dump(row, outfile, ensure_ascii=False)
                outfile.write("\n")
    
    create_last_id_file(raw_data)

def get_metadata():
    metadata_dicts = []

    with open("files/news_meta.jsonl", "r", encoding="utf-8") as infile:
        for line in infile:
            metadata_dicts.append(json.loads(line))

    return metadata_dicts

def get_faiss_index(new_entries = None, field_to_index=""):
    new_contents = get_new_contents(new_entries, field_to_index)
    if os.path.exists("files/index.faiss") and not new_contents:
        index = faiss.read_index("files/index.faiss")
    elif os.path.exists("files/index.faiss") and new_contents:
        embeddings = model.encode(new_contents, normalize_embeddings=True)
        # Adding the embeddings to the index
        index = faiss.read_index("files/index.faiss")
        index.add(embeddings)
        faiss.write_index(index, "files/index.faiss")
    else:
        metadata_dicts = get_metadata()
        clean_contents = [metadata[field_to_index] for metadata in metadata_dicts]
        
        embeddings = model.encode(clean_contents, normalize_embeddings=True)

        # Dimensions of our embeddings
        d = embeddings.shape[1]

        # Creating an index for our dense vectors
        index = faiss.IndexFlatL2(d)

        # Adding the embeddings to the index
        index.add(embeddings)

        # write index to file
        faiss.write_index(index, "files/index.faiss")

        print(f"Total sentences indexed: {index.ntotal}")
    return index

def querying_index(query_sentence, new_entries=None, field_to_index=""):
    #get faiss index
    index = get_faiss_index(new_entries, field_to_index)

    # Define a query sentence
    query_embedding = model.encode([query_sentence])

    # Perform the search
    k = 5  # Number of nearest neighbors to retrieve
    distances, indices = index.search(query_embedding, k)

    # Display the results
    print(f"Query: {query_sentence}")
        
    metadata_dicts = get_metadata()

    return [
    {
        "metadata": metadata_dicts[idx],
        "distance": distances[0][i]
    }
    for i, idx in enumerate(indices[0])
]

def debug_check_alignment():
    index = faiss.read_index("files/index.faiss")
    metadata = get_metadata()
    assert index.ntotal == len(metadata), "Mismatch between FAISS index and metadata lines!"
    print("✅ FAISS and metadata are aligned.")

# debug_check_alignment()