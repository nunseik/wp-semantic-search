import requests

def run_llama3(answers, pergunta):
    dados = ""
    for a in range(len(answers)):
        dados += f"### Artigo {a+1}\n" + f"Distancia:{answers[a]['distance']}\n" + f"Titulo:{answers[a]['metadata']['title']}\n" + f"Slug:{answers[a]['metadata']['slug']}\n" + f"Conteudo:{answers[a]['content']}\n\n"
    prompt = (
        dados +
        f"Com base nos artigos acima, responda à pergunta do usuário:\n{pergunta}\n"
    )
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False
        }
    )
    response.raise_for_status()
    return response.json()["response"]

def extract_keywords(question):
    prompt = f"Dada a pergunta do usuario, extraia as palavras chaves para busca semantica no banco de dados. Liste apenas as palavras, separadas por vírgulas. \nPergunta: {question}"
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False
        }
    )
    raw_output = response.json()["response"]
    keywords = [kw.strip().lower() for kw in raw_output.replace('"', '').split(",") if kw.strip()]
    return " ".join(keywords)

