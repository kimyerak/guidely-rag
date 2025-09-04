#!/usr/bin/env python3
"""
fetch_arxiv_links_by_field.py
---------------------------------
Fetch the top‑cited arXiv papers for eight disciplines and save them as a single
text file organised by field headings.  Requires Python 3.8+ and the 'requests'
and 'tqdm' packages.

Usage:
    $ pip install requests tqdm
    $ python fetch_arxiv_links_by_field.py

The script writes `arxiv_links_by_field.txt` in the current directory, with
eight sections (Communication, Life Sciences, Semiconductor, Chemistry,
Earth Science, Physics, Mathematics, Logic) and 100 links in each section,
using an approximate "≥10 000 citations" threshold.  It queries the open
OpenAlex API, so an Internet connection is required.
"""

import requests, time, json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from tqdm import tqdm

# -----------------------------------------------
# Settings – concept IDs for each requested field
# -----------------------------------------------
FIELDS = {
    # Display name          OpenAlex concept IDs (comma‑sep)
    "Communication":        ["C2779782262", "C111664753", "C2780236457"],   # Information theory, Wireless comms, Signal processing
    "Life Sciences":        ["C86803240", "C75106024", "C126322002"],        # Biology, Neuroscience, Bioinformatics
    "Semiconductor":        ["C121332964", "C3313618474", "C2675089202"],    # Semiconductor, Nanotechnology, Electronic engineering
    "Chemistry":            ["C185592680", "C8820508", "C104317684"],        # Chemistry, Physical chemistry, Organic chemistry
    "Earth Science":        ["C71924100", "C2680935589", "C154945302"],      # Earth science, Atmospheric science, Geophysics
    "Physics":              ["C121332964", "C12819563", "C134018473"],       # Physics, Particle physics, Quantum mechanics
    "Mathematics":          ["C33923547"],                                    # Mathematics
    "Logic":                ["C162929596", "C17744445"]                      # Mathematical logic, Set theory
}

MAX_PER_FIELD = 100    # links we want
API_BASE = "https://api.openalex.org/works"
ARXIV_HOST_FILTER = "primary_location.source.host_url:https://arxiv.org"
PER_PAGE = 200         # OpenAlex maximum
HEADERS = {
    "User-Agent": "fetch_arxiv_links_by_field.py (nrbsld@korea.ac.kr)"  # ← 본인 이메일 넣기
}
def fetch_top_arxiv(concepts):
    """Return list of arXiv IDs (as strings) for the given concept IDs."""
    cursor = "*"
    results = []
    while len(results) < MAX_PER_FIELD and cursor:
        # Build filter string
        concept_filter = ",".join(f"concept.id:{cid}" for cid in concepts)
        flt = f"{ARXIV_HOST_FILTER},{concept_filter}"
        url = f"{API_BASE}?filter={flt}&sort=cited_by_count:desc&per_page={PER_PAGE}&cursor={cursor}"
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        data = r.json()
        for w in data["results"]:
            # Extract any arXiv ID from the locations
            arxiv_id = None
            for loc in w.get("locations", []):
                url = loc.get("source", {}).get("host_url", "")
                if "arxiv.org" in url:
                    pdf = loc.get("pdf_url") or loc.get("landing_page_url") or ""
                    if "arxiv.org" in pdf:
                        arxiv_id = pdf.split("/")[-1].replace(".pdf", "")
                        break
            if arxiv_id and arxiv_id not in results:
                results.append(arxiv_id)
                if len(results) >= MAX_PER_FIELD:
                    break
        cursor = data["meta"].get("next_cursor")
        if not cursor:
            break
        time.sleep(0.2)    # be nice to the API
    return results

def main():
    master = []
    for field, concept_ids in FIELDS.items():
        print(f"Fetching {field:>14} ...", end=" ")
        ids = fetch_top_arxiv(concept_ids)
        print(f"{len(ids)} IDs")
        master.append((field, ids))
    # Write master file
    out_path = Path("arxiv_links_by_field.txt")
    with out_path.open("w", encoding="utf-8") as f:
        for field, ids in master:
            f.write(f"## {field}\n")
            for arxiv_id in ids:
                f.write(f"https://arxiv.org/pdf/{arxiv_id}\n")
            f.write("\n")
    print("\nDone →", out_path.resolve())

if __name__ == "__main__":
    main()
