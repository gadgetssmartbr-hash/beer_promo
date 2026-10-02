"""
Pacote de serviços de busca e integração de promoções de bebidas.
"""
from .mercadolivre_service import search_mercadolivre, get_beer_deals_ml, get_wine_deals_ml
from .savegnago_service import get_local_supermarkets, get_savegnago_info, get_copercana_info
from .wine_service import get_wine_clubs_promos
from .coupons_service import get_active_coupons_and_tips

__all__ = [
    "search_mercadolivre",
    "get_beer_deals_ml",
    "get_wine_deals_ml",
    "get_local_supermarkets",
    "get_savegnago_info",
    "get_copercana_info",
    "get_wine_clubs_promos",
    "get_active_coupons_and_tips",
]
