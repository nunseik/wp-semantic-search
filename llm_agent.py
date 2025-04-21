import requests

def run_llama3(answers, pergunta):
    dados = ""
    for a in range(len(answers)):
        dados += f"Esse é o artigo numero {a}\n" + f"distancia do vetor:{answers[a]["distance"]}\n" + f"titulo:{answers[a]["metadata"]["title"]}\n" + f"conteudo:{answers[a]["content"]}\n\n"
    prompt = dados + "Considerando os artigos fornecidos, responda a seguinte pergunta do usuario: \n" + pergunta
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