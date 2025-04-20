from html.parser import HTMLParser
import csv

class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []

    def handle_data(self, data):
        self.text_parts.append(data)

    def get_data(self):
        return ''.join(self.text_parts)

def strip_html(html):
    stripper = HTMLStripper()
    stripper.feed(html)
    return stripper.get_data()

def get_csv_content():
    list_dict = []

    with open('files/news.csv', 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    row['content'] = strip_html(row['content'])
                    list_dict.append(row)
    return list_dict

def get_new_entries_content(new_entries):
    list_dict = []
    if not new_entries:
         return
    for row in new_entries:
        row['content'] = strip_html(row['content'])
        list_dict.append(row)

    return list_dict