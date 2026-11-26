from raw_data import get_url_data
from new_entries import find_new_entries
from config import DB_FILES
from database_creator import save_metadata, get_faiss_index, querying_index
from llm_agent import run_llama3, extract_keywords, run_openai_chat, format_sources
from claude_agent import run_claude
import os
import argparse

#disabling a harmless warning from huggingface/tokenizers
os.environ["TOKENIZERS_PARALLELISM"] = "false"

#set what fieldnames we get from the url & other settings to get raw data
fieldnames = ('id', 'modified', 'title', 'link', 'content') # check your url with /wp-json/wp/v2/posts to see what fieldnames you want
url="https://www2.itanhaem.sp.gov.br/" #accepts any Wordpress website
articles_per_page = 100 #DO NOT exceed 100 articles per page
pages = 1

#set fields to be indexed
field_to_index = "content" # full article text, split into chunks

def main():
    parser = argparse.ArgumentParser(description="Run semantic assistant for WordPress sites")
    parser.add_argument(
        "--model",
        choices=["ollama", "openai", "claude"],
        default="ollama",
        help="Choose which LLM backend to use: 'ollama', 'openai' or 'claude' (default: ollama)"
    )
    parser.add_argument(
        "--refresh",
        action='store_true',
        help="Refresh your databa with a new collection of articles"
    )
    args = parser.parse_args()

    if args.refresh:
        print("🧹 Refreshing the local database...")
        for file in DB_FILES:
            if os.path.exists(file):
                os.remove(file)
                print(f"✅ Deleted: {file}")
            else:
                print(f"⚠️ Skipped (not found): {file}")

    # get raw data from url (list of dicts)
    raw_data = get_url_data(url, articles_per_page, pages)

    # find new entries if news.csv already exist
    new_entries = find_new_entries(raw_data)

    # save metadata jsonl
    save_metadata(raw_data, new_entries, fieldnames)

    # build or update the index once; new entries must not be re-added on every question
    index = get_faiss_index(new_entries, field_to_index)

    print("🤖 Assistente da Prefeitura de Itanhaém")
    print("Digite sua pergunta ou 'sair' para encerrar.\n")

    while True:
        user_input = input("👤 Você: ")

        if user_input.lower() in ["sair", "exit", "quit"]:
            print("👋 Até logo!")
            break

        # query_sentence = extract_keywords(user_input)

        # top 5 articles, each with the passages that matched the question
        answers = querying_index(user_input, index)

        if args.model == "openai":
            response = run_openai_chat(answers, user_input)
        elif args.model == "claude":
            response = run_claude(answers, user_input)
        else:
            response = run_llama3(answers, user_input)

        print(f"\n🤖 Assistente:\n{response}\n")
        print(format_sources(answers) + "\n")

if __name__ == '__main__':
    main()

'''
### TO DO LIST
- Add the logic to keep history in conversation so users can request more info from it
- Add a function/script to clean database and refresh
'''