"""
Comparador Direto de Supermercados Locais de Sertãozinho (Savegnago vs Copercana)
e Calculador de Economia de Carrinho / Lista de Compras.
"""
from typing import List, Dict, Any, Optional
from database import get_connection

def compare_product_in_stores(query: str) -> Dict[str, Any]:
    """
    Compara o preço de um produto diretamente entre Savegnago, Copercana e Marketplaces.
    """
    search_term = query.strip()
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Busca último preço no Savegnago
        cursor.execute("""
            SELECT p.name, p.store, p.link, ph.price, ph.original_price
            FROM products p
            JOIN price_history ph ON ph.product_id = p.id
            WHERE p.store LIKE '%Savegnago%' AND p.name LIKE ?
            ORDER BY ph.recorded_at DESC LIMIT 1
        """, (f"%{search_term}%",))
        savegnago_match = cursor.fetchone()
        
        # Busca último preço no Copercana
        cursor.execute("""
            SELECT p.name, p.store, p.link, ph.price, ph.original_price
            FROM products p
            JOIN price_history ph ON ph.product_id = p.id
            WHERE p.store LIKE '%Copercana%' AND p.name LIKE ?
            ORDER BY ph.recorded_at DESC LIMIT 1
        """, (f"%{search_term}%",))
        copercana_match = cursor.fetchone()
        
        # Busca em Marketplaces (Amazon / ML)
        cursor.execute("""
            SELECT p.name, p.store, p.link, ph.price, ph.original_price
            FROM products p
            JOIN price_history ph ON ph.product_id = p.id
            WHERE p.store NOT LIKE '%Savegnago%' AND p.store NOT LIKE '%Copercana%' AND p.name LIKE ?
            ORDER BY ph.price ASC LIMIT 1
        """, (f"%{search_term}%",))
        market_match = cursor.fetchone()

    res = {
        "query": search_term,
        "savegnago": dict(savegnago_match) if savegnago_match else None,
        "copercana": dict(copercana_match) if copercana_match else None,
        "marketplace": dict(market_match) if market_match else None,
        "winner": None,
        "diff_amount": 0.0,
        "diff_pct": 0.0
    }

    if res["savegnago"] and res["copercana"]:
        price_sav = res["savegnago"]["price"]
        price_cop = res["copercana"]["price"]
        
        if price_sav < price_cop:
            res["winner"] = "Savegnago"
            res["diff_amount"] = round(price_cop - price_sav, 2)
            res["diff_pct"] = round(((price_cop - price_sav) / price_cop) * 100, 1)
        elif price_cop < price_sav:
            res["winner"] = "Copercana"
            res["diff_amount"] = round(price_sav - price_cop, 2)
            res["diff_pct"] = round(((price_sav - price_cop) / price_sav) * 100, 1)
        else:
            res["winner"] = "Empate"

    return res

def compare_shopping_basket(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calcula a simulação de compra completa da lista no Savegnago vs Copercana vs Melhor Combinação.
    """
    total_savegnago = 0.0
    total_copercana = 0.0
    total_mixed = 0.0
    
    detailed_items = []
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        for it in items:
            name = it["item_name"]
            
            # Savegnago
            cursor.execute("""
                SELECT ph.price, p.name FROM products p
                JOIN price_history ph ON ph.product_id = p.id
                WHERE p.store LIKE '%Savegnago%' AND p.name LIKE ?
                ORDER BY ph.recorded_at DESC LIMIT 1
            """, (f"%{name}%",))
            sav = cursor.fetchone()
            
            # Copercana
            cursor.execute("""
                SELECT ph.price, p.name FROM products p
                JOIN price_history ph ON ph.product_id = p.id
                WHERE p.store LIKE '%Copercana%' AND p.name LIKE ?
                ORDER BY ph.recorded_at DESC LIMIT 1
            """, (f"%{name}%",))
            cop = cursor.fetchone()
            
            p_sav = sav["price"] if sav else (it.get("target_max_price") or 25.0)
            p_cop = cop["price"] if cop else (it.get("target_max_price") or 25.0)
            
            p_best = min(p_sav, p_cop)
            best_store = "Savegnago" if p_sav <= p_cop else "Copercana"
            
            total_savegnago += p_sav
            total_copercana += p_cop
            total_mixed += p_best
            
            detailed_items.append({
                "item_name": name,
                "price_savegnago": p_sav,
                "price_copercana": p_cop,
                "best_store": best_store,
                "savings": abs(p_sav - p_cop)
            })

    # Decisão
    if total_savegnago < total_copercana:
        basket_winner = "Savegnago"
        diff_basket = round(total_copercana - total_savegnago, 2)
        diff_basket_pct = round(((total_copercana - total_savegnago) / total_copercana) * 100, 1)
    elif total_copercana < total_savegnago:
        basket_winner = "Copercana"
        diff_basket = round(total_savegnago - total_copercana, 2)
        diff_basket_pct = round(((total_savegnago - total_copercana) / total_savegnago) * 100, 1)
    else:
        basket_winner = "Empate"
        diff_basket = 0.0
        diff_basket_pct = 0.0

    split_savings = round(max(total_savegnago, total_copercana) - total_mixed, 2)

    return {
        "total_items": len(items),
        "total_savegnago": round(total_savegnago, 2),
        "total_copercana": round(total_copercana, 2),
        "total_mixed": round(total_mixed, 2),
        "winner": basket_winner,
        "single_store_savings": diff_basket,
        "single_store_savings_pct": diff_basket_pct,
        "split_store_savings": split_savings,
        "items": detailed_items
    }
