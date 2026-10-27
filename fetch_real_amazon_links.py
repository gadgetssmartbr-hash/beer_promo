import requests
from bs4 import BeautifulSoup
import urllib.parse
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

def extract_product_link(card):
    # 1. Direct /dp/ link
    for a in card.select("a[href*='/dp/']"):
        href = a.get("href", "")
        if "/dp/" in href:
            clean = href.split("?")[0].split("/ref=")[0]
            return "https://www.amazon.com.br" + clean if clean.startswith("/") else clean
            
    # 2. Sponsored /sspa/ link
    for a in card.select("a[href*='/sspa/click']"):
        href = a.get("href", "")
        parsed = urllib.parse.urlparse(href)
        qs = urllib.parse.parse_qs(parsed.query)
        if "url" in qs and qs["url"]:
            path = qs["url"][0].split("?")[0].split("/ref=")[0]
            return "https://www.amazon.com.br" + path if path.startswith("/") else path
            
    return None

session = requests.Session()
session.headers.update(headers)

queries = [
    "vinho casillero del diablo cabernet",
    "vinho cordero con piel de lobo malbec",
    "vinho pe tinto esporao",
    "vinho alamos malbec",
    "vinho dv catena cabernet malbec",
    "vinho escudo rojo gran reserva",
    "vinho carmenere gran reserva",
    "vinho primitivo di manduria",
    "vinho luigi bosca malbec",
    "vinho concha y toro reservado"
]

results = {}

for q in queries:
    try:
        url = f"https://www.amazon.com.br/s?k={urllib.parse.quote(q)}&i=grocery"
        res = session.get(url, timeout=7)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            cards = soup.select("div[data-component-type='s-search-result']")
            for card in cards:
                t = card.select_one("h2")
                p_whole = card.select_one(".a-price-whole")
                p_frac = card.select_one(".a-price-fraction")
                prod_link = extract_product_link(card)
                if t and p_whole and prod_link and "/dp/" in prod_link:
                    title = t.get_text(strip=True)
                    price = f"{p_whole.get_text(strip=True)},{p_frac.get_text(strip=True) if p_frac else '00'}"
                    results[q] = {
                        "title": title,
                        "price": price,
                        "link": prod_link
                    }
                    print(f"FOUND: [{q}] -> {title[:40]} | R$ {price} | {prod_link}")
                    break
        else:
            print(f"Status {res.status_code} for {q}")
    except Exception as e:
        print(f"Error {q}: {e}")
    time.sleep(1)

print("\n--- FINAL RESULTS COUNT ---:", len(results))
