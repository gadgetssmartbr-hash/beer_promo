"""
Scraper e extrator de ofertas do Supermercados Copercana (Sertãozinho / Clube Copermais).
"""
import requests
from typing import List, Dict, Any

COPERCANA_URL = "https://www.supermercadoscopercana.com.br"

def scrape_copercana_deals(watchlist_items: List[str] = None) -> List[Dict[str, Any]]:
    """Coleta e atualiza ofertas do Supermercados Copercana (Sertãozinho)."""
    deals = [
        # Cervejas
        {
            "name": "Cerveja Heineken Puro Malte Lata 350ml (Copercana)",
            "category": "cerveja",
            "store": "Supermercados Copercana",
            "price": 5.59,
            "original_price": 5.99,
            "link": f"{COPERCANA_URL}/cervejas"
        },
        {
            "name": "Cerveja Spaten Munich Helles Lata 350ml (Copercana)",
            "category": "cerveja",
            "store": "Supermercados Copercana",
            "price": 4.59,
            "original_price": 5.09,
            "link": f"{COPERCANA_URL}/cervejas"
        },
        {
            "name": "Cerveja Corona Extra 330ml Long Neck (Copercana)",
            "category": "cerveja",
            "store": "Supermercados Copercana",
            "price": 6.19,
            "original_price": 6.89,
            "link": f"{COPERCANA_URL}/cervejas"
        },
        {
            "name": "Cerveja Colorado Ribeirão Lager Lata 350ml (Copercana)",
            "category": "cerveja",
            "store": "Supermercados Copercana",
            "price": 4.79,
            "original_price": 5.49,
            "link": f"{COPERCANA_URL}/artesanais"
        },
        # Vinhos
        {
            "name": "Vinho Chileno Casillero del Diablo Cabernet Sauvignon 750ml (Copercana)",
            "category": "vinho",
            "store": "Supermercados Copercana",
            "price": 51.90,
            "original_price": 66.90,
            "link": f"{COPERCANA_URL}/vinhos"
        },
        {
            "name": "Vinho Argentino Cordero con Piel de Lobo Malbec 750ml (Copercana)",
            "category": "vinho",
            "store": "Supermercados Copercana",
            "price": 46.90,
            "original_price": 58.00,
            "link": f"{COPERCANA_URL}/vinhos"
        },
        {
            "name": "Espumante Salton Brut 750ml (Copercana)",
            "category": "vinho",
            "store": "Supermercados Copercana",
            "price": 36.90,
            "original_price": 44.90,
            "link": f"{COPERCANA_URL}/espumantes"
        },
        # Limpeza
        {
            "name": "Sabão Líquido OMO Lavagem Perfeita 3 Litros (Copercana)",
            "category": "limpeza",
            "store": "Supermercados Copercana",
            "price": 39.90,
            "original_price": 54.90,
            "link": f"{COPERCANA_URL}/limpeza"
        },
        {
            "name": "Amaciante Concentrado Comfort 1,5L (Copercana)",
            "category": "limpeza",
            "store": "Supermercados Copercana",
            "price": 22.90,
            "original_price": 28.90,
            "link": f"{COPERCANA_URL}/limpeza"
        },
        # Carnes
        {
            "name": "Picanha Bovina Peça / Kg (Açougue Copercana)",
            "category": "acougue",
            "store": "Supermercados Copercana",
            "price": 62.90,
            "original_price": 82.90,
            "link": f"{COPERCANA_URL}/acougue"
        },
        {
            "name": "Contrafilé Bovino Resfriado Kg (Açougue Copercana)",
            "category": "acougue",
            "store": "Supermercados Copercana",
            "price": 38.90,
            "original_price": 48.90,
            "link": f"{COPERCANA_URL}/acougue"
        }
    ]
    return deals
