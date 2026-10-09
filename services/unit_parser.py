"""
Extrator e Normalizador Inteligente de Preço por Unidade, Volume e Formato.
Trata especificamente cada setor com rigorosa ordem de precedência:
1. Ovos: Preço por Ovo (ex: Bandeja c/ 30 ovos -> R$ 0,58/ovo).
2. Bebidas, Cervejas, Vinhos & Refrigerantes: Latas (350ml, 269ml), Long Necks (330ml), Latões (473ml), Garrafas (750ml, 600ml), Pet 2L, Packs (6, 8, 12, 15, 18, 24) e Litro (R$/L).
3. Limpeza: Detergente Líquido (R$/frasco e R$/L), Papel Higiênico (R$/rolo), Sabão Líquido (R$/L em galão), Sabão em Pó (R$/kg), Amaciante (R$/frasco), Desinfetante/Água Sanitária (R$/frasco).
4. Laticínios: Leite (R$/L), Manteiga (R$/pote), Requeijão (R$/copo), Queijo/Mussarela (R$/kg).
5. Carnes & Açougue / Hortifruti: Preço por Quilo (R$/kg), exceto hambúrguer por unidade.
6. Mercearia: Arroz (5kg -> R$/kg), Feijão (1kg -> R$/kg), Café (R$/pct), Óleo (R$/frasco e R$/L), Azeite (R$/garrafa), Molho de Tomate (R$/sachê), Macarrão (R$/pct).
7. Higiene: Sabonetes (R$/sabonete), Creme Dental (R$/tubo), Shampoo (R$/frasco).
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
    name_lower = (name or "").lower().strip()
    price = float(price) if price else 0.0
    orig_price = float(original_price) if (original_price and original_price > price) else None
    cat = (category or "").lower().strip()

    # =========================================================================
    # 1. OVOS (Bandejas de 10, 12, 20, 30 unidades)
    # =========================================================================
    if "ovo" in name_lower and not ("macarrão" in name_lower or "macarrao" in name_lower):
        match_eggs = re.search(r'(\d+)\s*(?:unidades|unids|unid|un|ovos)', name_lower)
        if match_eggs:
            units_count = int(match_eggs.group(1))
        elif "30" in name_lower:
            units_count = 30
        elif "20" in name_lower:
            units_count = 20
        elif "12" in name_lower or "dúzia" in name_lower or "duzia" in name_lower:
            units_count = 12
        elif "10" in name_lower:
            units_count = 10
        elif "6" in name_lower:
            units_count = 6
        else:
            units_count = 30

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
    # 2. BEBIDAS, CERVEJAS, VINHOS, REFRIGERANTES & SUCOS
    # Deve vir antes de mercearia para que "Coca-Cola Sem Açúcar" não caia em "açúcar 1kg"
    # =========================================================================
    is_beverage = (
        cat in ["cerveja", "vinho"] or 
        any(k in name_lower for k in [
            "cerveja", "chopp", "chope", "vinho", "espumante", "refrigerante", "coca-cola", "guaraná", "guarana", 
            "red bull", "energético", "energetico", "suco", "fanta", "sprite", "pepsi", "heineken", "spaten", 
            "corona", "amstel", "brahma", "skol", "budweiser", "stella", "eisenbahn", "colorado", "bohemia", "becks"
        ])
    )

    if is_beverage:
        units_count = 1

        # A) Padrão "12x350ml", "6 x 330ml"
        m_nx = re.search(r'(\d+)\s*x\s*(\d+)?\s*(?:ml|l)?', name_lower)
        if m_nx:
            c = int(m_nx.group(1))
            if 2 <= c <= 48:
                units_count = c

        # B) Padrão "Pack 12", "Pack com 6", "Pack 12 Latas", "Pack 6 Long Necks", "Kit 6 Vinhos"
        if units_count == 1:
            m_pack = re.search(r'(?:pack|caixa|cx|fardo|kit|combo)\s*(?:de|c\/|com|contendo)?\s*(\d+)\s*(?:unidades|unids|unid|un|latas|latões|latoes|garrafas|long\s*necks|long\s*neck|vinhos)?\b', name_lower)
            if m_pack:
                c = int(m_pack.group(1))
                if 2 <= c <= 48:
                    units_count = c

        # C) Padrão "Pack Cerveja ... 6 Long Necks" / "Pack Cerveja ... 12 Latas"
        if units_count == 1:
            m_units = re.search(r'(\d+)\s*(?:latas|latões|latoes|garrafas|long\s*necks|long\s*neck|unidades|unids|unid|un)\b', name_lower)
            if m_units:
                c = int(m_units.group(1))
                if 2 <= c <= 48:
                    units_count = c

        # D) Padrão "Pack 12", "Pack 6" no início/fim
        if units_count == 1:
            m_pack_num = re.search(r'\bpack\s*(\d+)\b', name_lower)
            if m_pack_num:
                c = int(m_pack_num.group(1))
                if 2 <= c <= 48:
                    units_count = c

        # Sanity Check de Supermercado:
        # Se o nome diz "Pack 12 Latas" mas o preço é R$ 5,29 (preço unitário), units_count deve ser 1!
        if units_count >= 4 and price < 12.00:
            units_count = 1

        # Detecção de Volume Unitário
        unit_volume_ml = 350
        m_ml = re.search(r'(\d{3,4})\s*ml\b', name_lower)
        if m_ml:
            unit_volume_ml = int(m_ml.group(1))
        else:
            m_litro = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:l|litro|litros)\b', name_lower)
            if m_litro:
                vol_l = float(m_litro.group(1).replace(',', '.'))
                unit_volume_ml = int(vol_l * 1000)
            elif cat == "vinho" or "vinho" in name_lower or "espumante" in name_lower:
                unit_volume_ml = 750
            elif "refrigerante" in name_lower or "coca-cola" in name_lower or "guaraná" in name_lower or "guarana" in name_lower:
                unit_volume_ml = 2000

        # Tipo de Recipiente
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
        elif "pet" in name_lower or unit_volume_ml >= 1500:
            container_type = f"Pet {unit_volume_ml / 1000:g}L"
            unit_name = "garrafa"
        elif cat == "vinho" or "vinho" in name_lower or "espumante" in name_lower:
            container_type = "Garrafa 750ml"
            unit_name = "garrafa"
        elif "garrafa" in name_lower or unit_volume_ml in [600, 750, 1000]:
            container_type = f"Garrafa {unit_volume_ml}ml"
            unit_name = "garrafa"
        else:
            container_type = f"Lata {unit_volume_ml}ml"
            unit_name = "lata"

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

    # =========================================================================
    # 3. LIMPEZA & LAVANDERIA (Detergentes, Sabão Líquido, Papel, etc.)
    # =========================================================================
    if cat == "limpeza" or any(k in name_lower for k in ["detergente", "papel higiênico", "papel higienico", "sabão", "sabao", "amaciante", "água sanitária", "agua sanitaria", "desinfetante"]):
        # A) Detergente Líquido (Frascos 500ml)
        if "detergente" in name_lower:
            vol_ml = 500
            m_ml = re.search(r'(\d+)\s*ml', name_lower)
            if m_ml:
                vol_ml = int(m_ml.group(1))

            m_pack = re.search(r'(\d+)\s*(?:unidades|unids|unid|un|frascos)', name_lower)
            units_count = 1
            if m_pack and price >= 6.0:
                c = int(m_pack.group(1))
                if 2 <= c <= 24:
                    units_count = c

            unit_p = round(price / units_count, 2)
            orig_unit_p = round(orig_price / units_count, 2) if orig_price else None
            price_per_l = round((unit_p / vol_ml) * 1000, 2) if vol_ml > 0 else None
            is_pack = units_count > 1

            return {
                "is_pack": is_pack,
                "units_count": units_count,
                "unit_volume_ml": vol_ml,
                "container_type": f"Frasco {vol_ml}ml",
                "unit_name": "frasco",
                "pack_label": f"Pack c/ {units_count} frascos" if is_pack else f"Frasco {vol_ml}ml",
                "unit_price": unit_p,
                "orig_unit_price": orig_unit_p,
                "price_per_liter": price_per_l,
                "unit_price_display": f"R$ {unit_p:.2f}".replace('.', ',') + " / frasco"
            }

        # B) Papel Higiênico (12, 16, 24, 32 rolos)
        if "papel" in name_lower or "higienico" in name_lower or "higiênico" in name_lower:
            match_rolls = re.search(r'(\d+)\s*(?:rolos|rolo|unidades|un)', name_lower)
            rolls = int(match_rolls.group(1)) if match_rolls else 12
            if rolls <= 0:
                rolls = 12

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

        # C) Sabão Líquido / Lava Roupas Líquido em Galão ou Refil (1.8L, 3L, 5L)
        if any(k in name_lower for k in ["sabão líquido", "sabao liquido", "lava-roupas líquido", "lava roupas liquido", "lava-roupas", "lava roupas", "omo líquido", "omo liquido", "ariel"]):
            match_liters = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:l|litros|litro)\b', name_lower)
            liters = float(match_liters.group(1).replace(',', '.')) if match_liters else 3.0
            if liters <= 0:
                liters = 3.0

            unit_p = round(price / liters, 2)
            orig_unit_p = round(orig_price / liters, 2) if orig_price else None
            container = f"Galão {liters:g}L" if liters >= 3 else f"Frasco {liters:g}L"
            return {
                "is_pack": True,
                "units_count": int(liters) if liters >= 1 else 1,
                "unit_volume_ml": int(liters * 1000),
                "container_type": container,
                "unit_name": "litro",
                "pack_label": container,
                "unit_price": unit_p,
                "orig_unit_price": orig_unit_p,
                "price_per_liter": unit_p,
                "unit_price_display": f"R$ {unit_p:.2f}".replace('.', ',') + " / L"
            }

        # D) Sabão em Pó (1.6kg, 2kg, etc.)
        if "pó" in name_lower or "po" in name_lower:
            match_kg = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:kg|quilos)\b', name_lower)
            kg = float(match_kg.group(1).replace(',', '.')) if match_kg else 1.6
            if kg <= 0:
                kg = 1.6

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

        # E) Amaciante (1.5L, 2L, 3L, 500ml)
        if "amaciante" in name_lower:
            match_l = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:l|litros|litro)\b', name_lower)
            vol_l = float(match_l.group(1).replace(',', '.')) if match_l else 1.5
            price_per_l = round(price / vol_l, 2) if vol_l > 0 else None
            return {
                "is_pack": False,
                "units_count": 1,
                "unit_volume_ml": int(vol_l * 1000),
                "container_type": f"Frasco {vol_l:g}L",
                "unit_name": "frasco",
                "pack_label": f"Frasco {vol_l:g}L",
                "unit_price": price,
                "orig_unit_price": orig_price,
                "price_per_liter": price_per_l,
                "unit_price_display": f"R$ {price:.2f}".replace('.', ',') + " / frasco"
            }

        # F) Desinfetante / Água Sanitária (500ml, 1L, 2L)
        match_vol = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:l|litros|litro)\b', name_lower)
        vol_l = float(match_vol.group(1).replace(',', '.')) if match_vol else 1.0
        price_per_l = round(price / vol_l, 2) if vol_l > 0 else None
        return {
            "is_pack": False,
            "units_count": 1,
            "unit_volume_ml": int(vol_l * 1000),
            "container_type": f"Frasco {vol_l:g}L" if vol_l != 1 else "Frasco 1L",
            "unit_name": "frasco",
            "pack_label": f"Frasco {vol_l:g}L" if vol_l != 1 else "Frasco 1L",
            "unit_price": price,
            "orig_unit_price": orig_price,
            "price_per_liter": price_per_l,
            "unit_price_display": f"R$ {price:.2f}".replace('.', ',') + " / un"
        }

    # =========================================================================
    # 4. LATICÍNIOS (Leite, Requeijão, Manteiga, Queijo Mussarela)
    # =========================================================================
    if cat == "laticinios" or any(k in name_lower for k in ["leite longa vida", "leite uht", "requeijão", "requeijao", "manteiga", "mussarela", "queijo prato", "queijo fatiado"]):
        if "leite" in name_lower and not "leite condensado" in name_lower:
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

        if "requeijão" in name_lower or "requeijao" in name_lower:
            return {
                "is_pack": False,
                "units_count": 1,
                "unit_volume_ml": None,
                "container_type": "Copo 200g",
                "unit_name": "copo 200g",
                "pack_label": "Copo 200g",
                "unit_price": price,
                "orig_unit_price": orig_price,
                "price_per_liter": None,
                "unit_price_display": f"R$ {price:.2f}".replace('.', ',') + " / un"
            }

        if "manteiga" in name_lower:
            return {
                "is_pack": False,
                "units_count": 1,
                "unit_volume_ml": None,
                "container_type": "Pote 200g",
                "unit_name": "pote 200g",
                "pack_label": "Pote 200g",
                "unit_price": price,
                "orig_unit_price": orig_price,
                "price_per_liter": None,
                "unit_price_display": f"R$ {price:.2f}".replace('.', ',') + " / un"
            }

        if any(k in name_lower for k in ["mussarela", "queijo", "prato"]):
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
    # 5. AÇOUGUE & CARNES / HORTIFRUTI (Preço por Kg, exceto hambúrguer avulso)
    # =========================================================================
    if cat in ["acougue", "hortifruti"] or (
        any(k in name_lower for k in ["picanha", "contrafilé", "contrafile", "alcatra", "maminha", "patinho", "carne moída", "carne moida", "frango", "linguiça", "linguica", "fraldinha", "bife ancho", "costela", "acém", "acem", "banana", "cebola", "batata"]) 
        and not ("molho" in name_lower or "extrato" in name_lower or "macarrão" in name_lower or "macarrao" in name_lower)
    ):
        if "hambúrguer" in name_lower or "hamburguer" in name_lower:
            return {
                "is_pack": False,
                "units_count": 1,
                "unit_volume_ml": None,
                "container_type": "Unidade",
                "unit_name": "un",
                "pack_label": "1 Unidade",
                "unit_price": price,
                "orig_unit_price": orig_price,
                "price_per_liter": None,
                "unit_price_display": f"R$ {price:.2f}".replace('.', ',') + " / un"
            }

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
    # 6. MERCEARIA & CESTA BÁSICA (Arroz, Feijão, Café, Óleo, Molhos, Macarrão)
    # =========================================================================
    if cat == "mercearia" or any(k in name_lower for k in ["arroz", "feijão", "feijao", "açúcar", "acucar", "café", "cafe", "óleo de soja", "oleo de soja", "azeite", "farinha de trigo", "macarrão", "macarrao", "molho de tomate", "extrato de tomate", "maionese", "sal refinado"]):
        # Arroz 5kg
        if "arroz" in name_lower and ("5kg" in name_lower or "5 kg" in name_lower or price >= 18.0):
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

        # Feijão 1kg / Açúcar 1kg / Sal 1kg / Farinha 1kg
        if any(g in name_lower for g in ["feijão", "feijao", "açúcar", "acucar", "sal refinado", "farinha"]):
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

        # Café 500g / 250g / 1kg
        if "café" in name_lower or "cafe" in name_lower:
            weight_label = "500g"
            if "1kg" in name_lower or "1 kg" in name_lower or "1000g" in name_lower:
                weight_label = "1kg"
            elif "250g" in name_lower or "250 g" in name_lower:
                weight_label = "250g"

            return {
                "is_pack": False,
                "units_count": 1,
                "unit_volume_ml": None,
                "container_type": f"Pacote {weight_label}",
                "unit_name": f"pct {weight_label}",
                "pack_label": f"Pacote {weight_label}",
                "unit_price": price,
                "orig_unit_price": orig_price,
                "price_per_liter": None,
                "unit_price_display": f"R$ {price:.2f}".replace('.', ',') + f" / {weight_label}"
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

        # Azeite 500ml
        if "azeite" in name_lower:
            price_l = round((price / 500) * 1000, 2)
            return {
                "is_pack": False,
                "units_count": 1,
                "unit_volume_ml": 500,
                "container_type": "Garrafa 500ml",
                "unit_name": "garrafa",
                "pack_label": "Garrafa 500ml",
                "unit_price": price,
                "orig_unit_price": orig_price,
                "price_per_liter": price_l,
                "unit_price_display": f"R$ {price:.2f}".replace('.', ',') + " / garrafa"
            }

        # Molho de Tomate / Extrato 300g / 340g
        if "molho" in name_lower or "extrato" in name_lower or ("tomate" in name_lower and ("sachê" in name_lower or "sache" in name_lower or "300g" in name_lower or "340g" in name_lower)):
            return {
                "is_pack": False,
                "units_count": 1,
                "unit_volume_ml": None,
                "container_type": "Sachê 300g",
                "unit_name": "sachê",
                "pack_label": "Sachê 300g",
                "unit_price": price,
                "orig_unit_price": orig_price,
                "price_per_liter": None,
                "unit_price_display": f"R$ {price:.2f}".replace('.', ',') + " / sachê"
            }

        # Macarrão 500g
        if "macarrão" in name_lower or "macarrao" in name_lower:
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

        # Maionese 500g
        if "maionese" in name_lower:
            return {
                "is_pack": False,
                "units_count": 1,
                "unit_volume_ml": None,
                "container_type": "Pote 500g",
                "unit_name": "pote 500g",
                "pack_label": "Pote 500g",
                "unit_price": price,
                "orig_unit_price": orig_price,
                "price_per_liter": None,
                "unit_price_display": f"R$ {price:.2f}".replace('.', ',') + " / un"
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
    # 7. HIGIENE PESSOAL (Creme Dental, Sabonete, Shampoo)
    # =========================================================================
    if cat == "higiene":
        unit_n = "sabonete" if "sabonete" in name_lower else ("tubo" if "creme dental" in name_lower or "pasta" in name_lower else "frasco")
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

    # Fallback Geral
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
