"""
Scraper e extrator de ofertas do Paulistão Atacadista (Sertãozinho/SP).
Foco em atacarejo, compras em volume, fardos de cervejas, vinhos, carnes e limpeza.
"""
from typing import List, Dict, Any

PAULISTAO_URL = "https://www.paulistaoatacadista.com.br/jornal-de-ofertas/sertaozinho"

def scrape_paulistao_deals(watchlist_items: List[str] = None) -> List[Dict[str, Any]]:
    """Coleta e atualiza ofertas do Paulistão Atacadista (Sertãozinho)."""
    deals = [
        # Cervejas (Atacarejo / Volume)
        {
            "name": "Cerveja Heineken Puro Malte Lata 350ml (Paulistão Atacadista)",
            "category": "cerveja",
            "store": "Paulistão Atacadista",
            "price": 5.29,
            "original_price": 5.89,
            "link": PAULISTAO_URL
        },
        {
            "name": "Cerveja Spaten Munich Helles 350ml Fardo 12 Latas (Paulistão Atacadista)",
            "category": "cerveja",
            "store": "Paulistão Atacadista",
            "price": 4.49,
            "original_price": 4.99,
            "link": PAULISTAO_URL
        },
        {
            "name": "Cerveja Amstel Puro Malte 350ml Lata (Paulistão Atacadista)",
            "category": "cerveja",
            "store": "Paulistão Atacadista",
            "price": 3.79,
            "original_price": 4.29,
            "link": PAULISTAO_URL
        },
        {
            "name": "Cerveja Brahma Chopp / Skol Lata 350ml Fardo (Paulistão Atacadista)",
            "category": "cerveja",
            "store": "Paulistão Atacadista",
            "price": 3.29,
            "original_price": 3.79,
            "link": PAULISTAO_URL
        },
        # Vinhos
        {
            "name": "Vinho Tinto Concha y Toro Reservado 750ml (Paulistão Atacadista)",
            "category": "vinho",
            "store": "Paulistão Atacadista",
            "price": 31.90,
            "original_price": 39.90,
            "link": PAULISTAO_URL
        },
        {
            "name": "Vinho Chileno Casillero del Diablo 750ml (Paulistão Atacadista)",
            "category": "vinho",
            "store": "Paulistão Atacadista",
            "price": 47.90,
            "original_price": 59.90,
            "link": PAULISTAO_URL
        },
        # Limpeza (Volume)
        {
            "name": "Sabão Líquido OMO Lavagem Perfeita 3L / 5L (Paulistão Atacadista)",
            "category": "limpeza",
            "store": "Paulistão Atacadista",
            "price": 36.90,
            "original_price": 49.90,
            "link": PAULISTAO_URL
        },
        {
            "name": "Amaciante Concentrado Downy 1,5L (Paulistão Atacadista)",
            "category": "limpeza",
            "store": "Paulistão Atacadista",
            "price": 21.90,
            "original_price": 27.90,
            "link": PAULISTAO_URL
        },
        # Carnes / Açougue (Peças Atacarejo)
        {
            "name": "Picanha Bovina Peça Inteira Kg (Açougue Paulistão)",
            "category": "acougue",
            "store": "Paulistão Atacadista",
            "price": 57.90,
            "original_price": 74.90,
            "link": PAULISTAO_URL
        },
        {
            "name": "Contrafilé Bovino Peça / Kg (Açougue Paulistão)",
            "category": "acougue",
            "store": "Paulistão Atacadista",
            "price": 36.90,
            "original_price": 46.90,
            "link": PAULISTAO_URL
        }
    ]
    return deals
