import sys
import requests
from bs4 import BeautifulSoup
import webbrowser
import concurrent.futures

# Headers to mimic a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7',
}

def get_csrf_token(session, url):
    try:
        response = session.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        token_input = soup.find('input', {'name': '_token'})
        if token_input:
            return token_input['value']
        else:
            print("Error: Could not find CSRF token.")
            sys.exit(1)
    except requests.RequestException as e:
        print(f"Error fetching search page: {e}")
        sys.exit(1)

def perform_search(session, url, token, agb_code, party_type):
    payload = {
        '_token': token,
        'naam': '',
        'agbcode': agb_code,
        'plaats': '',
        'zorgpartijtype': party_type,
        'zorgsoort': ''
    }
    
    try:
        # Use a separate session or the same? Requests session is not thread-safe for simultaneous requests 
        # if we were modifying it, but here we just read/post. 
        # To be safe and robust, we'll use the passed session but requests usually handles this okay-ish,
        # however, creating a new request context is safer for parallel execution if cookies change.
        # Since we just need the session for the cookies (XSRF-TOKEN etc), it's fine.
        response = session.post(url, data=payload, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return parse_results(response.text)
    except requests.RequestException as e:
        # Print error but don't crash, return empty list so other threads can succeed
        # print(f"Debug: Search failed for {party_type}: {e}") 
        return []

def parse_results(html):
    soup = BeautifulSoup(html, 'html.parser')
    results_container = soup.find('div', id='resultsContainer')
    
    if not results_container:
        return []
    
    title = results_container.find('h2', class_='title')
    if title and '0 Zoekresultaten' in title.text:
        return []
        
    table = results_container.find('table', class_='js-datatable')
    if not table:
        return []
        
    links = []
    tbody = table.find('tbody')
    if not tbody:
        return []
        
    rows = tbody.find_all('tr')
    for row in rows:
        name_cell = row.find('td', class_='card-table__cell--name')
        if name_cell:
            link = name_cell.find('a')
            if link and link.get('href'):
                links.append(link['href'])
                
    return links

def main():
    args = [arg for arg in sys.argv[1:] if arg != "--dry-run"]
    if not args:
        print("Gebruik: python agb_checker.py <AGB-code> [--dry-run]")
        sys.exit(1)
        
    agb_code = args[0]
    dry_run = "--dry-run" in sys.argv
    
    base_url = "https://www.vektis.nl"
    search_url = f"{base_url}/agb-register/zoeken"
    results_url = f"{base_url}/agb-register/zoeken/resultaten"
    
    session = requests.Session()
    
    print("Verbinding maken met Vektis...")
    token = get_csrf_token(session, search_url)
    
    print(f"Zoeken naar AGB code {agb_code}...")
    
    # Define the search types
    search_types = ['zorgverlener', 'onderneming,vestiging']
    found_links = []

    # Execute searches in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        # Map the search function to the types
        future_to_type = {
            executor.submit(perform_search, session, results_url, token, agb_code, stype): stype 
            for stype in search_types
        }
        
        for future in concurrent.futures.as_completed(future_to_type):
            stype = future_to_type[future]
            try:
                links = future.result()
                if links:
                    found_links.extend(links)
            except Exception as exc:
                print(f"Zoekopdracht voor {stype} genereerde een uitzondering: {exc}")

    if found_links:
        # Deduplicate links just in case, though unlikely to overlap types
        unique_links = list(set(found_links))
        target_url = unique_links[0]
        
        print(f"Match gevonden! ({len(unique_links)} resultaten)")
        print(f"Openen van: {target_url}")
        
        if not dry_run:
            webbrowser.open(target_url)
    else:
        print("Geen resultaten gevonden voor deze AGB code.")

if __name__ == "__main__":
    main()
