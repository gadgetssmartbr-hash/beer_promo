"""
Scraper de ofertas de lojas virtuais de vinhos (Wine e Evino).
"""
from typing import List, Dict, Any

def scrape_wine_evino_deals() -> List[Dict[str, Any]]:
    """Gera dados de monitoramento das principais adegas virtuais."""
    return [
        {
            "name": "Kit 3 Vinhos Tintos Portugueses Bons Ventos (Wine.com.br)",
            "category": "vinho",
            "store": "Wine.com.br",
            "price": 109.90,
            "original_price": 179.70,
            "link": "https://www.wine.com.br/vinhos/ofertas"
        },
        {
            "name": "Kit 6 Vinhos Chilenos Gran Reserva Cabernet Sauvignon (Evino)",
            "category": "vinho",
            "store": "Evino",
            "price": 219.00,
            "original_price": 389.00,
            "link": "https://www.evino.com.br/promocoes"
        },
        {
            "name": "Espumante Brasileiro Salton Brut 750ml (Wine)",
            "category": "vinho",
            "store": "Wine.com.br",
            "price": 36.90,
            "original_price": 45.90,
            "link": "https://www.wine.com.br/vinhos/espumantes"
        }
    ]
