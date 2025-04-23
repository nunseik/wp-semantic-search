from csv_reader import get_csv_content, get_new_entries_field
import json
from sentence_transformers import SentenceTransformer
import faiss
import os

model = SentenceTransformer('all-MiniLM-L6-v2')  # Or another model

def get_new_contents(new_entries=None, field_to_index=""):
    if not new_entries:
        return None
    
    new_list_contents = get_new_entries_field(new_entries, field_to_index)
    return [row[field_to_index] for row in new_list_contents]

def save_clean_field(new_entries=None, field_to_index=""):
    if os.path.exists("files/indexed_field.jsonl"):
        if not new_entries:
            return
        new_clean_contents = get_new_contents(new_entries, field_to_index)

        with open("files/indexed_field.jsonl", "a", encoding="utf-8") as f:
            for text in new_clean_contents:
                f.write(text.strip() + "\n")

    else:
        list_contents = get_csv_content(field_to_index)

        if list_contents == []:
            return []
        
        clean_contents = [row[field_to_index] for row in list_contents]
        
        with open("files/indexed_field.jsonl", "w", encoding="utf-8") as f:
            for text in clean_contents:
                f.write(text.strip() + "\n")

def get_clean_field():
    with open("files/indexed_field.jsonl", "r", encoding="utf-8") as f:
        return [line.strip() for line in f]


def save_metadata(new_entries=None, field_to_index=""):
    if os.path.exists("files/news_meta.jsonl"):
        if not new_entries:
            return
        new_list_contents = get_new_entries_field(new_entries, field_to_index)

        new_metadata_dicts = [{'id':row['id'], 'modified':row['modified'],'title':row['title'], 'slug':row['slug']} for row in new_list_contents]

        with open("files/news_meta.jsonl", "a", encoding="utf-8") as outfile:
            for row in new_metadata_dicts:
                json.dump(row, outfile, ensure_ascii=False)
                outfile.write("\n")
    else:
        list_contents = get_csv_content(field_to_index)
        
        metadata_dicts = [{'id':row['id'], 'modified':row['modified'],'title':row['title'], 'slug':row['slug']} for row in list_contents]

        with open("files/news_meta.jsonl", "w", encoding="utf-8") as outfile:
            for row in metadata_dicts:
                json.dump(row, outfile, ensure_ascii=False)
                outfile.write("\n")

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
        clean_contents = get_clean_field()
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
    k = 3  # Number of nearest neighbors to retrieve
    distances, indices = index.search(query_embedding, k)

    # Display the results
    print(f"Query: {query_sentence}")
        
    metadata_dicts = get_metadata()
    clean_contents = get_clean_field()

    return [
    {
        "content": clean_contents[idx],
        "metadata": metadata_dicts[idx],
        "distance": distances[0][i]
    }
    for i, idx in enumerate(indices[0])
]