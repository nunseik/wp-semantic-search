from csv_reader import get_csv_content
import json
from sentence_transformers import SentenceTransformer
import faiss
import os

def get_clean_contents():
    list_contents = get_csv_content()
    if list_contents == []:
        return []
    clean_contents = [row['content'] for row in list_contents]
    return clean_contents

def save_metadata_dicts():
    list_contents = get_csv_content()

    if list_contents == []:
        return []
    
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

clean_contents = get_clean_contents()
model = SentenceTransformer('all-MiniLM-L6-v2')  # Or another model

if os.path.exists("files/news_index.faiss"):
    index = faiss.read_index("files/news_index.faiss")
else:
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

# Define a query sentence
query_sentence = "aniversario"
query_embedding = model.encode([query_sentence])

# Perform the search
k = 3  # Number of nearest neighbors to retrieve
distances, indices = index.search(query_embedding, k)

# Display the results
print(f"Query: {query_sentence}")

print("Most similar sentences:")
metadata_dicts = get_metadata_dicts()
for i, idx in enumerate(indices[0]):
    print(f"{i + 1}: {clean_contents[idx]} (Distance: {distances[0][i]}) meta: {metadata_dicts[idx]}")