import os
import csv

def find_new_entries(raw_data):
    if os.path.exists("files/last_id.txt"):
        with open('files/last_id.txt', 'r') as txtfile:
            last_id = int(txtfile.read())
    elif os.path.exists("files/news.csv"):
        with open('files/news.csv', 'r') as csvfile:
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

def get_new_entries_dict(new_entries, fieldnames):
    new_entries_lst = []
    for entry in new_entries:
        new_entry_dict = {key: entry[key] for key in fieldnames}
        new_entries_lst.append(new_entry_dict)
    return new_entries_lst