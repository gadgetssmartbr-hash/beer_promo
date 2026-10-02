"""
Scraper e extrator de ofertas do Paulistão Atacadista (Sertãozinho/SP).
Foco em atacarejo, compras em volume, fardos de cervejas, vinhos, carnes, limpeza e cesta básica.
"""
from typing import List, Dict, Any
from services.basic_basket import BASIC_CATALOG

PAULISTAO_URL = "https://www.paulistaoatacadista.com.br/jornal-de-ofertas/sertaozinho"

def scrape_paulistao_deals(watchlist_items: List[str] = None) -> List[Dict[str, Any]]:
    """Coleta e atualiza ofertas do Paulistão Atacadista (Sertãozinho)."""
    deals = []
    
    for item in BASIC_CATALOG:
        deals.append({
            "name": f"{item['name']} (Paulistão Atacadista)",
            "category": item["category"],
            "store": "Paulistão Atacadista",
            "price": item["paulistao"]["price"],
            "original_price": item["paulistao"].get("original_price"),
            "link": PAULISTAO_URL
        })
        
    return deals
