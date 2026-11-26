# WP Semantic Search

This is a lightweight semantic search assistant built for WordPress-based news websites. It uses sentence-transformers, FAISS, and a local or cloud-based LLM (via Ollama or OpenAI) to answer user queries using indexed news content.

---

## 🚀 Features

- Connects to any WordPress site exposing the REST API
- Extracts and cleans HTML content from articles
- Splits each article into chunks (paragraphs packed up to 120 words, long paragraphs split with overlap)
- Embeds every chunk (with its article title) using Sentence Transformers
- Stores chunk embeddings in FAISS and ranks articles by their best-matching chunk
- Answers cite their sources as [n], and the matching article links are listed after each answer
- Supports two LLM backends: **Ollama** (offline) and **OpenAI GPT-4o**
- Incremental updates: adds only new articles to the database
- Includes CLI flags for switching models and refreshing the index

---

## 📦 Installation

1. Clone the repository:

```bash
git clone https://github.com/your-user/wp-semantic-search.git
cd wp-semantic-search
```

2. (Optional) Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Install and run Ollama (if using the local LLaMA 3.2 model):

Visit https://ollama.com and follow the installation instructions for your operating system. Once installed, pull the model:

```bash
ollama pull llama3
```

Then run Ollama in the background:

```bash
ollama run llama3
```

---

## 🧐 Running the Assistant

To run the assistant:

```bash
python main.py
```

### Available CLI flags

- `--model openai` → use GPT-4o via OpenAI API
- `--model ollama` → use LLaMA 3.2B via Ollama (default)
- `--refresh` → rebuild your FAISS index and metadata from scratch

> Upgrading from an earlier version? Run once with `--refresh`: the index is now built from chunks with a different embedding model, so the old one can't be reused.

Example:

```bash
python main.py --model openai
```

---

## 🔑 OpenAI Configuration

To use OpenAI, create a file called `api_key.py` and add:

```python
openai_key = "sk-..."
```

---

## 📏 Retrieval eval

`eval/` holds a fixed snapshot of 100 articles from the Itanhaém site (June–August 2025) and 45 questions written the way residents would ask them, each with the article(s) that answer it. The eval builds a fresh index from the snapshot and checks whether those articles come back in the top 5:

```bash
python eval/run_eval.py                                       # default model
python eval/run_eval.py --model intfloat/multilingual-e5-base
```

| model | recall@5 | hit@5 | MRR | index build (100 articles, M-series CPU, model cached) |
|---|---|---|---|---|
| all-MiniLM-L6-v2 | 0.700 | 0.733 | 0.610 | 7s |
| intfloat/multilingual-e5-base (default) | 0.989 | 1.000 | 0.978 | 17s |

The site is in Portuguese and MiniLM is an English model: it finds articles that share words with the question but misses paraphrases ("camelô" vs. "ambulantes", "doar roupas de frio" vs. "Campanha do Agasalho"), which is why the multilingual E5 model is the default. GitHub Actions runs the eval for both models on every push and pull request, and fails if recall@5 drops below the baseline.

---

## ⚙️ Configuration

`config.py` holds the data folder (`WP_SEARCH_DATA`, default `files`), the embedding model (`WP_SEARCH_MODEL`, default `intfloat/multilingual-e5-base`) and the chunk size. Changing the model or chunk size needs a `--refresh`.

---

## 🗂 File Structure

- `files/news_meta.jsonl` – one row per article (ID, date, title, link, and plain-text content)
- `files/chunks.jsonl` – one row per chunk (article ID, chunk number, text); row *i* is vector *i* of the index
- `files/index.faiss` – FAISS index of normalized chunk embeddings (inner product = cosine similarity)
- `files/index_model.txt` – the embedding model that built the index (a different configured model asks for `--refresh`)
- `files/last_id.txt` – stores the last indexed article ID

---

## 💡 Future Improvements

- Add a conversation memory mode
- Support natural-language date filters (e.g. “último mês”)
- Add GUI or web interface (e.g. Streamlit or Flask)
- Create Docker image for easy deployment
- Export answers + metadata as logs
- Support additional WordPress fields (e.g., tags, categories)

---

## 📄 License

MIT License
