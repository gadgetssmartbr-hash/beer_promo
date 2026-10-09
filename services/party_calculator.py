"""
Calculadora Inteligente de Churrasco e Eventos com Comparador Direto de Supermercados (Sertãozinho/SP).
Calcula consumos precisos e compara os custos no Savegnago, Copercana, Paulistão Atacadista e Mix Otimizado.
"""
from typing import Dict, Any, List
from services.basic_basket import BASIC_CATALOG

def calculate_bbq_plan(
    men: int = 4,
    women: int = 4,
    kids: int = 2,
    duration_hours: int = 5,
    beer_type: str = "spaten_lata_350ml", # ou heineken, amstel, corona
    include_wine: bool = False
) -> Dict[str, Any]:
    """
    Calcula consumo por pessoa baseado em métricas reais de churrasco:
    - Homens: 450g carne, 5 latas cerveja (base 4h + 1 lata/h extra)
    - Mulheres: 300g carne, 3 latas cerveja (base 4h + 0.8 lata/h extra)
    - Crianças: 150g carne, 400ml refrigerante/suco
    """
    men = max(0, int(men))
    women = max(0, int(women))
    kids = max(0, int(kids))
    duration_hours = max(2, int(duration_hours))
    extra_hours = max(0, duration_hours - 4)

    # 1. Carnes (Kg)
    total_meat_kg = (men * 0.45) + (women * 0.30) + (kids * 0.15)
    # Aumenta 10% por hora extra além de 4h
    total_meat_kg *= (1 + (extra_hours * 0.08))
    total_meat_kg = round(total_meat_kg, 2)

    # Distribuição recomendada de carnes
    picanha_kg = round(total_meat_kg * 0.35, 2)
    contrafile_kg = round(total_meat_kg * 0.25, 2)
    linguica_kg = round(total_meat_kg * 0.25, 2)
    frango_kg = round(total_meat_kg * 0.15, 2)

    # 2. Bebidas
    # Cerveja (Latas 350ml)
    beer_cans_men = men * (5 + (extra_hours * 1.2))
    beer_cans_women = women * (3 + (extra_hours * 0.8))
    total_beer_cans = int(round(beer_cans_men + beer_cans_women))

    # Refrigerante (Garrafas 2L)
    soda_liters = (kids * (0.5 + (extra_hours * 0.1))) + ((men + women) * 0.25)
    soda_2l_bottles = max(1, int(round(soda_liters / 2.0)))

    # Acompanhamentos Essenciais
    adults = men + women
    carvao_kg = max(4, int(round(total_meat_kg * 1.0))) # 1kg carvão por kg carne
    gelo_kg = max(5, int(round(adults * 1.2)))
    pao_alho_pct = max(1, int(round(adults / 4.0)))

    # 3. Precificação por Supermercado em Sertãozinho
    catalog_map = {item["id"]: item for item in BASIC_CATALOG}
    
    picanha_item = catalog_map.get("picanha_kg", {})
    contrafile_item = catalog_map.get("contrafile_kg", {})
    linguica_item = catalog_map.get("linguica_toscana_kg", {})
    frango_item = catalog_map.get("frango_file_kg", {})
    beer_item = catalog_map.get(beer_type, catalog_map.get("spaten_lata_350ml", {}))
    soda_item = catalog_map.get("coca_cola_2l", {})

    def get_store_price(item, store_key):
        return item.get(store_key, {}).get("price", 0.0)

    stores = ["savegnago", "copercana", "paulistao"]
    totals = {}
    itemized = {
        "picanha": {"name": "Picanha Bovina", "qty": picanha_kg, "unit": "kg"},
        "contrafile": {"name": "Contrafilé", "qty": contrafile_kg, "unit": "kg"},
        "linguica": {"name": "Linguiça Toscana", "qty": linguica_kg, "unit": "kg"},
        "frango": {"name": "Filé de Frango", "qty": frango_kg, "unit": "kg"},
        "cerveja": {"name": beer_item.get("short_name", "Cerveja Lata"), "qty": total_beer_cans, "unit": "latas"},
        "refrigerante": {"name": "Coca-Cola 2L", "qty": soda_2l_bottles, "unit": "pet 2L"},
        "carvao": {"name": "Carvão Especial 4kg", "qty": max(1, carvao_kg // 4), "unit": "saco 4kg", "fixed_price": 18.90},
        "gelo": {"name": "Gelo em Cubos 5kg", "qty": max(1, gelo_kg // 5), "unit": "saco 5kg", "fixed_price": 12.00},
        "pao_alho": {"name": "Pão de Alho 400g", "qty": pao_alho_pct, "unit": "pct", "fixed_price": 12.90}
    }

    for store in stores:
        st_total = 0.0
        st_total += picanha_kg * get_store_price(picanha_item, store)
        st_total += contrafile_kg * get_store_price(contrafile_item, store)
        st_total += linguica_kg * get_store_price(linguica_item, store)
        st_total += frango_kg * get_store_price(frango_item, store)
        st_total += total_beer_cans * get_store_price(beer_item, store)
        st_total += soda_2l_bottles * get_store_price(soda_item, store)
        # Fixos
        st_total += (max(1, carvao_kg // 4) * 18.90)
        st_total += (max(1, gelo_kg // 5) * 12.00)
        st_total += (pao_alho_pct * 12.90)
        totals[store] = round(st_total, 2)

    # 4. Cálculo do Mix Otimizado (Melhor loja para cada item)
    mix_total = 0.0
    best_picks = {}
    for k, item_obj in [
        ("Picanha", (picanha_kg, picanha_item)),
        ("Contrafilé", (contrafile_kg, contrafile_item)),
        ("Linguiça", (linguica_kg, linguica_item)),
        ("Frango", (frango_kg, frango_item)),
        ("Cerveja", (total_beer_cans, beer_item)),
        ("Refrigerante", (soda_2l_bottles, soda_item))
    ]:
        qty, catalog_entry = item_obj
        store_prices = [(s, get_store_price(catalog_entry, s)) for s in stores if get_store_price(catalog_entry, s) > 0]
        if store_prices:
            store_prices.sort(key=lambda x: x[1])
            best_st, best_pr = store_prices[0]
            cost = qty * best_pr
            mix_total += cost
            best_picks[k] = {"store": best_st, "unit_price": best_pr, "total_cost": round(cost, 2), "qty": qty}

    mix_total += (max(1, carvao_kg // 4) * 18.90) + (max(1, gelo_kg // 5) * 12.00) + (pao_alho_pct * 12.90)
    totals["mix_otimizado"] = round(mix_total, 2)

    # Ranking
    ranked_stores = [
        {"store": "Paulistão Atacadista", "store_key": "paulistao", "total": totals["paulistao"]},
        {"store": "Supermercados Copercana", "store_key": "copercana", "total": totals["copercana"]},
        {"store": "Savegnago Supermercados", "store_key": "savegnago", "total": totals["savegnago"]},
    ]
    ranked_stores.sort(key=lambda x: x["total"])

    best_single_store = ranked_stores[0]
    worst_single_store = ranked_stores[-1]
    economy_mix = round(worst_single_store["total"] - totals["mix_otimizado"], 2)

    return {
        "params": {
            "men": men,
            "women": women,
            "kids": kids,
            "total_people": men + women + kids,
            "duration_hours": duration_hours,
            "beer_type": beer_type
        },
        "quantities": {
            "total_meat_kg": total_meat_kg,
            "picanha_kg": picanha_kg,
            "contrafile_kg": contrafile_kg,
            "linguica_kg": linguica_kg,
            "frango_kg": frango_kg,
            "total_beer_cans": total_beer_cans,
            "soda_2l_bottles": soda_2l_bottles,
            "carvao_kg": carvao_kg,
            "gelo_kg": gelo_kg,
            "pao_alho_pct": pao_alho_pct
        },
        "itemized": itemized,
        "totals": totals,
        "ranked_stores": ranked_stores,
        "best_picks": best_picks,
        "economy_mix": economy_mix,
        "cost_per_person": round(totals["mix_otimizado"] / max(1, (men + women + kids)), 2)
    }
