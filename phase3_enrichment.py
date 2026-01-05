"""
phase3_enrichment.py

PHASE 3 ENRICHMENT (FREE SIGNALS ONLY)

Adds:
- Non-Google review platform detection (Yelp, Facebook, Avvo, Justia)
- Social presence signals
- Backlink indicators (free heuristics)
- Ads presence signals
- Hiring growth signals
"""

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def enrich_phase3(row: dict) -> dict:
    url = row.get("url", "")
    if not url:
        return row

    row.setdefault("non_google_reviews", "")
    row.setdefault("social_presence_score", "")
    row.setdefault("backlink_signal", "")
    row.setdefault("ads_library_signal", "")
    row.setdefault("hiring_growth_signal", "")

    try:
        resp = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0"
        })
        html = resp.text.lower()

        platforms = []
        for p in ["yelp.com", "facebook.com", "avvo.com", "justia.com"]:
            if p in html:
                platforms.append(p.split(".")[0])

        row["non_google_reviews"] = "; ".join(sorted(set(platforms)))

        social_hits = sum(1 for p in ["facebook.com", "instagram.com", "linkedin.com", "twitter.com"] if p in html)
        row["social_presence_score"] = social_hits

        backlink_hits = sum(1 for p in ["href="http", "href="https"] if p in html)
        row["backlink_signal"] = backlink_hits

        ads = []
        if "adsbygoogle" in html:
            ads.append("google_ads")
        if "facebook pixel" in html or "fbq(" in html:
            ads.append("meta_ads")

        row["ads_library_signal"] = "; ".join(ads)

        hiring = []
        for kw in ["careers", "jobs", "join our team", "hiring"]:
            if kw in html:
                hiring.append(kw)

        row["hiring_growth_signal"] = "; ".join(hiring)

    except Exception:
        pass

    return row
