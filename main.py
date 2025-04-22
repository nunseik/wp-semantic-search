from raw_data import get_url_data
from new_entries import find_new_entries
from csv_creator import csv_creator
from database_creator import save_clean_contents, save_metadata_dicts, querying_index
from llm_agent import run_llama3, extract_keywords, run_openai_chat
import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"
fieldnames = ('id', 'modified', 'title', 'slug', 'content')
url="https://www2.itanhaem.sp.gov.br/wp-json/wp/v2/posts"
articles_per_page = 100
pages = 10

def main():
    # get raw data from url (list of dicts)
    raw_data = get_url_data(url, articles_per_page, pages)
    # find new entries if news.csv already exist
    new_entries = find_new_entries(raw_data)
    # create a csv file/ update a csv with new entries
    csv_creator(raw_data, new_entries, fieldnames)

    save_metadata_dicts(new_entries)
    save_clean_contents(new_entries)

    print("🤖 Assistente da Prefeitura de Itanhaém")
    print("Digite sua pergunta ou 'sair' para encerrar.\n")

    while True:
        user_input = input("👤 Você: ")

        if user_input.lower() in ["sair", "exit", "quit"]:
            print("👋 Até logo!")
            break

        # query_sentence = extract_keywords(user_input)

        answers = querying_index(user_input, new_entries)

        response = run_llama3(answers, user_input)
        # response = run_openai_chat(answers, user_input)

        print(f"\n🤖 Assistente:\n{response}\n")

if __name__ == '__main__':
    main()