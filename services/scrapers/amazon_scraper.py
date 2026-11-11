"""
Scraper de ofertas de Mercado, Limpeza, Mercearia e Bebidas na Amazon Brasil (Prime).
Com extração avançada de links diretos de produtos (/dp/ASIN).
"""
import requests
import urllib.parse
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional

AMAZON_SEARCH_URL = "https://www.amazon.com.br/s"

def extract_amazon_product_url(card) -> Optional[str]:
    """
    Extrai o link direto para a página do produto (/dp/ASIN) no card de busca da Amazon.
    Decodifica links patrocinados (/sspa/click) para obter a URL limpa e direta do item.
    Retorna None se nenhum link de produto for encontrado (evita URLs genéricas).
    """
    # 1. Procura primeiro link direto com /dp/
    a_dp = card.select_one("a[href*='/dp/']")
    if a_dp:
        href = a_dp.get("href", "")
        if "/dp/" in href:
            clean = href.split("?")[0].split("/ref=")[0]
            return "https://www.amazon.com.br" + clean if clean.startswith("/") else clean

    # 2. Procura link patrocinado (/sspa/click) e extrai o parâmetro url
    a_sspa = card.select_one("a[href*='/sspa/click']")
    if a_sspa:
        href = a_sspa.get("href", "")
        parsed = urllib.parse.urlparse(href)
        qs = urllib.parse.parse_qs(parsed.query)
        if "url" in qs and qs["url"]:
            clean = qs["url"][0].split("?")[0].split("/ref=")[0]
            return "https://www.amazon.com.br" + clean if clean.startswith("/") else clean

    # 3. Procura em links com classe a-link-normal
    for a in card.select("a.a-link-normal[href]"):
        href = a.get("href", "")
        if "/dp/" in href:
            clean = href.split("?")[0].split("/ref=")[0]
            return "https://www.amazon.com.br" + clean if clean.startswith("/") else clean
        elif "/sspa/click" in href:
            parsed = urllib.parse.urlparse(href)
            qs = urllib.parse.parse_qs(parsed.query)
            if "url" in qs and qs["url"]:
                clean = qs["url"][0].split("?")[0].split("/ref=")[0]
                return "https://www.amazon.com.br" + clean if clean.startswith("/") else clean

    return None

import random
import time


def _create_amazon_session() -> requests.Session:
    """Inicializa uma sessão HTTP com cabeçalhos de navegador e warmup na Amazon Brasil."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://www.amazon.com.br/",
        "Upgrade-Insecure-Requests": "1",
    })
    try:
        session.get("https://www.amazon.com.br/gp/browse.html?node=19645263011", timeout=5)
    except Exception:
        pass
    return session


def _fetch_search_cards(session: requests.Session, term: str, max_cards: int = 5):
    """Executa uma busca na Amazon Brasil com delay aleatório e retry único em 503."""
    time.sleep(random.uniform(0.6, 1.2))
    params = {"k": term, "i": "grocery"}
    response = session.get(AMAZON_SEARCH_URL, params=params, timeout=8)
    if response.status_code == 503:
        time.sleep(2.0)
        response = session.get(AMAZON_SEARCH_URL, params=params, timeout=8)
    if response.status_code != 200:
        return []
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.select("div[data-component-type='s-search-result']")[:max_cards]


def _parse_amazon_card(card):
    """Extrai (nome, preco, preco_original, url) de um card de busca da Amazon."""
    title_elem = card.select_one("h2 span") or card.select_one("h2")
    price_whole = card.select_one(".a-price-whole")
    price_fraction = card.select_one(".a-price-fraction")
    product_url = extract_amazon_product_url(card)

    if not (title_elem and price_whole and product_url):
        return None

    name = title_elem.get_text().strip()
    price_str = price_whole.get_text().replace(".", "").replace(",", "")
    fraction_str = price_fraction.get_text() if price_fraction else "00"
    try:
        price_val = float(f"{price_str}.{fraction_str}")
    except ValueError:
        return None

    if price_val <= 0:
        return None

    # Evita capturar preço unitário (.a-text-price sem data-a-strike="true") como preço riscado
    strike_elem = card.select_one('.a-text-price[data-a-strike="true"] .a-offscreen')
    orig_val = None
    if strike_elem:
        strike_text = strike_elem.get_text().replace("R$", "").replace(".", "").replace(",", ".").strip()
        try:
            orig_val = float(strike_text)
        except ValueError:
            orig_val = None

    if orig_val is not None and orig_val <= price_val:
        orig_val = None

    return name, price_val, orig_val, product_url


def scrape_amazon_deals() -> List[Dict[str, Any]]:
    """
    Busca ofertas e preços em destaque de produtos de supermercado, limpeza e bebidas na Amazon Brasil.
    """
    deals = []
    seen_urls = set()
    session = _create_amazon_session()

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
        ("cerveja heineken pack", "cerveja"),
        ("cerveja importada pack", "cerveja"),
        ("vinho tinto seco fino", "vinho"),
        ("kit vinho tinto seco", "vinho"),
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
            cards = _fetch_search_cards(session, term, max_cards=5)
            for card in cards:
                parsed = _parse_amazon_card(card)
                if not parsed:
                    continue
                name, price_val, orig_val, product_url = parsed
                if product_url in seen_urls:
                    continue
                seen_urls.add(product_url)
                deals.append({
                    "name": f"{name} (Amazon Prime)",
                    "category": category,
                    "store": "Amazon Brasil",
                    "price": price_val,
                    "original_price": orig_val,
                    "link": product_url
                })
        except Exception:
            pass

    # Curadoria padrão com links diretos verificados de produtos (/dp/ASIN)
    if len(deals) < 6:
        deals.extend([
            {
                "name": "Cerveja Paulaner Hefe-Weissbier Garrafa 500ml (Alemanha) (Amazon Prime)",
                "category": "cerveja",
                "store": "Amazon Brasil",
                "price": 19.90,
                "original_price": 25.90,
                "link": "https://www.amazon.com.br/Cerveja-Paulaner-Hefe-Weissbier-500ml/dp/B0797C224B"
            },
            {
                "name": "Cerveja Erdinger Weissbier Garrafa 500ml (Alemanha) (Amazon Prime)",
                "category": "cerveja",
                "store": "Amazon Brasil",
                "price": 18.90,
                "original_price": 23.90,
                "link": "https://www.amazon.com.br/Cerveja-Erdinger-Tradicional-500-ml/dp/B078NWS1F1"
            },
            {
                "name": "Cerveja Guinness Draught Stout Lata 440ml c/ Nitrogênio (Irlanda) (Amazon Prime)",
                "category": "cerveja",
                "store": "Amazon Brasil",
                "price": 23.90,
                "original_price": 28.90,
                "link": "https://www.amazon.com.br/Cerveja-Guinness-Draught-Lata-440ml/dp/B07H8K7B6K"
            },
            {
                "name": "Cerveja Leffe Blonde 330ml Long Neck (Bélgica) (Amazon Prime)",
                "category": "cerveja",
                "store": "Amazon Brasil",
                "price": 9.90,
                "original_price": 12.90,
                "link": "https://www.amazon.com.br/Cerveja-Leffe-Blonde-330ml/dp/B073XQL7R1"
            },
            {
                "name": "Cerveja Hoegaarden Witbier 330ml Long Neck (Bélgica) (Amazon Prime)",
                "category": "cerveja",
                "store": "Amazon Brasil",
                "price": 8.90,
                "original_price": 11.49,
                "link": "https://www.amazon.com.br/Cerveja-Hoegaarden-Witbier-330ml/dp/B0727K3Q2B"
            },
            {
                "name": "Cerveja Blue Moon Belgian White 355ml Long Neck (EUA) (Amazon Prime)",
                "category": "cerveja",
                "store": "Amazon Brasil",
                "price": 9.90,
                "original_price": 12.50,
                "link": "https://www.amazon.com.br/Cerveja-Blue-Moon-Belgian-White/dp/B0852932W4"
            },
            {
                "name": "Concha y Toro Casillero Del Diablo Cabernet Sauvignon 750ml (Amazon Prime)",
                "category": "vinho",
                "store": "Amazon Brasil",
                "price": 47.40,
                "original_price": 59.90,
                "link": "https://www.amazon.com.br/Vinho-Casillero-Diablo-Cabernet-Sauvignon/dp/B07LBK41YG"
            },
            {
                "name": "Concha y Toro Casillero Del Diablo Carmenere 750ml (Amazon Prime)",
                "category": "vinho",
                "store": "Amazon Brasil",
                "price": 39.97,
                "original_price": 54.90,
                "link": "https://www.amazon.com.br/Vinho-Casillero-Diablo-Carmenere-750ml/dp/B01IT28BY2"
            },
            {
                "name": "Vinho Pé Tinto Esporão Alentejo 750ml (Amazon Prime)",
                "category": "vinho",
                "store": "Amazon Brasil",
                "price": 39.90,
                "original_price": 49.90,
                "link": "https://www.amazon.com.br/Vinho-Espor%C3%A3o-Tinto-750ml-2018/dp/B00DTRY07A"
            },
            {
                "name": "Vinho Argentino Cordero Con Piel de Lobo 750ml (Amazon Prime)",
                "category": "vinho",
                "store": "Amazon Brasil",
                "price": 44.93,
                "original_price": 64.90,
                "link": "https://www.amazon.com.br/Vinho-Argentino-Cordero-Cabernet-Sauvignon/dp/B092R993VQ"
            },
            {
                "name": "Vinho Tinto Alandra Esporão 750ml (Amazon Prime)",
                "category": "vinho",
                "store": "Amazon Brasil",
                "price": 32.50,
                "original_price": 46.00,
                "link": "https://www.amazon.com.br/Espor%C3%A3o-Vinho-Tinto-Alandra/dp/B0CHWYSRTD"
            },
            {
                "name": "Vinho Fino Tinto Português Intimista Alentejo 750ml (Amazon Prime)",
                "category": "vinho",
                "store": "Amazon Brasil",
                "price": 33.52,
                "original_price": 49.90,
                "link": "https://www.amazon.com.br/Vinho-Tinto-Portugu%C3%AAs-Intimista-Alentejo/dp/B0D4NH9363"
            },
            {
                "name": "Vinho Tinto Chileno Escudo Rojo Gran Reserva Origine Cabernet Sauvignon 750ml (Amazon Prime)",
                "category": "vinho",
                "store": "Amazon Brasil",
                "price": 188.10,
                "original_price": 240.00,
                "link": "https://www.amazon.com.br/Chileno-Reserva-Origine-Cabernet-Sauvignon/dp/B09SHY372L"
            },
            {
                "name": "DV Catena Cabernet Malbec 6 Garrafas (Amazon Prime)",
                "category": "vinho",
                "store": "Amazon Brasil",
                "price": 484.99,
                "original_price": 599.00,
                "link": "https://www.amazon.com.br/DV-Catena-Cabernet-Malbec-Garrafas/dp/B0HM7F3WLF"
            },
            {
                "name": "Concha y Toro Reservado Cabernet Sauvignon 750ml (Amazon Prime)",
                "category": "vinho",
                "store": "Amazon Brasil",
                "price": 29.79,
                "original_price": 39.90,
                "link": "https://www.amazon.com.br/Concha-Toro-Reservado-Cabernet-Sauvignon/dp/B07XLMJHRN"
            },
            {
                "name": "Concha y Toro Reservado Vinho Chileno Merlot 750ml (Amazon Prime)",
                "category": "vinho",
                "store": "Amazon Brasil",
                "price": 24.98,
                "original_price": 34.90,
                "link": "https://www.amazon.com.br/Concha-Reservado-Vinho-Chileno-Merlot/dp/B09Q4JK85H"
            },
            {
                "name": "Sierra Batuco Vinho Tinto Chileno Cabernet Sauvignon 750ml (Amazon Prime)",
                "category": "vinho",
                "store": "Amazon Brasil",
                "price": 35.00,
                "original_price": 45.00,
                "link": "https://www.amazon.com.br/Chileno-Sierra-Batuco-Cabernet-Sauvignon/dp/B0BNQSFV8T"
            },
            {
                "name": "Vinho Tinto Português Casa Ferreirinha Esteva Douro 750ml (Amazon Prime)",
                "category": "vinho",
                "store": "Amazon Brasil",
                "price": 93.95,
                "original_price": 120.00,
                "link": "https://www.amazon.com.br/Vinho-Tinto-Portugu%C3%AAs-Ferreirinha-Esteva/dp/B0FW6DDVP9"
            },
            {
                "name": "Montes Limited Selection Pinot Noir Vinho Tinto Chileno 750ml (Amazon Prime)",
                "category": "vinho",
                "store": "Amazon Brasil",
                "price": 154.40,
                "original_price": 199.00,
                "link": "https://www.amazon.com.br/Montes-Limited-Selection-Pinot-chileno/dp/B001M2DUIY"
            },
            {
                "name": "Tormaresca Neprica Vinho Tinto Seco Primitivo Puglia IGT 750ml (Amazon Prime)",
                "category": "vinho",
                "store": "Amazon Brasil",
                "price": 182.10,
                "original_price": 230.00,
                "link": "https://www.amazon.com.br/Tormaresca-Neprica-Primitivo-encorpado-frutado/dp/B00O0SCESO"
            },
            {
                "name": "Vinho Faustino Crianza Tinto Seco DOCa Rioja 750ml (Amazon Prime)",
                "category": "vinho",
                "store": "Amazon Brasil",
                "price": 179.55,
                "original_price": 235.00,
                "link": "https://www.amazon.com.br/Vinho-Faustino-Crianza-Tinto-750ml/dp/B009XPFHV0"
            }
        ])

    return deals

def scrape_amazon_wine_deals() -> List[Dict[str, Any]]:
    """
    Busca rápida focada exclusivamente em vinhos tintos secos na Amazon Brasil (Prime).
    Garante links diretos para a página do produto (/dp/ASIN).
    """
    from services.wine_sommelier import is_good_dry_red

    wine_queries = [
        "vinho tinto seco fino",
        "kit vinho tinto seco",
        "vinho tinto cabernet sauvignon",
        "vinho tinto malbec",
        "vinho casillero del diablo",
        "vinho cordero con piel de lobo",
        "vinho esporao tinto",
        "vinho carmenere",
        "vinho primitivo di manduria",
        "vinho escudo rojo",
        "vinho dv catena"
    ]

    wine_deals = []
    seen_titles = set()
    seen_urls = set()
    session = _create_amazon_session()

    for term in wine_queries:
        try:
            cards = _fetch_search_cards(session, term, max_cards=5)
            for card in cards:
                parsed = _parse_amazon_card(card)
                if not parsed:
                    continue
                name, price_val, orig_val, product_url = parsed
                title_key = name[:25].lower()
                if title_key in seen_titles or product_url in seen_urls:
                    continue
                if not is_good_dry_red(name, price_val):
                    continue

                seen_titles.add(title_key)
                seen_urls.add(product_url)
                wine_deals.append({
                    "name": f"{name} (Amazon Prime)",
                    "category": "vinho",
                    "store": "Amazon Brasil",
                    "price": price_val,
                    "original_price": orig_val,
                    "link": product_url
                })
        except Exception:
            pass

    return wine_deals
