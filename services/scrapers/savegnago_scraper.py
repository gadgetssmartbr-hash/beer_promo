"""
Scraper / Extrator de ofertas do Savegnago Supermercados (Sertãozinho)
Suporta Cervejas, Vinhos, Carnes/Açougue, Limpeza, Mercearia e Cesta Básica Familiar em paralelo.
"""
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
from services.basic_basket import BASIC_CATALOG

SAVEGNAGO_API_SEARCH = "https://www.savegnago.com.br/api/catalog_system/pub/products/search"

def fetch_category(term: str, category: str, headers: dict) -> List[Dict[str, Any]]:
    items_out = []
    try:
        url = f"https://www.savegnago.com.br/api/catalog_system/pub/products/search/{term}?_from=0&_to=6"
        response = requests.get(url, headers=headers, timeout=3.5)
        if response.status_code == 200:
            items = response.json()
            for prod in items:
                name = prod.get("productName", "")
                link = prod.get("link", f"https://www.savegnago.com.br/busca?ft={term}")
                items_list = prod.get("items", [])
                if items_list:
                    sellers = items_list[0].get("sellers", [])
                    if sellers:
                        comm_offer = sellers[0].get("commertialOffer", {})
                        price = comm_offer.get("Price", 0.0)
                        list_price = comm_offer.get("ListPrice", 0.0)
                        
                        if price > 0:
                            items_out.append({
                                "name": name,
                                "category": category,
                                "store": "Savegnago Supermercados",
                                "price": float(price),
                                "original_price": float(list_price) if list_price > price else None,
                                "link": link
                            })
    except Exception:
        pass
    return items_out

def scrape_savegnago_deals(watchlist_items: List[str] = None) -> List[Dict[str, Any]]:
    """Busca ofertas ativas no catálogo online do Savegnago em todas as categorias em paralelo."""
    deals = []
    
    queries = [
        ("cerveja", "cerveja"),
        ("vinho", "vinho"),
        ("sabao liquido omo", "limpeza"),
        ("amaciante", "limpeza"),
        ("detergente", "limpeza"),
        ("papel higienico", "limpeza"),
        ("picanha", "acougue"),
        ("contrafile", "acougue"),
        ("file de frango", "acougue"),
        ("ovos", "mercearia"),
        ("leite", "mercearia"),
        ("arroz", "mercearia"),
        ("feijao", "mercearia"),
        ("cafe", "mercearia")
    ]
    
    if watchlist_items:
        for item in watchlist_items:
            queries.append((item.lower(), "watchlist"))

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_category, term, cat, headers) for term, cat in queries]
        for f in as_completed(futures):
            deals.extend(f.result())

    # Complementa com o catálogo essencial do Savegnago
    for item in BASIC_CATALOG:
        deals.append({
            "name": f"{item['name']} (Savegnago)",
            "category": item["category"],
            "store": "Savegnago Supermercados",
            "price": item["savegnago"]["price"],
            "original_price": item["savegnago"].get("original_price"),
            "link": f"https://www.savegnago.com.br/busca?ft={item['short_name'].replace(' ', '+')}"
        })

    return deals
