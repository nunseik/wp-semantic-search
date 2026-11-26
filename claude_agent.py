"""Claude backend: answers from the retrieved articles with API-verified citations.

Each retrieved article is sent as a plain-text document with citations enabled, so the
response comes back as text blocks carrying the exact passages they rely on. The [n]
markers in the answer are built from those citations (document n = source [n] in the
CLI's source list), not from numbers the model typed.

Credentials come from the environment (ANTHROPIC_API_KEY, or an `ant auth login` profile).
"""
import os
from datetime import datetime

MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-5-5")
EFFORT = os.environ.get("CLAUDE_EFFORT", "medium")

SYSTEM = (
    "Você é o assistente de notícias da Prefeitura de Itanhaém. "
    "Responda em português do Brasil, de forma curta e direta, usando apenas os artigos fornecidos. "
    "Se os artigos não tiverem a resposta, diga que não encontrou essa informação nas notícias, "
    "sem completar com conhecimento próprio. "
    "Atenção às datas: diga quando um evento já passou em relação à data de hoje."
)

_client = None


def get_client():
    global _client
    if _client is None:
        import anthropic
        _client = anthropic.Anthropic()
    return _client


def build_documents(answers):
    docs = []
    for answer in answers:
        meta = answer["metadata"]
        context = " | ".join(
            part for part in (f"Atualizado em {meta['modified'][:10]}" if meta.get("modified") else "",
                              meta.get("link", "")) if part
        )
        doc = {
            "type": "document",
            "source": {"type": "text", "media_type": "text/plain", "data": "\n\n".join(answer["passages"])},
            "title": (meta.get("title") or "(sem título)")[:250],
            "citations": {"enabled": True},
        }
        if context:
            doc["context"] = context
        docs.append(doc)
    return docs


def render_answer(content):
    """Join the text blocks, adding [n] after each cited span (n = document_index + 1)."""
    parts = []
    for block in content:
        if getattr(block, "type", None) != "text":
            continue  # thinking / fallback blocks are not part of the answer
        parts.append(block.text)
        numbers = sorted({c.document_index + 1 for c in (getattr(block, "citations", None) or [])})
        if numbers:
            parts.append("".join(f"[{n}]" for n in numbers))
    return "".join(parts).strip()


def run_claude(answers, pergunta):
    import anthropic

    if not answers:
        return "Não encontrei notícias relacionadas a essa pergunta."

    today = datetime.today().strftime("%Y-%m-%d")
    try:
        response = get_client().beta.messages.create(
            model=MODEL,
            max_tokens=16000,
            output_config={"effort": EFFORT},
            # on a safety decline, the API retries the request on a fallback model it picks
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            system=SYSTEM,
            messages=[{
                "role": "user",
                "content": build_documents(answers) + [
                    {"type": "text", "text": f"Hoje é {today}.\n\nPergunta: {pergunta}"}
                ],
            }],
        )
    except anthropic.AuthenticationError:
        return "⚠️ Claude: credenciais inválidas ou ausentes. Defina ANTHROPIC_API_KEY."
    except anthropic.RateLimitError:
        return "⚠️ Claude: limite de requisições atingido, tente de novo em instantes."
    except anthropic.APIStatusError as e:
        return f"⚠️ Claude: erro da API ({e.status_code}): {e.message}"
    except anthropic.APIConnectionError:
        return "⚠️ Claude: sem conexão com a API."

    if response.stop_reason == "refusal":
        return "⚠️ Claude recusou responder a essa pergunta."

    answer = render_answer(response.content)
    if response.stop_reason == "max_tokens":
        answer += "\n(resposta cortada no limite de tamanho)"
    return answer
