import requests
import time
import os

def get_url_data(base_url, articles_per_page=10, pages=1):
    if os.path.exists("files/news.csv"):
        response = requests.get(base_url+"wp-json/wp/v2/posts", timeout=10)

        if response.status_code != requests.codes.ok:
            raise Exception(f"Erro ao acessar página {base_url}: {response.status_code}")
        
        return response.json()
    
    all_articles = []

    for i in range(1, pages + 1):
        page_url = f"{base_url}wp-json/wp/v2/posts?per_page={articles_per_page}&page={i}"
        print(f"Fetching page {i}: {page_url}")

        response = requests.get(page_url, timeout=10)

        if response.status_code != requests.codes.ok:
            raise Exception(f"Erro ao acessar página {i}: {response.status_code}")

        data = response.json()

        if not data:
            print("Página vazia, encerrando busca.")
            break

        all_articles.extend(data)

        time.sleep(1)

    return all_articles