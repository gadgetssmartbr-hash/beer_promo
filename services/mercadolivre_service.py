"""
Serviço de busca e agregação de promoções em Marketplaces e Lojas Online.
"""
import urllib.parse
from typing import List, Dict, Any

def get_direct_marketplace_links(query: str) -> List[Dict[str, Any]]:
    """
    Gera links diretos com filtros de entrega rápida/Full/Prime e promoções para o termo pesquisado.
    """
    encoded_query = urllib.parse.quote_plus(query)
    
    return [
        {
            "store": "📦 Mercado Livre (Envios Full)",
            "title": f"Ver '{query}' com frete rápido Full no Mercado Livre",
            "price": "Conferir ofertas do dia",
            "discount": "",
            "free_shipping": "🚚 Frete Grátis acima de R$79",
            "is_full": "⚡ Full (Entrega rápida)",
            "link": f"https://lista.mercadolivre.com.br/{encoded_query}_OrderId_PRICE*ASC_CustId_0_ItemType_N_Installments_NO*INTEREST_Shipping_fulfillment"
        },
        {
            "store": "🛒 Savegnago Online (Sertãozinho)",
            "title": f"Buscar '{query}' no Savegnago Supermercados",
            "price": "Preço de encarte local",
            "discount": "",
            "free_shipping": "🛵 Delivery Local",
            "is_full": "📍 Sertãozinho",
            "link": f"https://www.savegnago.com.br/busca?ft={encoded_query}"
        },
        {
            "store": "⚡ Zé Delivery (Sertãozinho)",
            "title": f"Pedir '{query}' gelada no Zé Delivery",
            "price": "Preço de distribuidora",
            "discount": "",
            "free_shipping": "⏱️ Entrega em ~35 min",
            "is_full": "❄️ Gelada",
            "link": f"https://www.ze.delivery/produtos?q={encoded_query}"
        },
        {
            "store": "🛒 Amazon Brasil (Prime)",
            "title": f"Ofertas de '{query}' na Amazon Brasil",
            "price": "Preço Prime / Promoções",
            "discount": "",
            "free_shipping": "📦 Frete Grátis Prime",
            "is_full": "⭐ Amazon Prime",
            "link": f"https://www.amazon.com.br/s?k={encoded_query}&i=grocery"
        }
    ]

def get_beer_deals_ml() -> List[Dict[str, Any]]:
    """Destaques de cervejas populares e promoções."""
    return [
        {
            "title": "🍺 Heineken Pilsen (Pack 12x350ml / 24x350ml / Long Neck)",
            "price": "A partir de R$ 5,19 / lata",
            "discount": " (-12% no fardo)",
            "free_shipping": "🚚 Frete Grátis / Full",
            "is_full": "⚡ Full",
            "store": "Mercado Livre & Supermercados",
            "link": "https://lista.mercadolivre.com.br/cerveja-heineken-pack_OrderId_PRICE*ASC_Shipping_fulfillment"
        },
        {
            "title": "🍺 Spaten Munich Helles (Pack 12 ou 24 latas)",
            "price": "A partir de R$ 4,39 / unidade",
            "discount": " (-15% no combo)",
            "free_shipping": "🚚 Envio Rápido",
            "is_full": "⚡ Full",
            "store": "Mercado Livre",
            "link": "https://lista.mercadolivre.com.br/cerveja-spaten-pack_OrderId_PRICE*ASC_Shipping_fulfillment"
        },
        {
            "title": "🍺 Corona Extra (Pack Long Neck 330ml)",
            "price": "A partir de R$ 5,99 / un",
            "discount": " (-10%)",
            "free_shipping": "🚚 Frete Grátis",
            "is_full": "⚡ Full",
            "store": "Amazon Brasil / ML",
            "link": "https://www.amazon.com.br/s?k=cerveja+corona+pack"
        },
        {
            "title": "🍺 Cervejas Artesanais & IPA (Colorado, Roleta Russa, Baden Baden)",
            "price": "A partir de R$ 11,90",
            "discount": " (Kits com até 25% OFF)",
            "free_shipping": "📦 Frete Econômico",
            "is_full": "⭐ Seleção Especial",
            "store": "Supermercados Sertãozinho & Web",
            "link": "https://lista.mercadolivre.com.br/cerveja-artesanal-ipa_OrderId_PRICE*ASC"
        }
    ]

def get_wine_deals_ml() -> List[Dict[str, Any]]:
    """Destaques de vinhos populares e promoções."""
    return [
        {
            "title": "🍷 Kit 3 ou 6 Vinhos Tintos Importados (Malbec / Cabernet / Carmenere)",
            "price": "A partir de R$ 29,90 / garrafa",
            "discount": " (-45% no kit)",
            "free_shipping": "🚚 Frete Grátis",
            "is_full": "⚡ Full",
            "store": "Mercado Livre & Wine",
            "link": "https://lista.mercadolivre.com.br/kit-vinho-tinto-importado_OrderId_PRICE*ASC_Shipping_fulfillment"
        },
        {
            "title": "🍷 Vinho Chileno Concha y Toro Reservado / Casillero del Diablo",
            "price": "A partir de R$ 32,90",
            "discount": " (-20%)",
            "free_shipping": "📦 Envio Rápido",
            "is_full": "⚡ Full",
            "store": "Savegnago & Amazon",
            "link": "https://www.savegnago.com.br/busca?ft=casillero+del+diablo"
        },
        {
            "title": "🍾 Espumante Salton / Chandon Brut & Moscatel",
            "price": "A partir de R$ 34,90",
            "discount": " (-18%)",
            "free_shipping": "🚚 Entrega em Sertãozinho",
            "is_full": "📍 Supermercados",
            "store": "Savegnago & Copercana",
            "link": "https://www.savegnago.com.br/busca?ft=espumante+salton"
        }
    ]

def search_mercadolivre(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Retorna links diretos e estruturados para a busca multi-plataforma."""
    return get_direct_marketplace_links(query)
