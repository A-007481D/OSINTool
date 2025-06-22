import requests
from bs4 import BeautifulSoup
import re
import time

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
HEADERS = {"User-Agent": USER_AGENT}

SEARCH_SITES = [
    ("LinkedIn", "site:linkedin.com/in {}"),
    ("Facebook", "site:facebook.com {}"),
    ("Twitter", "site:twitter.com {}"),
    ("Instagram", "site:instagram.com {}"),
    ("GitHub", "site:github.com {}"),
]

GOOGLE_URL = "https://www.google.com/search?q={}&num=10"


def google_search(query):
    url = GOOGLE_URL.format(requests.utils.quote(query))
    resp = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")
    results = []
    for g in soup.select("div.g"):
        title = g.find("h3")
        link = g.find("a", href=True)
        snippet = g.find("span", class_="aCOpRe")
        if title and link:
            results.append({
                "title": title.text.strip(),
                "url": link['href'],
                "snippet": snippet.text.strip() if snippet else ""
            })
    return results


def search_person(name):
    people = []
    for site, pattern in SEARCH_SITES:
        query = pattern.format(name)
        try:
            results = google_search(query)
            for r in results:
                # Try to extract photo and extra info later
                people.append({
                    "site": site,
                    "name": name,
                    "profile_url": r["url"],
                    "title": r["title"],
                    "snippet": r["snippet"],
                    "avatar_url": "",  # To be enriched
                    "location": "",    # To be enriched
                    "emails": re.findall(r"[\w\.-]+@[\w\.-]+", r["snippet"]),
                    "phones": re.findall(r"\+?\d[\d\s\-]{7,}\d", r["snippet"]),
                })
            time.sleep(1)  # Be polite to Google
        except Exception as e:
            continue
    return people
