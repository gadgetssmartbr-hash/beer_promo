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

from database import get_connection, get_recent_price_drops
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
    """Gera o arquivo JSON completo com todas as ofertas para o frontend do GitHub Pages."""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # 1. Carrega do banco de dados SQLite
    products_db = []
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.name, p.category, p.store, p.link,
                   ph.price, ph.original_price, ph.discount_pct, ph.recorded_at
            FROM products p
            JOIN price_history ph ON ph.product_id = p.id
            WHERE ph.id IN (
                SELECT MAX(id) FROM price_history GROUP BY product_id
            )
            ORDER BY ph.discount_pct DESC, ph.price ASC
        """)
        for row in cursor.fetchall():
            products_db.append({
                "name": row["name"],
                "category": row["category"],
                "store": row["store"],
                "price": row["price"],
                "original_price": row["original_price"],
                "discount_pct": row["discount_pct"],
                "link": row["link"],
                "recorded_at": row["recorded_at"],
                "badge": "⚡ Oferta" if row["discount_pct"] > 10 else "🛒 Preço Regular"
            })

    # 2. Monta o payload final
    payload: Dict[str, Any] = {
        "metadata": {
            "city": "Sertãozinho - SP",
            "updated_at": datetime.now().strftime("%d/%m/%Y às %H:%M"),
            "telegram_bot": "https://t.me/beerstz_bot",
            "total_items": len(products_db)
        },
        "deals": products_db,
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
