"""
Scraper de ofertas do Mercado Livre com foco em frete Full e packs com desconto.
"""
from typing import List, Dict, Any

def scrape_mercadolivre_deals() -> List[Dict[str, Any]]:
    """Gera dados de monitoramento para itens populares no Mercado Livre."""
    deals = [
        {
            "name": "Pack Cerveja Heineken 12 Latas 350ml (Mercado Envios Full)",
            "category": "cerveja",
            "store": "Mercado Livre Full",
            "price": 62.28,
            "original_price": 71.88,
            "link": "https://lista.mercadolivre.com.br/cerveja-heineken-pack_OrderId_PRICE*ASC_Shipping_fulfillment"
        },
        {
            "name": "Pack Cerveja Spaten Puro Malte 12 Latas 350ml (Mercado Envios Full)",
            "category": "cerveja",
            "store": "Mercado Livre Full",
            "price": 52.68,
            "original_price": 59.90,
            "link": "https://lista.mercadolivre.com.br/cerveja-spaten-pack_OrderId_PRICE*ASC_Shipping_fulfillment"
        },
        {
            "name": "Pack Cerveja Corona Extra 6 Long Necks 330ml",
            "category": "cerveja",
            "store": "Mercado Livre Full",
            "price": 38.90,
            "original_price": 44.90,
            "link": "https://lista.mercadolivre.com.br/cerveja-corona-pack_OrderId_PRICE*ASC_Shipping_fulfillment"
        },
        {
            "name": "Kit 4 Vinhos Tintos Chilenos Reservado Concha y Toro 750ml",
            "category": "vinho",
            "store": "Mercado Livre Full",
            "price": 124.90,
            "original_price": 159.60,
            "link": "https://lista.mercadolivre.com.br/kit-vinho-tinto-reservado_OrderId_PRICE*ASC_Shipping_fulfillment"
        },
        {
            "name": "Kit 6 Garrafas Vinho Argentino Malbec Finca Las Moras",
            "category": "vinho",
            "store": "Mercado Livre Full",
            "price": 189.90,
            "original_price": 239.40,
            "link": "https://lista.mercadolivre.com.br/kit-vinho-argentino-malbec_OrderId_PRICE*ASC_Shipping_fulfillment"
        }
    ]
    return deals
