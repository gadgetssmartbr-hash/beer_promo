"""
Módulo de Busca em Tempo Real Sob Demanda (Multi-loja).
Quando o usuário pede uma pesquisa específica, roda a busca na hora no Savegnago, Copercana, Mercado Livre e Amazon.
"""
import requests
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from database import save_price_record, get_product_history
from services.price_intelligence import analyze_price_quality

SAVEGNAGO_API_SEARCH = "https://www.savegnago.com.br/api/catalog_system/pub/products/search"

def query_savegnago_live(term: str) -> List[Dict[str, Any]]:
    """Consulta direta em tempo real na API do Savegnago."""
    results = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        url = f"{SAVEGNAGO_API_SEARCH}/{term}?_from=0&_to=4"
        r = requests.get(url, headers=headers, timeout=4)
        if r.status_code == 200:
            for item in r.json():
                name = item.get("productName", "")
                link = item.get("link", f"https://www.savegnago.com.br/busca?ft={term}")
                items_list = item.get("items", [])
                if items_list:
                    sellers = items_list[0].get("sellers", [])
                    if sellers:
                        offer = sellers[0].get("commertialOffer", {})
                        price = offer.get("Price", 0.0)
                        orig = offer.get("ListPrice", 0.0)
                        if price > 0:
                            results.append({
                                "name": name,
                                "store": "Savegnago Supermercados",
                                "price": float(price),
                                "original_price": float(orig) if orig > price else None,
                                "link": link
                            })
    except Exception:
        pass
    return results

def search_realtime_all_stores(query: str) -> Dict[str, Any]:
    """
    Executa busca em tempo real em todas as lojas simultaneamente para o termo solicitado.
    """
    clean_query = query.strip()
    
    # 1. Busca no Savegnago ao vivo
    savegnago_items = query_savegnago_live(clean_query)
    
    # Salva no histórico SQLite os resultados em tempo real
    for item in savegnago_items:
        save_price_record(
            name=item["name"],
            category="busca_tempo_real",
            store=item["store"],
            price=item["price"],
            original_price=item.get("original_price"),
            link=item.get("link", "")
        )

    # 2. Compara no banco (Savegnago vs Copercana vs Marketplaces)
    from services.supermarket_comparator import compare_product_in_stores
    battle = compare_product_in_stores(clean_query)

    # Se pegamos preço ao vivo do Savegnago, atualiza o battle
    if savegnago_items:
        best_sav = savegnago_items[0]
        battle["savegnago"] = best_sav
        if battle.get("copercana"):
            price_sav = best_sav["price"]
            price_cop = battle["copercana"]["price"]
            if price_sav < price_cop:
                battle["winner"] = "Savegnago"
                battle["diff_amount"] = round(price_cop - price_sav, 2)
                battle["diff_pct"] = round(((price_cop - price_sav) / price_cop) * 100, 1)
            elif price_cop < price_sav:
                battle["winner"] = "Copercana"
                battle["diff_amount"] = round(price_sav - price_cop, 2)
                battle["diff_pct"] = round(((price_sav - price_cop) / price_sav) * 100, 1)
            else:
                battle["winner"] = "Empate"

    # 3. Links diretos para Mercado Livre e Amazon
    from services.mercadolivre_service import get_direct_marketplace_links
    mp_links = get_direct_marketplace_links(clean_query)

    # 4. Histórico e inteligência
    history_records = get_product_history(clean_query, limit=2)

    return {
        "query": clean_query,
        "battle": battle,
        "savegnago_live_items": savegnago_items,
        "history_records": history_records,
        "marketplace_links": mp_links
    }
