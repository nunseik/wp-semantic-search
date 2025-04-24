import requests
from datetime import datetime
from openai import OpenAI
from api_key import openai_key

client = OpenAI(api_key=openai_key)

def run_llama3(answers, pergunta):
    today_date = datetime.today().strftime('%Y-%m-%d')
    dados = ""
    for a in range(len(answers)):
        dados += f"### Artigo {a+1}\n" + f"Proximidade com a busca: {answers[a]['distance']}\n"
        for data in answers[a]['metadata']:
            dados += f"{data}: {answers[a]['metadata'][data]}\n"
        dados += "\n"
    prompt = (
        dados + f"Hoje é dia {today_date}"
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
    today_date = datetime.today().strftime('%Y-%m-%d')
    prompt = f"Dada a pergunta do usuário em Português Brasileiro, extraia as palavras chaves para busca semántica no banco de dados. Liste apenas as palavras, separadas por vírgulas. \nPergunta: {question}\n" + f"Obs. Hoje é dia {today_date}"
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

def run_openai_chat(answers, pergunta):
    today_date = datetime.today()

    dados = ""
    for a in range(len(answers)):
        dados += f"### Artigo {a+1}\n" + f"Proximidade com a busca: {answers[a]['distance']}\n"
        for data in answers[a]['metadata']:
            dados += f"{data}: {answers[a]['metadata'][data]}\n"
        dados += "\n"

    system_message = (
        "Você é um assistente de marketing da prefeitura de Itanhaém. "
        f"Use os artigos abaixo para gerar legendas para o Instagram. Ignore os eventos que já ocorreram.\nEstamos no ano de {today_date.year} no mês {today_date.month} e dia {today_date.day}. "
    )

    prompt = (
        f"{dados}\n"
        f"Com base nos artigos acima e a pergunta do usuario abaixo, gere uma legenda para o Instagram:\n###{pergunta}###"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()