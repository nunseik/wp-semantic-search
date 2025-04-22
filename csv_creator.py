import os
import csv

def create_last_id_file(raw_data):
    with open('files/last_id.txt', 'w') as txtfile:
            txtfile.write(str(raw_data[0]['id']))

def csv_creator(raw_data, new_entries, fieldnames):
    if os.path.exists("files/news.csv"):

        with open('files/news.csv', 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            writer.writerows(new_entries[::-1])

    else:
        with open('files/news.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(raw_data[::-1])
        
    create_last_id_file(raw_data)