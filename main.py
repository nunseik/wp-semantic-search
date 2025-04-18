import requests
import csv
import os

r = requests.get('https://www2.itanhaem.sp.gov.br/wp-json/wp/v2/posts', timeout=1)

if r.status_code != requests.codes.ok:
    raise Exception("Servidor indisponivel, tente novamente.")

if os.path.exists("news.csv"):

    with open('last_id.txt', 'r') as txtfile:
        last_id = int(txtfile.read())

    count = 0
    list_ids = []
    for i in range(len(r.json())):
        list_ids.append(r.json()[i]['id'])

    while list_ids[count] != last_id:
        print(list_ids[count], last_id)
        count += 1

    print(count)

    with open('news.csv', 'a', newline='') as csvfile:
        fieldnames = list(r.json()[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerows(r.json()[:count][::-1])
    
    with open('last_id.txt', 'w') as txtfile:
        txtfile.write(str(r.json()[0]['id']))

else:
    with open('news.csv', 'w', newline='') as csvfile:
        fieldnames = list(r.json()[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(r.json()[::-1])
    
    with open('last_id.txt', 'w') as txtfile:
        txtfile.write(str(r.json()[0]['id']))