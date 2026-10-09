"""
Scraper de ofertas do Mercado Livre com foco em frete Full, packs fechados e Cervejas Importadas Especiais.
"""
from typing import List, Dict, Any

def scrape_mercadolivre_deals() -> List[Dict[str, Any]]:
    """Gera dados de monitoramento para itens populares e cervejas importadas no Mercado Livre."""
    deals = [
        # --- Cervejas Importadas & Especiais ---
        {
            "name": "Cerveja Paulaner Hefe-Weissbier Garrafa 500ml (Alemanha)",
            "category": "cerveja",
            "store": "Mercado Livre Full",
            "price": 19.90,
            "original_price": 24.90,
            "link": "https://lista.mercadolivre.com.br/cerveja-paulaner-500ml_OrderId_PRICE*ASC_Shipping_fulfillment"
        },
        {
            "name": "Pack Cerveja Erdinger Weissbier 6 Garrafas 500ml (Alemanha)",
            "category": "cerveja",
            "store": "Mercado Livre Full",
            "price": 114.90,
            "original_price": 139.90,
            "link": "https://lista.mercadolivre.com.br/cerveja-erdinger-pack_OrderId_PRICE*ASC_Shipping_fulfillment"
        },
        {
            "name": "Cerveja Guinness Draught Stout Lata 440ml c/ Nitrogênio (Irlanda)",
            "category": "cerveja",
            "store": "Mercado Livre Full",
            "price": 24.90,
            "original_price": 29.90,
            "link": "https://lista.mercadolivre.com.br/cerveja-guinness-lata-440ml_OrderId_PRICE*ASC_Shipping_fulfillment"
        },
        {
            "name": "Pack Cerveja Hoegaarden Witbier 6 Long Necks 330ml (Bélgica)",
            "category": "cerveja",
            "store": "Mercado Livre Full",
            "price": 49.90,
            "original_price": 59.40,
            "link": "https://lista.mercadolivre.com.br/cerveja-hoegaarden-pack_OrderId_PRICE*ASC_Shipping_fulfillment"
        },
        {
            "name": "Pack Cerveja Leffe Blonde 6 Long Necks 330ml (Bélgica)",
            "category": "cerveja",
            "store": "Mercado Livre Full",
            "price": 54.90,
            "original_price": 65.90,
            "link": "https://lista.mercadolivre.com.br/cerveja-leffe-blonde-pack_OrderId_PRICE*ASC_Shipping_fulfillment"
        },
        {
            "name": "Pack Cerveja Blue Moon Belgian White 6 Long Necks 355ml (EUA)",
            "category": "cerveja",
            "store": "Mercado Livre Full",
            "price": 58.90,
            "original_price": 71.90,
            "link": "https://lista.mercadolivre.com.br/cerveja-blue-moon-pack_OrderId_PRICE*ASC_Shipping_fulfillment"
        },
        {
            "name": "Cerveja Duvel Belgian Strong Blond Ale 330ml (Bélgica)",
            "category": "cerveja",
            "store": "Mercado Livre Full",
            "price": 27.90,
            "original_price": 34.90,
            "link": "https://lista.mercadolivre.com.br/cerveja-duvel-330ml_OrderId_PRICE*ASC_Shipping_fulfillment"
        },
        {
            "name": "Cerveja Franziskaner Hefe-Weissbier Hell Garrafa 500ml (Alemanha)",
            "category": "cerveja",
            "store": "Mercado Livre Full",
            "price": 18.90,
            "original_price": 23.50,
            "link": "https://lista.mercadolivre.com.br/cerveja-franziskaner-500ml_OrderId_PRICE*ASC_Shipping_fulfillment"
        },
        # --- Cervejas Comerciais & Puro Malte ---
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
        # --- Vinhos Importados ---
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
