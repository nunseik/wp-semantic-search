from raw_data import get_url_data
from new_entries import find_new_entries
from database_creator import save_metadata, querying_index
from llm_agent import run_llama3, extract_keywords, run_openai_chat
import os

#disabling a harmless warning from huggingface/tokenizers
os.environ["TOKENIZERS_PARALLELISM"] = "false"

#set what fieldnames we get from the url & other settings to get raw data
fieldnames = ('id', 'modified', 'title', 'slug', 'content') # check your url with /wp-json/wp/v2/posts to see what fieldnames you want
url="https://www2.itanhaem.sp.gov.br/" #accepts any Wordpress website
articles_per_page = 100 #DO NOT exceed 100 articles per page
pages = 2

#set fields to be indexed
field_to_index = "content"

def main():
    # get raw data from url (list of dicts)
    raw_data = get_url_data(url, articles_per_page, pages)

    # find new entries if news.csv already exist
    new_entries = find_new_entries(raw_data)

    # save metadata jsonl
    save_metadata(raw_data, new_entries, field_to_index, fieldnames)

    print("🤖 Assistente da Prefeitura de Itanhaém")
    print("Digite sua pergunta ou 'sair' para encerrar.\n")

    while True:
        user_input = input("👤 Você: ")

        if user_input.lower() in ["sair", "exit", "quit"]:
            print("👋 Até logo!")
            break

        # query_sentence = extract_keywords(user_input)

        # querying index returns the top 3 articles in the faiss database
        answers = querying_index(query_sentence=user_input, new_entries=new_entries, field_to_index=field_to_index)

        response = run_llama3(answers, user_input)
        # response = run_openai_chat(answers, user_input)

        print(f"\n🤖 Assistente:\n{response}\n")

if __name__ == '__main__':
    main()

''' 
### TO DO LIST
- Add the logic to keep history in conversation so users can request more info from it
- Test more models at model = SentenceTransformer('all-MiniLM-L6-v2')
- Test excerpt as field to index
- Add a function/script to clean database and refresh
'''