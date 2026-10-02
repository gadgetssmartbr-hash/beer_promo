"""
Exportador de dados de ofertas do SQLite e Scrapers para JSON estático consumido pelo GitHub Pages.
"""
import os
import sys
import json
from datetime import datetime
from typing import Dict, Any

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from database import get_connection, get_recent_price_drops, get_all_products_with_intelligence
from services import (
    get_beer_deals_ml,
    get_wine_deals_ml,
    get_local_supermarkets,
    get_wine_clubs_promos,
    get_active_coupons_and_tips,
)

DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")
DATA_DIR = os.path.join(DOCS_DIR, "data")
OUTPUT_JSON_PATH = os.path.join(DATA_DIR, "deals.json")

def export_deals_to_json() -> str:
    """Gera o arquivo JSON completo com todas as ofertas e análise de preço para o frontend."""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # 1. Carrega produtos com inteligência de preço do banco de dados SQLite
    products_db = get_all_products_with_intelligence()


    # 2. Gera comparativos diretos Savegnago vs Copercana
    from services.supermarket_comparator import compare_product_in_stores, compare_shopping_basket
    sample_queries = ["Heineken", "Spaten", "Corona", "Casillero", "Picanha", "Sabão Líquido OMO"]
    store_battles = [compare_product_in_stores(q) for q in sample_queries]

    # 3. Simulação de Carrinho
    sample_basket = [
        {"item_name": "Heineken"},
        {"item_name": "Spaten"},
        {"item_name": "Casillero"},
        {"item_name": "Picanha"},
        {"item_name": "OMO"}
    ]
    basket_analysis = compare_shopping_basket(sample_basket)

    # 4. Monta o payload final
    payload: Dict[str, Any] = {
        "metadata": {
            "city": "Sertãozinho - SP",
            "updated_at": datetime.now().strftime("%d/%m/%Y às %H:%M"),
            "telegram_bot": "https://t.me/beerstz_bot",
            "total_items": len(products_db)
        },
        "deals": products_db,
        "store_battles": store_battles,
        "basket_comparison": basket_analysis,
        "supermarkets": get_local_supermarkets(),
        "wine_clubs": get_wine_clubs_promos(),
        "coupons": get_active_coupons_and_tips()
    }


    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"✅ JSON de ofertas exportado para: {OUTPUT_JSON_PATH}")
    return OUTPUT_JSON_PATH

if __name__ == "__main__":
    export_deals_to_json()
