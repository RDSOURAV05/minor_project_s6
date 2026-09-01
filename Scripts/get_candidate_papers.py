import requests
import json
import re
import os
import time

def fetch_ieee_papers():
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    queries = [
        "audio watermarking IEEE",
        "audio deepfake watermark IEEE",
        "audio tamper localization IEEE",
        "deepfake audio detection IEEE",
        "acoustic watermarking neural network IEEE",
        "robust audio watermarking wavelet IEEE"
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    collected = []
    seen_titles = set()

    for q in queries:
        params = {
            'query': q,
            'limit': 20,
            'fields': 'title,authors,venue,year,externalIds,publicationTypes,abstract,openAccessPdf,url'
        }
        try:
            r = requests.get(url, params=params, headers=headers, timeout=10)
            if r.status_code == 200:
                data = r.json()
                for item in data.get('data', []):
                    title = item.get('title', '')
                    year = item.get('year', 0)
                    venue = item.get('venue', '')
                    ext_ids = item.get('externalIds', {})
                    doi = ext_ids.get('DOI', '')
                    
                    # Must be published between 2020 and 2026
                    if year and 2020 <= year <= 2026:
                        # Check if IEEE journal/venue or DOI contains 10.1109
                        is_ieee = 'IEEE' in venue.upper() or '10.1109' in doi or 'IEEE' in title.upper()
                        if is_ieee and title.lower() not in seen_titles:
                            seen_titles.add(title.lower())
                            collected.append(item)
        except Exception as e:
            print(f"Error querying {q}: {e}")
        time.sleep(1)

    print(f"Found {len(collected)} IEEE candidate papers.")
    return collected

if __name__ == "__main__":
    candidates = fetch_ieee_papers()
    for i, c in enumerate(candidates[:15]):
        print(f"[{i+1}] {c.get('year')} - {c.get('venue')} - {c.get('title')}")
        print(f"     DOI: {c.get('externalIds', {}).get('DOI')}")
        print(f"     PDF: {c.get('openAccessPdf')}")
