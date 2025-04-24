import os
from database_creator import get_metadata

def find_new_entries(raw_data):
    last_id = None

    if os.path.exists("files/last_id.txt"):
        with open('files/last_id.txt', 'r') as txtfile:
            last_id = int(txtfile.read())

    elif os.path.exists("files/news_meta.jsonl"):
        metadata = get_metadata()
        last_id = metadata[0]['id']

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