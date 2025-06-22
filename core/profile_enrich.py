import requests
from bs4 import BeautifulSoup
import re

def enrich_github(url):
    # url: https://github.com/<username>
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return {}
        soup = BeautifulSoup(resp.text, 'html.parser')
        avatar_url = soup.find('img', {'alt': 'Avatar'})
        avatar_url = avatar_url['src'] if avatar_url else ''
        bio = ''
        bio_tag = soup.find('div', {'data-bio-text': True})
        if bio_tag:
            bio = bio_tag.text.strip()
        # Follower count
        followers = ''
        following = ''
        for a in soup.find_all('a', href=re.compile(r'\?tab=followers$')):
            followers = a.find('span', {'class': 'text-bold'}).text.strip() if a.find('span', {'class': 'text-bold'}) else ''
        for a in soup.find_all('a', href=re.compile(r'\?tab=following$')):
            following = a.find('span', {'class': 'text-bold'}).text.strip() if a.find('span', {'class': 'text-bold'}) else ''
        return {
            'bio': bio,
            'avatar_url': avatar_url,
            'followers': followers,
            'following': following
        }
    except Exception as e:
        return {}

def enrich_twitter(url):
    # Twitter blocks scraping; best effort for public profiles only
    try:
        resp = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'})
        if resp.status_code != 200:
            return {}
        soup = BeautifulSoup(resp.text, 'html.parser')
        avatar_url = ''
        bio = ''
        followers = ''
        following = ''
        # Twitter HTML is heavily obfuscated, so this is just a placeholder
        return {
            'bio': bio,
            'avatar_url': avatar_url,
            'followers': followers,
            'following': following
        }
    except Exception:
        return {}

def enrich_profile(url, site):
    if 'github.com' in url:
        return enrich_github(url)
    if 'twitter.com' in url:
        return enrich_twitter(url)
    # Add more platforms as needed
    return {}
