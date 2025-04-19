from raw_data import get_url_data
from new_entries import find_new_entries, get_new_entries_dict
from csv_creator import csv_creator

fieldnames = ('id', 'modified', 'title', 'slug', 'content')
url="https://www2.itanhaem.sp.gov.br/wp-json/wp/v2/posts?per_page=20&page=1"

def main():
    # get raw data from url (list of dicts)
    raw_data = get_url_data(url=url)
    # find new entries if news.csv already exist
    new_entries = find_new_entries(raw_data)
    # create a csv file/ update a csv with new entries
    csv_creator(raw_data, new_entries, fieldnames)

    # get new entries filtered by fieldnames and return a list of dictionaries
    new_entries_lst = get_new_entries_dict(new_entries, fieldnames)
    for dict in new_entries_lst:
        print(dict) #printing new entries in dict format

if __name__ == '__main__':
    main()