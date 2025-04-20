import requests

def get_url_data(url):
    raw_data = requests.get(url, timeout=10)

    if raw_data.status_code != requests.codes.ok:
        raise Exception("Servidor indisponivel, tente novamente.")
    
    return raw_data

'''
IDEAS: 
    We can create a for loop to get as many posts as we want by adding the field ?per_page=20&page=1 after the link
    For example:
    
    raw_data = [] #starts a empty list
    For i in range(1, 11): # get the first ten pages
        url = f"https://www2.itanhaem.sp.gov.br/wp-json/wp/v2/posts?per_page=100&page={i}"
        raw_data_page = requests.get(url, timeout=1)
        raw_data.extend(raw_data_page)
    
    Now, raw_data will contain 1000 entries.
'''