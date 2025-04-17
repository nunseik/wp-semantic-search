import requests
import csv

r = requests.get('https://www2.itanhaem.sp.gov.br/wp-json/wp/v2/posts', timeout=1)

if r.status_code != requests.codes.ok:
    raise Exception("Servidor indisponivel, tente novamente.")

print(r.json()[0].keys())

# with open('news.csv', newline='') as csvfile:
#     reader = csv.DictReader(csvfile)
#     first_row = next(reader)
#     print(int(first_row['id']))

# count = 0
# list_ids = []
# for i in range(len(r.json())):
#     list_ids.append(r.json()[i]['id'])

# while list_ids[count] != int(first_row['id']):
#     print(list_ids[count], int(first_row['id']))
#     count += 1

# print(count)

# with open('news.csv', 'a', newline='') as csvfile:
#     fieldnames = list(r.json()[0].keys())
#     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#     writer.writerows(r.json()[:count])

with open('news.csv', 'w', newline='') as csvfile:
    fieldnames = list(r.json()[0].keys())
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(r.json()[::-1])