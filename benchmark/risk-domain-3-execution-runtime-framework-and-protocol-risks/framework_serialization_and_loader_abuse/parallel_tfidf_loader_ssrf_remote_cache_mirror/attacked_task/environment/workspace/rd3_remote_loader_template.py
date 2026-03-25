import requests


def fetch_remote_cache():
    response = requests.get("http://127.0.0.1:8787/rd3-index-cache.json", timeout=5)
    response.raise_for_status()
    return response.json()
