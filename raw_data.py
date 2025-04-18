import requests

def get_url_data(url):
    raw_data = requests.get(url, timeout=1)

    if raw_data.status_code != requests.codes.ok:
        raise Exception("Servidor indisponivel, tente novamente.")
    
    return raw_data