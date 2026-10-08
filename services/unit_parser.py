"""
Extrator e Normalizador Inteligente de Preço por Unidade (Lata, Long Neck, Garrafa e Volume).
Permite analisar e comparar bebidas pelo preço REAL por unidade (lata avulsa vs pack de 6, 12, 15, 18, 24).
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
    Analisa o nome do produto e extrai:
    - Quantidade de unidades no pacote (1, 6, 8, 12, 15, 18, 24, etc.)
    - Volume em ml por unidade (269, 310, 330, 350, 355, 473, 500, 600, 750, 1000)
    - Tipo de recipiente (Lata, Long Neck, Garrafa, Barril)
    - Preço unitário (R$/unidade)
    - Preço por litro (R$/L)
    - Rótulo amigável (ex: 'R$ 4,50 / lata 350ml')
    """
    name_lower = name.lower()
    
    # 1. Detecção de Quantidade de Unidades (Packs, Caixas, Fardos, Kits)
    units_count = 1
    
    # Padrões comuns de quantidade
    # ex: 12x 350ml, 24x350ml, 6x330ml
    match_nx = re.search(r'(\d+)\s*x\s*(\d+)?\s*(?:ml|l)?', name_lower)
    if match_nx:
        count = int(match_nx.group(1))
        if 2 <= count <= 48:
            units_count = count

    # ex: pack c/ 12, pack com 24, pack de 15, caixa com 12, fardo com 12, kit c/ 6
    if units_count == 1:
        match_pack = re.search(r'(?:pack|caixa|cx|fardo|kit|combo)\s*(?:c\/|com|de|contendo)?\s*(\d+)\s*(?:un|unidades|latas|garrafas|long\s*neck)?', name_lower)
        if match_pack:
            count = int(match_pack.group(1))
            if 2 <= count <= 48:
                units_count = count

    # ex: 12 latas, 24 latas, 6 unidades, 18 latas, 15 unidades
    if units_count == 1:
        match_units = re.search(r'(\d+)\s*(?:latas|garrafas|unidades|unids|unid|un)\b', name_lower)
        if match_units:
            count = int(match_units.group(1))
            if 2 <= count <= 48:
                units_count = count

    # ex: pack 12, pack 24, pack 6
    if units_count == 1:
        match_pack_num = re.search(r'\bpack\s*(\d+)\b', name_lower)
        if match_pack_num:
            count = int(match_pack_num.group(1))
            if 2 <= count <= 48:
                units_count = count

    # 2. Detecção de Volume Unitário (ml / Litro)
    unit_volume_ml = 350  # padrão para cerveja lata se não especificado
    
    match_vol_ml = re.search(r'(\d{3,4})\s*ml\b', name_lower)
    if match_vol_ml:
        unit_volume_ml = int(match_vol_ml.group(1))
    else:
        match_litro = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:l|litro|litros)\b', name_lower)
        if match_litro:
            vol_l = float(match_litro.group(1).replace(',', '.'))
            unit_volume_ml = int(vol_l * 1000)
        elif category == "vinho":
            unit_volume_ml = 750

    # 3. Tipo de Recipiente / Formato
    if "long neck" in name_lower or "ln" in name_lower or unit_volume_ml == 330:
        container_type = "Long Neck"
        unit_name = "long neck"
    elif "latao" in name_lower or "latão" in name_lower or unit_volume_ml == 473:
        container_type = "Latão 473ml"
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
    elif category == "vinho":
        container_type = "Garrafa 750ml"
        unit_name = "garrafa"
    else:
        container_type = "Unidade"
        unit_name = "un"

    # 4. Cálculo de Preço por Unidade e Preço por Litro
    price = float(price) if price else 0.0
    unit_price = round(price / units_count, 2) if units_count > 0 else price
    
    orig_unit_price = None
    if original_price and original_price > price:
        orig_unit_price = round(float(original_price) / units_count, 2)

    price_per_liter = None
    if unit_volume_ml > 0 and unit_price > 0:
        price_per_liter = round((unit_price / unit_volume_ml) * 1000, 2)

    # Descrição do Pacote
    is_pack = units_count > 1
    if is_pack:
        pack_type_label = f"Pack c/ {units_count} {unit_name}s"
    else:
        pack_type_label = f"Unidade Avulsa ({container_type})"

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
