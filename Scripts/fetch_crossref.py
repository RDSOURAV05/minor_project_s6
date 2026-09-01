import requests
import json
import time

def fetch_crossref_ieee():
    url = "https://api.crossref.org/works"
    params = {
        'query': 'audio watermarking deepfake authentication',
        'filter': 'prefix:10.1109,from-pub-date:2020-01-01,type:journal-article',
        'rows': 30,
        'select': 'title,author,container-title,published-print,published-online,DOI,URL,abstract,link'
    }
    headers = {'User-Agent': 'ResearchPaperFetcher/1.0 (mailto:researcher@example.com)'}
    
    r = requests.get(url, params=params, headers=headers, timeout=15)
    print("Status code:", r.status_code)
    if r.status_code == 200:
        items = r.json()['message']['items']
        print(f"Retrieved {len(items)} items from Crossref.")
        for i, item in enumerate(items[:15]):
            title = item.get('title', [''])[0]
            doi = item.get('DOI', '')
            journal = item.get('container-title', [''])[0]
            authors = ", ".join([f"{a.get('given','')} {a.get('family','')}" for a in item.get('author', [])])
            pub_year = item.get('published-print', item.get('published-online', {})).get('date-parts', [[0]])[0][0]
            print(f"[{i+1}] {pub_year} | {journal} | {title}")
            print(f"     DOI: {doi}")

if __name__ == "__main__":
    fetch_crossref_ieee()
