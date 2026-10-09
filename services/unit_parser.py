"""
Extrator e Normalizador Inteligente de Preço por Unidade, Volume e Formato.
Trata especificamente cada setor:
1. Bebidas & Cervejas: Latas (350ml, 269ml), Long Necks (330ml), Latões (473ml), Garrafas, Packs de 6, 8, 12, 15, 18, 24 e Litro (R$/L).
2. Ovos & Laticínios: Preço por Ovo (ex: Bandeja c/ 30 ovos -> R$ 0,58/ovo), Leite por Litro (R$/L).
3. Açougue & Carnes: Preço por Quilo (R$/kg).
4. Mercearia & Cesta Básica: Arroz (5kg -> R$/kg), Feijão (1kg -> R$/kg), Café (500g -> R$/pct ou R$/kg), Óleo (900ml -> R$/un ou R$/L).
5. Limpeza: Papel Higiênico (R$/rolo), Sabão Líquido (R$/L), Sabão em Pó (R$/kg), Detergente (R$/frasco).
6. Higiene: Sabonetes (R$/un), Creme Dental (R$/tubo), Shampoo (R$/frasco).
"""
import re
from typing import Dict, Any, Optional

def parse_unit_pricing(
    name: str,
    price: float,
    original_price: Optional[float] = None,
    category: str = "cerveja"
) -> Dict[str, Any]:
    """
    Analisa o produto de acordo com sua categoria real e extrai informações unitárias precisas.
    """
    name_lower = name.lower()
    price = float(price) if price else 0.0
    orig_price = float(original_price) if (original_price and original_price > price) else None

    # Normaliza categoria
    cat = (category or "").lower()

    # =========================================================================
    # CASO 1: AÇOUGUE & CARNES / HORTIFRUTI (Preço sempre por Quilo)
    # =========================================================================
    if cat in ["acougue", "hortifruti"] or any(k in name_lower for k in ["picanha", "contrafilé", "contrafile", "alcatra", "maminha", "patinho", "carne moída", "carne moida", "frango", "linguiça", "linguica", "banana", "tomate", "cebola", "batata"]):
        return {
            "is_pack": False,
            "units_count": 1,
            "unit_volume_ml": None,
            "container_type": "Quilo (Kg)",
            "unit_name": "kg",
            "pack_label": "Preço por Kg",
            "unit_price": price,
            "orig_unit_price": orig_price,
            "price_per_liter": None,
            "unit_price_display": f"R$ {price:.2f}".replace('.', ',') + " / kg"
        }

    # =========================================================================
    # CASO 2: OVOS (Bandejas de 10, 12, 20, 30 unidades)
    # =========================================================================
    if "ovo" in name_lower and not "macarrão" in name_lower and not "macarrao" in name_lower:
        match_eggs = re.search(r'(\d+)\s*(?:unidades|unids|unid|un|ovos)', name_lower)
        units_count = int(match_eggs.group(1)) if match_eggs else 30
        if units_count <= 0:
            units_count = 30

        unit_p = round(price / units_count, 2)
        orig_unit_p = round(orig_price / units_count, 2) if orig_price else None

        return {
            "is_pack": True,
            "units_count": units_count,
            "unit_volume_ml": None,
            "container_type": f"Bandeja c/ {units_count} ovos",
            "unit_name": "ovo",
            "pack_label": f"Bandeja c/ {units_count} ovos",
            "unit_price": unit_p,
            "orig_unit_price": orig_unit_p,
            "price_per_liter": None,
            "unit_price_display": f"R$ {unit_p:.2f}".replace('.', ',') + " / ovo"
        }

    # =========================================================================
    # CASO 3: MERCEARIA (Arroz, Feijão, Açúcar, Café, Óleo, Sal, Leite, etc.)
    # =========================================================================
    if cat == "mercearia":
        # Arroz 5kg
        if "arroz" in name_lower and "5kg" in name_lower:
            unit_p = round(price / 5.0, 2)
            orig_unit_p = round(orig_price / 5.0, 2) if orig_price else None
            return {
                "is_pack": True,
                "units_count": 5,
                "unit_volume_ml": None,
                "container_type": "Pacote 5kg",
                "unit_name": "kg",
                "pack_label": "Pacote 5kg",
                "unit_price": unit_p,
                "orig_unit_price": orig_unit_p,
                "price_per_liter": None,
                "unit_price_display": f"R$ {unit_p:.2f}".replace('.', ',') + " / kg"
            }
        
        # Feijão 1kg / Açúcar 1kg / Sal 1kg
        if any(g in name_lower for g in ["feijão", "feijao", "açúcar", "acucar", "sal refinado"]):
            return {
                "is_pack": False,
                "units_count": 1,
                "unit_volume_ml": None,
                "container_type": "Pacote 1kg",
                "unit_name": "kg",
                "pack_label": "Pacote 1kg",
                "unit_price": price,
                "orig_unit_price": orig_price,
                "price_per_liter": None,
                "unit_price_display": f"R$ {price:.2f}".replace('.', ',') + " / kg"
            }

        # Café 500g / 250g
        if "café" in name_lower or "cafe" in name_lower:
            return {
                "is_pack": False,
                "units_count": 1,
                "unit_volume_ml": None,
                "container_type": "Pacote 500g",
                "unit_name": "pct 500g",
                "pack_label": "Pacote 500g",
                "unit_price": price,
                "orig_unit_price": orig_price,
                "price_per_liter": None,
                "unit_price_display": f"R$ {price:.2f}".replace('.', ',') + " / pct"
            }

        # Óleo de Soja 900ml
        if "óleo" in name_lower or "oleo" in name_lower:
            price_l = round((price / 900) * 1000, 2)
            return {
                "is_pack": False,
                "units_count": 1,
                "unit_volume_ml": 900,
                "container_type": "Frasco 900ml",
                "unit_name": "frasco",
                "pack_label": "Frasco 900ml",
                "unit_price": price,
                "orig_unit_price": orig_price,
                "price_per_liter": price_l,
                "unit_price_display": f"R$ {price:.2f}".replace('.', ',') + " / un"
            }

        # Leite 1L
        if "leite" in name_lower:
            return {
                "is_pack": False,
                "units_count": 1,
                "unit_volume_ml": 1000,
                "container_type": "Caixa 1L",
                "unit_name": "litro",
                "pack_label": "Caixa 1L",
                "unit_price": price,
                "orig_unit_price": orig_price,
                "price_per_liter": price,
                "unit_price_display": f"R$ {price:.2f}".replace('.', ',') + " / L"
            }

        # Geral Mercearia
        return {
            "is_pack": False,
            "units_count": 1,
            "unit_volume_ml": None,
            "container_type": "Unidade",
            "unit_name": "un",
            "pack_label": "Unidade",
            "unit_price": price,
            "orig_unit_price": orig_price,
            "price_per_liter": None,
            "unit_price_display": f"R$ {price:.2f}".replace('.', ',') + " / un"
        }

    # =========================================================================
    # CASO 4: LIMPEZA & LAVANDERIA (OMO, Downy, Papel Higiênico, Ypê)
    # =========================================================================
    if cat == "limpeza":
        # Papel Higiênico (12 rolos, 16 rolos, etc.)
        if "papel" in name_lower or "higienico" in name_lower or "higiênico" in name_lower:
            match_rolls = re.search(r'(\d+)\s*(?:rolos|rolo|unidades|un)', name_lower)
            rolls = int(match_rolls.group(1)) if match_rolls else 12
            unit_p = round(price / rolls, 2)
            orig_unit_p = round(orig_price / rolls, 2) if orig_price else None
            return {
                "is_pack": True,
                "units_count": rolls,
                "unit_volume_ml": None,
                "container_type": f"Pacote c/ {rolls} rolos",
                "unit_name": "rolo",
                "pack_label": f"Pacote c/ {rolls} rolos",
                "unit_price": unit_p,
                "orig_unit_price": orig_unit_p,
                "price_per_liter": None,
                "unit_price_display": f"R$ {unit_p:.2f}".replace('.', ',') + " / rolo"
            }

        # Sabão Líquido (3L / 5L)
        if "líquido" in name_lower or "liquido" in name_lower:
            match_liters = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:l|litros|litro)\b', name_lower)
            liters = float(match_liters.group(1).replace(',', '.')) if match_liters else 3.0
            unit_p = round(price / liters, 2)
            orig_unit_p = round(orig_price / liters, 2) if orig_price else None
            return {
                "is_pack": True,
                "units_count": int(liters),
                "unit_volume_ml": int(liters * 1000),
                "container_type": f"Galão {liters:g}L",
                "unit_name": "litro",
                "pack_label": f"Galão {liters:g}L",
                "unit_price": unit_p,
                "orig_unit_price": orig_unit_p,
                "price_per_liter": unit_p,
                "unit_price_display": f"R$ {unit_p:.2f}".replace('.', ',') + " / L"
            }

        # Sabão em Pó (1.6kg / 2kg)
        if "pó" in name_lower or "po" in name_lower:
            match_kg = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:kg|quilos)\b', name_lower)
            kg = float(match_kg.group(1).replace(',', '.')) if match_kg else 1.6
            unit_p = round(price / kg, 2)
            orig_unit_p = round(orig_price / kg, 2) if orig_price else None
            return {
                "is_pack": True,
                "units_count": int(kg),
                "unit_volume_ml": None,
                "container_type": f"Caixa {kg:g}kg",
                "unit_name": "kg",
                "pack_label": f"Caixa {kg:g}kg",
                "unit_price": unit_p,
                "orig_unit_price": orig_unit_p,
                "price_per_liter": None,
                "unit_price_display": f"R$ {unit_p:.2f}".replace('.', ',') + " / kg"
            }

        # Detergente Ypê 500ml
        if "detergente" in name_lower:
            price_l = round((price / 500) * 1000, 2)
            return {
                "is_pack": False,
                "units_count": 1,
                "unit_volume_ml": 500,
                "container_type": "Frasco 500ml",
                "unit_name": "frasco",
                "pack_label": "Frasco 500ml",
                "unit_price": price,
                "orig_unit_price": orig_price,
                "price_per_liter": price_l,
                "unit_price_display": f"R$ {price:.2f}".replace('.', ',') + " / un"
            }

        # Limpeza Geral
        return {
            "is_pack": False,
            "units_count": 1,
            "unit_volume_ml": None,
            "container_type": "Unidade",
            "unit_name": "un",
            "pack_label": "Unidade",
            "unit_price": price,
            "orig_unit_price": orig_price,
            "price_per_liter": None,
            "unit_price_display": f"R$ {price:.2f}".replace('.', ',') + " / un"
        }

    # =========================================================================
    # CASO 5: HIGIENE PESSOAL (Creme Dental, Sabonete, Shampoo)
    # =========================================================================
    if cat == "higiene":
        unit_n = "sabonete" if "sabonete" in name_lower else ("tubo" if "creme dental" in name_lower or "pasta" in name_lower else "un")
        return {
            "is_pack": False,
            "units_count": 1,
            "unit_volume_ml": None,
            "container_type": "Unidade",
            "unit_name": unit_n,
            "pack_label": "Unidade Avulsa",
            "unit_price": price,
            "orig_unit_price": orig_price,
            "price_per_liter": None,
            "unit_price_display": f"R$ {price:.2f}".replace('.', ',') + f" / {unit_n}"
        }

    # =========================================================================
    # CASO 6: CERVEJAS & VINHOS & BEBIDAS (Lata, Long Neck, Garrafa, Pack, Litro)
    # =========================================================================
    units_count = 1

    # 1. Detecção de Quantidade
    match_nx = re.search(r'(\d+)\s*x\s*(\d+)?\s*(?:ml|l)?', name_lower)
    if match_nx:
        count = int(match_nx.group(1))
        if 2 <= count <= 48:
            units_count = count

    if units_count == 1:
        match_pack = re.search(r'(?:pack|caixa|cx|fardo|kit|combo)\s*(?:c\/|com|de|contendo)?\s*(\d+)\s*(?:un|unidades|latas|garrafas|long\s*neck)?', name_lower)
        if match_pack:
            count = int(match_pack.group(1))
            if 2 <= count <= 48:
                units_count = count

    if units_count == 1:
        match_units = re.search(r'(\d+)\s*(?:latas|garrafas|unidades|unids|unid|un)\b', name_lower)
        if match_units:
            count = int(match_units.group(1))
            if 2 <= count <= 48:
                units_count = count

    if units_count == 1:
        match_pack_num = re.search(r'\bpack\s*(\d+)\b', name_lower)
        if match_pack_num:
            count = int(match_pack_num.group(1))
            if 2 <= count <= 48:
                units_count = count

    # 2. Volume Unitário
    unit_volume_ml = 350
    match_vol_ml = re.search(r'(\d{3,4})\s*ml\b', name_lower)
    if match_vol_ml:
        unit_volume_ml = int(match_vol_ml.group(1))
    else:
        match_litro = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:l|litro|litros)\b', name_lower)
        if match_litro:
            vol_l = float(match_litro.group(1).replace(',', '.'))
            unit_volume_ml = int(vol_l * 1000)
        elif cat == "vinho":
            unit_volume_ml = 750

    # 3. Tipo de Recipiente
    if "long neck" in name_lower or "ln" in name_lower or unit_volume_ml == 330:
        container_type = f"Long Neck {unit_volume_ml}ml"
        unit_name = "long neck"
    elif "latao" in name_lower or "latão" in name_lower or unit_volume_ml == 473:
        container_type = f"Latão {unit_volume_ml}ml"
        unit_name = "latão"
    elif "lata" in name_lower or unit_volume_ml in [269, 310, 350, 355]:
        container_type = f"Lata {unit_volume_ml}ml"
        unit_name = "lata"
    elif "barril" in name_lower or unit_volume_ml >= 4000:
        container_type = f"Barril {unit_volume_ml // 1000}L"
        unit_name = "barril"
    elif "garrafa" in name_lower or unit_volume_ml in [600, 750, 1000]:
        container_type = f"Garrafa {unit_volume_ml}ml"
        unit_name = "garrafa"
    elif "pet" in name_lower or unit_volume_ml >= 1500:
        container_type = f"Pet {unit_volume_ml / 1000:g}L"
        unit_name = "garrafa"
    elif cat == "vinho":
        container_type = "Garrafa 750ml"
        unit_name = "garrafa"
    else:
        container_type = f"Lata {unit_volume_ml}ml"
        unit_name = "lata"

    # =========================================================================
    # REGRA CRÍTICA DE VALIDAÇÃO DE PREÇO REAL DE CERVEJA (SANITY CHECK):
    # Se units_count >= 6 e o preço for menor que R$ 12,00 (ex: R$ 4,49 / R$ 5,29),
    # o preço coletado no supermercado é DA LATA AVULSA (não é o total de 12 latas por R$ 4,49!).
    # =========================================================================
    if units_count >= 4 and price < 12.00:
        units_count = 1

    unit_price = round(price / units_count, 2) if units_count > 0 else price
    orig_unit_price = round(orig_price / units_count, 2) if orig_price else None

    price_per_liter = None
    if unit_volume_ml and unit_volume_ml > 0 and unit_price > 0:
        price_per_liter = round((unit_price / unit_volume_ml) * 1000, 2)

    is_pack = units_count > 1
    if is_pack:
        pack_type_label = f"Pack c/ {units_count} {unit_name}s"
    else:
        pack_type_label = f"1 {unit_name.capitalize()} Avulsa"

    unit_price_formatted = f"R$ {unit_price:.2f}".replace('.', ',')
    unit_price_display = f"{unit_price_formatted} / {unit_name}"

    return {
        "is_pack": is_pack,
        "units_count": units_count,
        "unit_volume_ml": unit_volume_ml,
        "container_type": container_type,
        "unit_name": unit_name,
        "pack_label": pack_type_label,
        "unit_price": unit_price,
        "orig_unit_price": orig_unit_price,
        "price_per_liter": price_per_liter,
        "unit_price_display": unit_price_display
    }
