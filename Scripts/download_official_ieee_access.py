import requests
import json
import os
import re

from compile_papers_data import WORKSPACE, papers_data

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

for p in papers_data:
    doi = p['doi']
    # Check via Unpaywall API for open access PDF link
    unpaywall_url = f"https://api.unpaywall.org/v2/{doi}?email=student@university.edu"
    try:
        r = requests.get(unpaywall_url, headers=headers, timeout=8)
        if r.status_code == 200:
            res = r.json()
            oa_url = res.get('best_oa_location', {}).get('url_for_pdf')
            if oa_url:
                print(f"[{p['id']}] Found OA PDF URL: {oa_url}")
                pdf_res = requests.get(oa_url, headers=headers, timeout=15)
                if pdf_res.status_code == 200 and len(pdf_res.content) > 10000:
                    official_name = f"Official_IEEE_Access_Paper_{p['id']}.pdf"
                    with open(os.path.join(WORKSPACE, official_name), 'wb') as f:
                        f.write(pdf_res.content)
                    print(f"    Saved official PDF: {official_name} ({len(pdf_res.content)} bytes)")
    except Exception as e:
        print(f"[{p['id']}] Check failed: {e}")
