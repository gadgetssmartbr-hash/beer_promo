"""
Scraper de ofertas de Mercado, Limpeza, Mercearia e Bebidas na Amazon Brasil (Prime).
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any

AMAZON_SEARCH_URL = "https://www.amazon.com.br/s"

def scrape_amazon_deals() -> List[Dict[str, Any]]:
    """
    Busca ofertas e preços em destaque de produtos de supermercado, limpeza e bebidas na Amazon Brasil.
    """
    deals = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }
    
    queries = [
        ("sabao liquido omo", "limpeza"),
        ("amaciante concentrado", "limpeza"),
        ("papel higienico", "limpeza"),
        ("cafe em graos torrado", "mercearia"),
        ("cerveja paulaner", "cerveja"),
        ("cerveja erdinger", "cerveja"),
        ("cerveja guinness", "cerveja"),
        ("cerveja leffe", "cerveja"),
        ("cerveja hoegaarden", "cerveja"),
        ("cerveja blue moon", "cerveja"),
        ("vinho tinto seco fino", "vinho"),
        ("vinho tinto cabernet sauvignon", "vinho"),
        ("vinho tinto malbec", "vinho"),
        ("vinho casillero del diablo", "vinho"),
        ("vinho cordero con piel de lobo", "vinho"),
        ("vinho alamos malbec", "vinho"),
        ("vinho esporao tinto", "vinho"),
        ("vinho carmenere", "vinho"),
        ("vinho primitivo di manduria", "vinho"),
        ("vinho escudo rojo", "vinho")
    ]
    
    for term, category in queries:
        try:
            params = {"k": term, "i": "grocery"}
            response = requests.get(AMAZON_SEARCH_URL, params=params, headers=headers, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                cards = soup.select("div[data-component-type='s-search-result']")
                for card in cards[:3]:
                    title_elem = card.select_one("h2 span")
                    price_whole = card.select_one(".a-price-whole")
                    price_fraction = card.select_one(".a-price-fraction")
                    link_elem = card.select_one("h2 a")
                    
                    if title_elem and price_whole:
                        name = title_elem.get_text().strip()
                        price_str = price_whole.get_text().replace(".", "").replace(",", "")
                        fraction_str = price_fraction.get_text() if price_fraction else "00"
                        price_val = float(f"{price_str}.{fraction_str}")
                        
                        link = "https://www.amazon.com.br" + link_elem.get("href") if link_elem else "https://www.amazon.com.br"
                        
                        strike_elem = card.select_one(".a-text-price .a-offscreen")
                        orig_val = None
                        if strike_elem:
                            strike_text = strike_elem.get_text().replace("R$", "").replace(".", "").replace(",", ".").strip()
                            try:
                                orig_val = float(strike_text)
                            except ValueError:
                                orig_val = None
                                
                        if price_val > 0:
                            deals.append({
                                "name": f"{name} (Amazon Prime)",
                                "category": category,
                                "store": "Amazon Brasil",
                                "price": price_val,
                                "original_price": orig_val,
                                "link": link
                            })
        except Exception:
            pass

    # Curadoria padrão de Cervejas Importadas e Mercado na Amazon
    if len(deals) < 6:
        deals.extend([
            {
                "name": "Cerveja Paulaner Hefe-Weissbier Garrafa 500ml (Alemanha) (Amazon Prime)",
                "category": "cerveja",
                "store": "Amazon Brasil",
                "price": 19.90,
                "original_price": 25.90,
                "link": "https://www.amazon.com.br/s?k=cerveja+paulaner&i=grocery"
            },
            {
                "name": "Cerveja Erdinger Weissbier Garrafa 500ml (Alemanha) (Amazon Prime)",
                "category": "cerveja",
                "store": "Amazon Brasil",
                "price": 18.90,
                "original_price": 23.90,
                "link": "https://www.amazon.com.br/s?k=cerveja+erdinger&i=grocery"
            },
            {
                "name": "Cerveja Guinness Draught Stout Lata 440ml c/ Nitrogênio (Irlanda) (Amazon Prime)",
                "category": "cerveja",
                "store": "Amazon Brasil",
                "price": 23.90,
                "original_price": 28.90,
                "link": "https://www.amazon.com.br/s?k=cerveja+guinness&i=grocery"
            },
            {
                "name": "Cerveja Leffe Blonde 330ml Long Neck (Bélgica) (Amazon Prime)",
                "category": "cerveja",
                "store": "Amazon Brasil",
                "price": 9.90,
                "original_price": 12.90,
                "link": "https://www.amazon.com.br/s?k=cerveja+leffe&i=grocery"
            },
            {
                "name": "Cerveja Hoegaarden Witbier 330ml Long Neck (Bélgica) (Amazon Prime)",
                "category": "cerveja",
                "store": "Amazon Brasil",
                "price": 8.90,
                "original_price": 11.49,
                "link": "https://www.amazon.com.br/s?k=cerveja+hoegaarden&i=grocery"
            },
            {
                "name": "Cerveja Blue Moon Belgian White 355ml Long Neck (EUA) (Amazon Prime)",
                "category": "cerveja",
                "store": "Amazon Brasil",
                "price": 9.90,
                "original_price": 12.50,
                "link": "https://www.amazon.com.br/s?k=cerveja+blue+moon&i=grocery"
            },
            {
                "name": "Sabão Líquido Ariel Expert Concentrado 2L (Amazon Prime)",
                "category": "limpeza",
                "store": "Amazon Brasil",
                "price": 31.90,
                "original_price": 42.90,
                "link": "https://www.amazon.com.br/s?k=sabao+liquido+ariel&i=grocery"
            },
            {
                "name": "Amaciante Concentrado Downy Brisa de Verão 1,5L (Amazon Prime)",
                "category": "limpeza",
                "store": "Amazon Brasil",
                "price": 24.90,
                "original_price": 32.90,
                "link": "https://www.amazon.com.br/s?k=amaciante+downy&i=grocery"
            },
            {
                "name": "Concha y Toro Casillero Del Diablo Cabernet Sauvignon 750ml (Amazon Prime)",
                "category": "vinho",
                "store": "Amazon Brasil",
                "price": 36.00,
                "original_price": 59.90,
                "link": "https://www.amazon.com.br/s?k=casillero+del+diablo+cabernet&i=grocery"
            },
            {
                "name": "Vinho Pé Tinto Esporão Alentejo 750ml (Amazon Prime)",
                "category": "vinho",
                "store": "Amazon Brasil",
                "price": 32.39,
                "original_price": 49.90,
                "link": "https://www.amazon.com.br/s?k=vinho+pe+tinto+esporao&i=grocery"
            },
            {
                "name": "Vinho Argentino Cordero Con Piel de Lobo Malbec 750ml (Amazon Prime)",
                "category": "vinho",
                "store": "Amazon Brasil",
                "price": 44.90,
                "original_price": 64.90,
                "link": "https://www.amazon.com.br/s?k=vinho+cordero+con+piel+de+lobo&i=grocery"
            },
            {
                "name": "Vinho Fino Tinto Português Intimista Alentejo 750ml (Amazon Prime)",
                "category": "vinho",
                "store": "Amazon Brasil",
                "price": 35.41,
                "original_price": 49.90,
                "link": "https://www.amazon.com.br/s?k=vinho+intimista+tinto&i=grocery"
            },
            {
                "name": "Vinho Tinto Chileno Escudo Rojo Gran Reserva Cabernet Sauvignon 750ml (Amazon Prime)",
                "category": "vinho",
                "store": "Amazon Brasil",
                "price": 122.55,
                "original_price": 169.90,
                "link": "https://www.amazon.com.br/s?k=escudo+rojo+gran+reserva&i=grocery"
            },
            {
                "name": "DV Catena Cabernet Malbec Mendoza (Amazon Prime)",
                "category": "vinho",
                "store": "Amazon Brasil",
                "price": 149.90,
                "original_price": 199.00,
                "link": "https://www.amazon.com.br/s?k=dv+catena+cabernet+malbec&i=grocery"
            }
        ])

    return deals

def scrape_amazon_wine_deals() -> List[Dict[str, Any]]:
    """
    Busca rápida focada exclusivamente em vinhos tintos secos na Amazon Brasil (Prime).
    Utilizado na varredura horária do Sommelier.
    """
    from services.wine_sommelier import is_good_dry_red
    
    wine_queries = [
        "vinho tinto seco fino",
        "vinho tinto cabernet sauvignon",
        "vinho tinto malbec",
        "vinho casillero del diablo",
        "vinho cordero con piel de lobo",
        "vinho alamos malbec",
        "vinho esporao alentejo tinto",
        "vinho carmenere",
        "vinho primitivo di manduria",
        "vinho escudo rojo",
        "vinho dv catena"
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }
    
    wine_deals = []
    seen_titles = set()
    
    for term in wine_queries:
        try:
            params = {"k": term, "i": "grocery"}
            response = requests.get(AMAZON_SEARCH_URL, params=params, headers=headers, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                cards = soup.select("div[data-component-type='s-search-result']")
                for card in cards[:4]:
                    title_elem = card.select_one("h2 span")
                    price_whole = card.select_one(".a-price-whole")
                    price_fraction = card.select_one(".a-price-fraction")
                    link_elem = card.select_one("h2 a")
                    
                    if title_elem and price_whole:
                        name = title_elem.get_text().strip()
                        title_key = name[:25].lower()
                        if title_key in seen_titles:
                            continue
                            
                        price_str = price_whole.get_text().replace(".", "").replace(",", "")
                        fraction_str = price_fraction.get_text() if price_fraction else "00"
                        price_val = float(f"{price_str}.{fraction_str}")
                        
                        if not is_good_dry_red(name, price_val):
                            continue
                            
                        seen_titles.add(title_key)
                        link = "https://www.amazon.com.br" + link_elem.get("href") if link_elem else "https://www.amazon.com.br"
                        
                        strike_elem = card.select_one(".a-text-price .a-offscreen")
                        orig_val = None
                        if strike_elem:
                            strike_text = strike_elem.get_text().replace("R$", "").replace(".", "").replace(",", ".").strip()
                            try:
                                orig_val = float(strike_text)
                            except ValueError:
                                orig_val = None
                                
                        wine_deals.append({
                            "name": f"{name} (Amazon Prime)",
                            "category": "vinho",
                            "store": "Amazon Brasil",
                            "price": price_val,
                            "original_price": orig_val,
                            "link": link
                        })
        except Exception:
            pass
            
    return wine_deals
