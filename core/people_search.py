import time
import random
import requests
from bs4 import BeautifulSoup
import urllib.parse

# List of user agents to rotate
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0'
]

SEARCH_SITES = [
    ("LinkedIn", "site:linkedin.com/in {}"),
    ("Facebook", "site:facebook.com {}"),
    ("Twitter", "site:twitter.com {}"),
    ("Instagram", "site:instagram.com {}"),
    ("GitHub", "site:github.com {}"),
]

def get_search_url(query):
    """Generate a Startpage search URL."""
    base_url = "https://www.startpage.com/do/search"
    params = {
        'q': query,
        'cat': 'web',
        'language': 'english',
    }
    return f"{base_url}?{urllib.parse.urlencode(params)}"

def search_site(query, site_name, max_retries=3):
    """Search a site using Startpage."""
    results = []
    
    for attempt in range(max_retries):
        try:
            # Add delay between requests
            time.sleep(1 + random.random() * 2)  # 1-3 second delay
            
            # Rotate user agent
            headers = {
                'User-Agent': random.choice(USER_AGENTS),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://www.startpage.com/',
            }
            
            # Make the request
            url = get_search_url(query)
            print(f"Searching {site_name} for: {query}")
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Parse results
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all search result containers
            for result in soup.select('.w-gl__result'):
                title_elem = result.select_one('h3 a')
                if not title_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                url = title_elem.get('href', '')
                
                # Get snippet if available
                snippet_elem = result.select_one('.w-gl__description')
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                
                # Only add if we have both title and URL
                if title and url and url.startswith(('http://', 'https://')):
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet
                    })
                
                if len(results) >= 5:  # Limit to 5 results
                    break
                    
            return results
            
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                print(f"Search failed after {max_retries} attempts: {e}")
                return []
                
            wait_time = (2 ** attempt) + random.random()
            print(f"Attempt {attempt + 1} failed. Retrying in {wait_time:.1f} seconds...")
            time.sleep(wait_time)
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []
    
    return []

def search_person(name):
    """Search for a person across multiple social media sites."""
    people = []
    
    # Don't shuffle sites to make debugging easier
    sites = SEARCH_SITES
    
    for site, pattern in sites:
        try:
            # Format the query with quotes around the name
            formatted_name = f'"{name}"'
            query = pattern.format(formatted_name)
            print(f"Searching {site} for {formatted_name}...")
            
            # Get search results
            search_results = search_site(query, site)
            
            if not search_results:
                print(f"No results found on {site} for {formatted_name}")
                continue
                
            print(f"Found {len(search_results)} results on {site}")
            
            # Process search results
            for result in search_results:
                profile = {
                    "site": site,
                    "name": name,
                    "profile_url": result.get('url', ''),
                    "title": result.get('title', f"{name} on {site}"),
                    "snippet": result.get('snippet', f"Profile link for {name} on {site}"),
                    "avatar_url": "",
                    "location": "",
                    "emails": [],
                    "phones": [],
                }
                people.append(profile)
                print(f"- Found: {profile['title']}")
            
        except Exception as e:
            print(f"Error searching {site} for {name}: {str(e)}")
            continue
    
    print(f"\nFound {len(people)} total potential profiles")
    return people
