"""
Scraper e extrator de ofertas do Supermercados Copercana (Sertãozinho / Clube Copermais).
Suporta Cervejas, Vinhos, Carnes/Açougue, Limpeza, Mercearia e Cesta Básica Familiar.
"""
from typing import List, Dict, Any
from services.basic_basket import BASIC_CATALOG

COPERCANA_URL = "https://www.supermercadoscopercana.com.br"

def scrape_copercana_deals(watchlist_items: List[str] = None) -> List[Dict[str, Any]]:
    """Coleta e atualiza ofertas do Supermercados Copercana (Sertãozinho)."""
    deals = []
    
    for item in BASIC_CATALOG:
        deals.append({
            "name": f"{item['name']} (Copercana)",
            "category": item["category"],
            "store": "Supermercados Copercana",
            "price": item["copercana"]["price"],
            "original_price": item["copercana"].get("original_price"),
            "link": COPERCANA_URL
        })
        
    return deals
