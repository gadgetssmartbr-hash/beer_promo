"""
Gerenciador central de busca e persistência de histórico de promoções.
"""
from typing import List, Dict, Any
from database import save_price_record, get_recent_price_drops, get_watchlist
from .savegnago_scraper import scrape_savegnago_deals
from .copercana_scraper import scrape_copercana_deals
from .paulistao_scraper import scrape_paulistao_deals
from .mercadolivre_scraper import scrape_mercadolivre_deals
from .wine_scraper import scrape_wine_evino_deals
from .amazon_scraper import scrape_amazon_deals

def run_all_scrapers() -> Dict[str, Any]:
    """
    Executa todos os scrapers, salva o histórico de preços no SQLite
    e retorna resumo das novidades e quedas de preço.
    """
    all_deals = []
    
    # Carrega itens da lista da família
    try:
        watchlist_items = [w["item_name"] for w in get_watchlist()]
    except Exception:
        watchlist_items = []

    # Executa cada scraper
    try:
        all_deals.extend(scrape_savegnago_deals(watchlist_items))
    except Exception as e:
        print(f"Erro no scraper Savegnago: {e}")

    try:
        all_deals.extend(scrape_copercana_deals(watchlist_items))
    except Exception as e:
        print(f"Erro no scraper Copercana: {e}")

    try:
        all_deals.extend(scrape_paulistao_deals(watchlist_items))
    except Exception as e:
        print(f"Erro no scraper Paulistão Atacadista: {e}")



        
    try:
        all_deals.extend(scrape_mercadolivre_deals())
    except Exception as e:
        print(f"Erro no scraper Mercado Livre: {e}")
        
    try:
        all_deals.extend(scrape_amazon_deals())
    except Exception as e:
        print(f"Erro no scraper Amazon: {e}")

    try:
        all_deals.extend(scrape_wine_evino_deals())
    except Exception as e:
        print(f"Erro no scraper Wine/Evino: {e}")


    price_drops = []
    saved_count = 0
    
    for item in all_deals:
        dropped, old_price, new_price = save_price_record(
            name=item["name"],
            category=item["category"],
            store=item["store"],
            price=item["price"],
            original_price=item.get("original_price"),
            link=item.get("link", "")
        )
        saved_count += 1
        if dropped:
            price_drops.append({
                "name": item["name"],
                "store": item["store"],
                "old_price": old_price,
                "new_price": new_price,
                "link": item.get("link", "")
            })

    # Exporta automaticamente o JSON para o site do GitHub Pages
    try:
        from services.export_web import export_deals_to_json
        export_deals_to_json()
    except Exception as e:
        print(f"Erro ao exportar JSON para o site: {e}")

    return {
        "total_scraped": len(all_deals),
        "total_saved": saved_count,
        "price_drops": price_drops,
        "top_promos": get_recent_price_drops(limit=8)
    }

