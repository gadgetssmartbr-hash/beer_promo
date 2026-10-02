"""
Comparador Direto de Supermercados Locais de Sertãozinho (Savegnago vs Copercana vs Paulistão Atacadista)
e Calculador de Economia de Carrinho / Lista de Compras.
"""
from typing import List, Dict, Any, Optional
from database import get_connection

def compare_product_in_stores(query: str) -> Dict[str, Any]:
    """
    Compara o preço de um produto diretamente entre Savegnago, Copercana, Paulistão Atacadista e Marketplaces.
    """
    search_term = query.strip()
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Savegnago
        cursor.execute("""
            SELECT p.name, p.store, p.link, ph.price, ph.original_price
            FROM products p
            JOIN price_history ph ON ph.product_id = p.id
            WHERE p.store LIKE '%Savegnago%' AND p.name LIKE ?
            ORDER BY ph.recorded_at DESC LIMIT 1
        """, (f"%{search_term}%",))
        savegnago_match = cursor.fetchone()
        
        # 2. Copercana
        cursor.execute("""
            SELECT p.name, p.store, p.link, ph.price, ph.original_price
            FROM products p
            JOIN price_history ph ON ph.product_id = p.id
            WHERE p.store LIKE '%Copercana%' AND p.name LIKE ?
            ORDER BY ph.recorded_at DESC LIMIT 1
        """, (f"%{search_term}%",))
        copercana_match = cursor.fetchone()
        
        # 3. Paulistão Atacadista
        cursor.execute("""
            SELECT p.name, p.store, p.link, ph.price, ph.original_price
            FROM products p
            JOIN price_history ph ON ph.product_id = p.id
            WHERE p.store LIKE '%Paulistão%' AND p.name LIKE ?
            ORDER BY ph.recorded_at DESC LIMIT 1
        """, (f"%{search_term}%",))
        paulistao_match = cursor.fetchone()

        # 4. Marketplaces (Amazon / ML)
        cursor.execute("""
            SELECT p.name, p.store, p.link, ph.price, ph.original_price
            FROM products p
            JOIN price_history ph ON ph.product_id = p.id
            WHERE p.store NOT LIKE '%Savegnago%' AND p.store NOT LIKE '%Copercana%' AND p.store NOT LIKE '%Paulistão%' AND p.name LIKE ?
            ORDER BY ph.price ASC LIMIT 1
        """, (f"%{search_term}%",))
        market_match = cursor.fetchone()

    # Se não houver correspondência completa no banco, busca no Catálogo Básico Oficial
    from services.basic_basket import find_staple_in_catalog
    staple = find_staple_in_catalog(search_term)
    
    sav_dict = dict(savegnago_match) if savegnago_match else None
    cop_dict = dict(copercana_match) if copercana_match else None
    pau_dict = dict(paulistao_match) if paulistao_match else None

    if staple:
        if not sav_dict:
            sav_dict = {
                "name": staple["name"],
                "store": "Savegnago Supermercados",
                "price": staple["savegnago"]["price"],
                "original_price": staple["savegnago"].get("original_price"),
                "link": f"https://www.savegnago.com.br/busca?ft={search_term}"
            }
        if not cop_dict:
            cop_dict = {
                "name": staple["name"],
                "store": "Supermercados Copercana",
                "price": staple["copercana"]["price"],
                "original_price": staple["copercana"].get("original_price"),
                "link": "https://www.supermercadoscopercana.com.br"
            }
        if not pau_dict:
            pau_dict = {
                "name": staple["name"],
                "store": "Paulistão Atacadista",
                "price": staple["paulistao"]["price"],
                "original_price": staple["paulistao"].get("original_price"),
                "link": "https://www.paulistaoatacadista.com.br/jornal-de-ofertas/sertaozinho"
            }

    res = {
        "query": search_term,
        "product_name": staple["name"] if staple else search_term,
        "savegnago": sav_dict,
        "copercana": cop_dict,
        "paulistao": pau_dict,
        "marketplace": dict(market_match) if market_match else None,
        "winner": None,
        "best_price": None,
        "diff_amount": 0.0,
        "diff_pct": 0.0
    }

    # Identifica o menor preço entre as redes locais de Sertãozinho
    local_candidates = []
    if res["savegnago"]:
        local_candidates.append(("Savegnago", res["savegnago"]["price"]))
    if res["copercana"]:
        local_candidates.append(("Copercana", res["copercana"]["price"]))
    if res["paulistao"]:
        local_candidates.append(("Paulistão Atacadista", res["paulistao"]["price"]))

    if local_candidates:
        local_candidates.sort(key=lambda x: x[1])
        winner_name, best_p = local_candidates[0]
        max_p = max(c[1] for c in local_candidates)
        
        res["winner"] = winner_name
        res["best_price"] = best_p
        res["diff_amount"] = round(max_p - best_p, 2)
        res["diff_pct"] = round(((max_p - best_p) / max_p) * 100, 1) if max_p > 0 else 0.0

    return res

def compare_shopping_basket(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calcula a simulação de compra completa da lista no Savegnago vs Copercana vs Paulistão Atacadista vs Melhor Combinação.
    """
    total_savegnago = 0.0
    total_copercana = 0.0
    total_paulistao = 0.0
    total_mixed = 0.0
    
    detailed_items = []
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        from services.basic_basket import find_staple_in_catalog
        for it in items:
            name = it["item_name"]
            staple = find_staple_in_catalog(name)
            
            # Savegnago
            cursor.execute("""
                SELECT ph.price FROM products p
                JOIN price_history ph ON ph.product_id = p.id
                WHERE p.store LIKE '%Savegnago%' AND p.name LIKE ?
                ORDER BY ph.recorded_at DESC LIMIT 1
            """, (f"%{name}%",))
            sav = cursor.fetchone()
            
            # Copercana
            cursor.execute("""
                SELECT ph.price FROM products p
                JOIN price_history ph ON ph.product_id = p.id
                WHERE p.store LIKE '%Copercana%' AND p.name LIKE ?
                ORDER BY ph.recorded_at DESC LIMIT 1
            """, (f"%{name}%",))
            cop = cursor.fetchone()

            # Paulistão
            cursor.execute("""
                SELECT ph.price FROM products p
                JOIN price_history ph ON ph.product_id = p.id
                WHERE p.store LIKE '%Paulistão%' AND p.name LIKE ?
                ORDER BY ph.recorded_at DESC LIMIT 1
            """, (f"%{name}%",))
            pau = cursor.fetchone()
            
            default_p = it.get("target_max_price") or 25.0
            p_sav = sav["price"] if sav else (staple["savegnago"]["price"] if staple else default_p)
            p_cop = cop["price"] if cop else (staple["copercana"]["price"] if staple else default_p)
            p_pau = pau["price"] if pau else (staple["paulistao"]["price"] if staple else default_p)
            
            prices_tuple = [("Savegnago", p_sav), ("Copercana", p_cop), ("Paulistão Atacadista", p_pau)]
            prices_tuple.sort(key=lambda x: x[1])
            
            best_store, p_best = prices_tuple[0]
            
            total_savegnago += p_sav
            total_copercana += p_cop
            total_paulistao += p_pau
            total_mixed += p_best
            
            detailed_items.append({
                "item_name": name,
                "price_savegnago": p_sav,
                "price_copercana": p_cop,
                "price_paulistao": p_pau,
                "best_store": best_store,
                "best_price": p_best
            })

    # Decisão entre redes únicas
    totals = [
        ("Savegnago", total_savegnago),
        ("Copercana", total_copercana),
        ("Paulistão Atacadista", total_paulistao)
    ]
    totals.sort(key=lambda x: x[1])
    basket_winner, min_total = totals[0]
    max_total = totals[-1][1]

    diff_basket = round(max_total - min_total, 2)
    diff_basket_pct = round(((max_total - min_total) / max_total) * 100, 1) if max_total > 0 else 0.0
    split_savings = round(max_total - total_mixed, 2)

    return {
        "total_items": len(items),
        "total_savegnago": round(total_savegnago, 2),
        "total_copercana": round(total_copercana, 2),
        "total_paulistao": round(total_paulistao, 2),
        "total_mixed": round(total_mixed, 2),
        "winner": basket_winner,
        "single_store_savings": diff_basket,
        "single_store_savings_pct": diff_basket_pct,
        "split_store_savings": split_savings,
        "items": detailed_items
    }
