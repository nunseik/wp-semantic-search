# WP Semantic Search

This is a lightweight semantic search assistant built for WordPress-based news websites. It uses sentence-transformers, FAISS, and a local or cloud-based LLM (via Ollama or OpenAI) to answer user queries using indexed news content.

---

## 🚀 Features

- Connects to any WordPress site exposing the REST API
- Extracts and cleans HTML content from articles
- Embeds article content with Sentence Transformers
- Stores embeddings in FAISS for fast vector similarity search
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

## 🗂 File Structure

- `files/news_meta.jsonl` – metadata for each article (ID, date, title, slug, and content)
- `files/index.faiss` – FAISS index storing all article embeddings
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
