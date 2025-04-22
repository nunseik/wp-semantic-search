import os
import csv

def find_new_entries(raw_data):
    last_id = None

    if os.path.exists("files/last_id.txt"):
        with open('files/last_id.txt', 'r') as txtfile:
            last_id = int(txtfile.read())

    elif os.path.exists("files/news.csv"):
        with open('files/news.csv', 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                last_id = int(row['id'])

    # Exit early if we couldn't determine the last ID
    if last_id is None:
        return []

    # Compare IDs
    count = 0
    list_ids = [entry['id'] for entry in raw_data]

    # Safety check in case the last_id is no longer present in the feed
    if last_id not in list_ids:
        print("⚠️ last_id not found in current data. Possibly outdated?")
        return []

    while list_ids[count] != last_id:
        print(f"new id: {list_ids[count]}, last id: {last_id}")
        count += 1

    print(f"Found {count} new entries")
    return raw_data[:count]

#get_new_entries_dict is going to be used to add new entries to a vectorized database without worrying about the CSV file

def get_new_entries_dict(new_entries, fieldnames):
    new_entries_lst = []
    for entry in new_entries:
        new_entry_dict = {key: entry[key] for key in fieldnames}
        new_entries_lst.append(new_entry_dict)
    return new_entries_lst