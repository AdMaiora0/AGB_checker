import sys
import requests
from bs4 import BeautifulSoup
import webbrowser
from concurrent.futures import ThreadPoolExecutor, as_completed

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7',
    'Origin': 'https://www.vektis.nl',
    'Referer': 'https://www.vektis.nl/agb-register/zoeken',
}

def get_csrf_token(session, url):
    try:
        response = session.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        token_input = soup.find('input', {'name': '_token'})
        if token_input:
            return token_input['value']
        print("Error: Could not find CSRF token.")
        sys.exit(1)
    except requests.RequestException as e:
        print(f"Error fetching search page: {e}")
        sys.exit(1)
def perform_search(session, url, token, agb_code, party_type):
    payload = {
        '_token': token,
        'agbcode': agb_code,
        'zorgpartijtype': party_type,
        'zorgsoort': ''
    }
    
    if party_type == 'onderneming,vestiging':
        payload['plaats'] = ''
    
    try:
        response = session.post(url, data=payload, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return parse_results(response.text)
    except requests.RequestException:
        return []

def parse_results(html):
    soup = BeautifulSoup(html, 'lxml')
    results_container = soup.find('div', id='resultsContainer')
    
    if not results_container:
        return []
    
    title = results_container.find('h2', class_='title')
    if title and '0 Zoekresultaten' in title.text:
        return []
        
    table = results_container.find('table', class_='js-datatable')
    if not table:
        return []
        
    tbody = table.find('tbody')
    if not tbody:
        return []
        
    links = []
    for row in tbody.find_all('tr'):
        name_cell = row.find('td', class_='card-table__cell--name')
        if name_cell:
            link = name_cell.find('a')
            if link and link.get('href'):
                links.append(link['href'])
                
    return links

def create_optimized_session():
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=10,
        pool_maxsize=10,
        max_retries=2,
        pool_block=False
    )
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def main():
    args = [arg for arg in sys.argv[1:] if arg != "--dry-run"]
    if not args:
        print("Gebruik: python agb_checker.py <AGB-code> [--dry-run]")
        sys.exit(1)
        
    agb_code = args[0].strip()
    dry_run = "--dry-run" in sys.argv
    
    base_url = "https://www.vektis.nl"
    search_url = f"{base_url}/agb-register/zoeken"
    results_url = f"{base_url}/agb-register/zoeken/resultaten"
    
    session = create_optimized_session()
    
    print("Verbinding maken met Vektis...")
    token = get_csrf_token(session, search_url)
    
    print(f"Zoeken naar AGB code '{agb_code}'...")
    
    search_types = ['zorgverlener', 'onderneming,vestiging']
    found_links = []

    # Parallel execution is safe: requests.Session with HTTPAdapter uses thread-safe urllib3
    # connection pooling. We only read from session (POST requests), never modify session state.
    # However, Vektis seems to block or fail on concurrent requests with the same token/session.
    # Switching back to sequential execution for reliability.
    for stype in search_types:
        links = perform_search(session, results_url, token, agb_code, stype)
        if links:
            found_links.extend(links)
            break

    if found_links:
        target_url = found_links[0]
        print(f"Match gevonden! ({len(found_links)} resultaten)")
        print(f"Openen van: {target_url}")
        
        if not dry_run:
            webbrowser.open(target_url)
    else:
        print("Geen resultaten gevonden voor deze AGB code.")

if __name__ == "__main__":
    main()
