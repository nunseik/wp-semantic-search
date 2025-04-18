import requests
import csv
import os

#Constants
fieldnames = ('id', 'modified', 'slug', 'content')
url="https://www2.itanhaem.sp.gov.br/wp-json/wp/v2/posts?per_page=20&page=1"

def get_url_data(url):
    raw_data = requests.get(url, timeout=1)

    if raw_data.status_code != requests.codes.ok:
        raise Exception("Servidor indisponivel, tente novamente.")
    
    return raw_data

def find_new_entries(raw_data):
    if os.path.exists("last_id.txt"):
        with open('last_id.txt', 'r') as txtfile:
            last_id = int(txtfile.read())
    elif os.path.exists("news.csv"):
        with open('news.csv', 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                last_id = int(row['id'])
    else:
        return []

    count = 0
    list_ids = []
    for i in range(len(raw_data.json())):
        list_ids.append(raw_data.json()[i]['id'])

    while list_ids[count] != last_id:
        print(f"new id: {list_ids[count]}, last id: {last_id}")
        count += 1

    print(f"Found {count} new entries")

    return raw_data.json()[:count]

def create_last_id_file(raw_data):
    with open('last_id.txt', 'w') as txtfile:
            txtfile.write(str(raw_data.json()[0]['id']))

def csv_creator(raw_data, new_entries, fieldnames):
    if os.path.exists("news.csv"):

        with open('news.csv', 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            writer.writerows(new_entries[::-1])

    else:
        with open('news.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(raw_data.json()[::-1])
        
    create_last_id_file(raw_data)

def get_new_entries_dict(new_entries, fieldnames):
    new_entries_lst = []
    for entry in new_entries:
        new_entry_dict = {key: entry[key] for key in fieldnames}
        new_entries_lst.append(new_entry_dict)
    return new_entries_lst

raw_data = get_url_data(url=url)
new_entries = find_new_entries(raw_data)
csv_creator(raw_data, new_entries, fieldnames)

new_entries_lst = get_new_entries_dict(new_entries, fieldnames)
for dict in new_entries_lst:
    print(dict)