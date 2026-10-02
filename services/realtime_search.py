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

    # 2. Compara no banco (Savegnago vs Copercana vs Paulistão Atacadista)
    from services.supermarket_comparator import compare_product_in_stores
    battle = compare_product_in_stores(clean_query)

    # Se pegamos preço ao vivo do Savegnago, atualiza o battle
    if savegnago_items:
        best_sav = savegnago_items[0]
        battle["savegnago"] = best_sav
        
        # Recalcula vencedor local
        local_candidates = []
        if battle.get("savegnago"):
            local_candidates.append(("Savegnago", battle["savegnago"]["price"]))
        if battle.get("copercana"):
            local_candidates.append(("Copercana", battle["copercana"]["price"]))
        if battle.get("paulistao"):
            local_candidates.append(("Paulistão Atacadista", battle["paulistao"]["price"]))
            
        if local_candidates:
            local_candidates.sort(key=lambda x: x[1])
            winner_name, best_p = local_candidates[0]
            max_p = max(c[1] for c in local_candidates)
            battle["winner"] = winner_name
            battle["best_price"] = best_p
            battle["diff_amount"] = round(max_p - best_p, 2)
            battle["diff_pct"] = round(((max_p - best_p) / max_p) * 100, 1) if max_p > 0 else 0.0

    # 3. Classificação de Intenção e Links Contextuais (Local vs Bebida vs Limpeza)
    from services.product_classifier import classify_product_query, get_store_links_for_product
    classification = classify_product_query(clean_query)
    contextual_links = get_store_links_for_product(clean_query)

    # 4. Histórico e inteligência
    history_records = get_product_history(clean_query, limit=2)

    return {
        "query": clean_query,
        "classification": classification,
        "battle": battle,
        "savegnago_live_items": savegnago_items,
        "history_records": history_records,
        "store_links": contextual_links
    }

