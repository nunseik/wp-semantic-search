import requests
from datetime import datetime


def format_context(answers):
    """Numbered articles with their matching passages; the numbers are what the answer cites."""
    blocks = []
    for n, answer in enumerate(answers, 1):
        meta = answer["metadata"]
        header = f"[{n}] {meta.get('title') or '(sem título)'}"
        if meta.get("modified"):
            header += f" ({meta['modified'][:10]})"
        if meta.get("link"):
            header += f"\nLink: {meta['link']}"
        passages = "\n[...]\n".join(answer["passages"])
        blocks.append(f"{header}\nTrechos:\n{passages}")
    return "\n\n".join(blocks)


def format_sources(answers):
    lines = ["📚 Fontes:"]
    for n, answer in enumerate(answers, 1):
        meta = answer["metadata"]
        lines.append(f"  [{n}] {meta.get('title') or '(sem título)'} — {meta.get('link', '')}")
    return "\n".join(lines)


def run_llama3(answers, pergunta):
    today_date = datetime.today().strftime('%Y-%m-%d')
    prompt = (
        f"Artigos:\n\n{format_context(answers)}\n\n"
        f"Hoje é dia {today_date}.\n"
        "Responda à pergunta do usuário usando apenas os artigos acima. "
        "Cite a fonte de cada informação com o número do artigo, por exemplo [1] ou [2][3]. "
        "Se os artigos não tiverem a resposta, diga que não encontrou essa informação.\n\n"
        f"Pergunta: {pergunta}\n"
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
    # imported here so the Ollama backend works without an OpenAI key
    from openai import OpenAI
    from api_key import openai_key

    client = OpenAI(api_key=openai_key)
    today_date = datetime.today()
    dados = format_context(answers)

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
