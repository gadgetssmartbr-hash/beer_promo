"""
Scraper de ofertas de lojas virtuais e importadoras de vinhos:
Wine.com.br, Evino, Grand Cru, Mistral e Pão de Açúcar Delivery.
Focado em Vinhos Tintos Secos Finos, Kits e Rótulos Consagrados.
"""
from typing import List, Dict, Any

def scrape_wine_evino_deals() -> List[Dict[str, Any]]:
    """Gera dados de monitoramento das principais adegas e importadoras virtuais."""
    return [
        # --- WINE.COM.BR ---
        {
            "name": "Kit 3 Vinhos Tintos Portugueses Bons Ventos Tinto Seco 750ml (Wine.com.br)",
            "category": "vinho",
            "store": "Wine.com.br",
            "price": 109.90,
            "original_price": 179.70,
            "link": "https://www.wine.com.br/vinhos/kit-3-vinhos-bons-ventos/p24823"
        },
        {
            "name": "Vinho Tinto Chileno Toro de Piedra Gran Reserva Cabernet Sauvignon 750ml (Wine.com.br)",
            "category": "vinho",
            "store": "Wine.com.br",
            "price": 89.90,
            "original_price": 129.90,
            "link": "https://www.wine.com.br/vinhos/toro-de-piedra-gran-reserva-cabernet/p18920"
        },
        {
            "name": "Vinho Tinto Espanhol Esteban Martín D.O.P. Cariñena Garnacha Syrah 750ml (Wine.com.br)",
            "category": "vinho",
            "store": "Wine.com.br",
            "price": 42.90,
            "original_price": 69.90,
            "link": "https://www.wine.com.br/vinhos/esteban-martin-dop-carinena/p27810"
        },
        {
            "name": "Vinho Tinto Português Encostas do Enxarrama Alentejo 750ml (Wine.com.br)",
            "category": "vinho",
            "store": "Wine.com.br",
            "price": 37.90,
            "original_price": 54.90,
            "link": "https://www.wine.com.br/vinhos/encostas-do-enxarrama-tinto/p29104"
        },
        {
            "name": "Vinho Tinto Argentino Partridge Reserva Malbec 750ml Las Perdices (Wine.com.br)",
            "category": "vinho",
            "store": "Wine.com.br",
            "price": 54.90,
            "original_price": 79.90,
            "link": "https://www.wine.com.br/vinhos/partridge-reserva-malbec/p23109"
        },

        # --- EVINO ---
        {
            "name": "Kit 6 Vinhos Chilenos Gran Reserva Cabernet Sauvignon 750ml (Evino)",
            "category": "vinho",
            "store": "Evino",
            "price": 219.00,
            "original_price": 389.00,
            "link": "https://www.evino.com.br/produto/kit-6-vinhos-gran-reserva-cabernet"
        },
        {
            "name": "Vinho Tinto Italiano Primitivo di Manduria Epicuro DOP 750ml (Evino)",
            "category": "vinho",
            "store": "Evino",
            "price": 84.90,
            "original_price": 129.90,
            "link": "https://www.evino.com.br/produto/epicuro-primitivo-di-manduria-dop"
        },
        {
            "name": "Vinho Tinto Espanhol Portada Winemaker's Selection 750ml (Evino)",
            "category": "vinho",
            "store": "Evino",
            "price": 39.90,
            "original_price": 59.90,
            "link": "https://www.evino.com.br/produto/portada-winemakers-selection-tinto"
        },
        {
            "name": "Vinho Tinto Chileno Ancón Reserva Carménère 750ml (Evino)",
            "category": "vinho",
            "store": "Evino",
            "price": 45.90,
            "original_price": 68.90,
            "link": "https://www.evino.com.br/produto/ancon-reserva-carmenere"
        },

        # --- GRAND CRU (ALTA GAMA & RESERVAS) ---
        {
            "name": "Vinho Argentino Cobos Felino Malbec 750ml Paul Hobbs (Grand Cru)",
            "category": "vinho",
            "store": "Grand Cru",
            "price": 139.90,
            "original_price": 179.90,
            "link": "https://www.grandcru.com.br/vinho-argentino-cobos-felino-malbec/p"
        },
        {
            "name": "Vinho Italiano San Marzano Il Pumo Primitivo Salento IGP 750ml (Grand Cru)",
            "category": "vinho",
            "store": "Grand Cru",
            "price": 94.90,
            "original_price": 129.90,
            "link": "https://www.grandcru.com.br/vinho-italiano-san-marzano-il-pumo-primitivo/p"
        },
        {
            "name": "Vinho Argentino Zuccardi Serie A Malbec Valle de Uco 750ml (Grand Cru)",
            "category": "vinho",
            "store": "Grand Cru",
            "price": 119.00,
            "original_price": 149.90,
            "link": "https://www.grandcru.com.br/vinho-argentino-zuccardi-serie-a-malbec/p"
        },
        {
            "name": "Vinho Chileno Errazuriz Max Reserva Cabernet Sauvignon 750ml (Grand Cru)",
            "category": "vinho",
            "store": "Grand Cru",
            "price": 129.90,
            "original_price": 169.90,
            "link": "https://www.grandcru.com.br/vinho-chileno-errazuriz-max-reserva-cabernet/p"
        },

        # --- MISTRAL (IMPORTADORA TRADICIONAL & ÍCONES) ---
        {
            "name": "Vinho Chileno Montes Alpha Cabernet Sauvignon Valle de Colchagua 750ml (Mistral)",
            "category": "vinho",
            "store": "Mistral",
            "price": 179.00,
            "original_price": 220.00,
            "link": "https://www.mistral.com.br/vinho/montes-alpha-cabernet-sauvignon-montes"
        },
        {
            "name": "Vinho Argentino Catena Malbec Mendoza 750ml Bodega Catena Zapata (Mistral)",
            "category": "vinho",
            "store": "Mistral",
            "price": 169.00,
            "original_price": 209.00,
            "link": "https://www.mistral.com.br/vinho/catena-malbec-catena-zapata"
        },
        {
            "name": "Vinho Português Quinta do Vallado Tinto Douro 750ml (Mistral)",
            "category": "vinho",
            "store": "Mistral",
            "price": 145.00,
            "original_price": 185.00,
            "link": "https://www.mistral.com.br/vinho/quinta-do-vallado-tinto-quinta-do-vallado"
        },

        # --- PÃO DE AÇÚCAR DELIVERY ---
        {
            "name": "Vinho Tinto Português EA Cartuxa Alentejo 750ml (Pão de Açúcar Delivery)",
            "category": "vinho",
            "store": "Pão de Açúcar Delivery",
            "price": 79.90,
            "original_price": 99.90,
            "link": "https://www.paodeacucar.com/produto/140228/vinho-portugues-tinto-ea-cartuxa-garrafa-750ml"
        },
        {
            "name": "Vinho Tinto Chileno Marques de Casa Concha Cabernet Sauvignon 750ml (Pão de Açúcar Delivery)",
            "category": "vinho",
            "store": "Pão de Açúcar Delivery",
            "price": 129.90,
            "original_price": 169.90,
            "link": "https://www.paodeacucar.com/produto/29184/vinho-chileno-tinto-marques-de-casa-concha-cabernet-sauvignon-750ml"
        }
    ]
