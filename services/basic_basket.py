"""
Catálogo Oficial de Itens Básicos de Supermercado e Bebidas para Sertãozinho/SP.
Permite à família consultar e comparar rapidamente itens essenciais do dia a dia
entre Savegnago, Copercana e Paulistão Atacadista.
"""
from typing import List, Dict, Any, Optional

BASIC_CATALOG: List[Dict[str, Any]] = [
    # -------------------------------------------------------------
    # 1. CESTA BÁSICA & MERCEARIA
    # -------------------------------------------------------------
    {
        "id": "arroz_5kg",
        "name": "Arroz Tipo 1 Pacote 5kg (Tio João / Camil)",
        "short_name": "Arroz 5kg",
        "category": "mercearia",
        "category_label": "🍚 Cesta Básica & Mercearia",
        "keywords": ["arroz", "arroz 5kg", "tio joao", "camil", "prato fino"],
        "unit": "pct 5kg",
        "savegnago": {"price": 28.90, "original_price": 32.90},
        "copercana": {"price": 27.90, "original_price": 31.90},
        "paulistao": {"price": 26.50, "original_price": 29.90},
    },
    {
        "id": "feijao_1kg",
        "name": "Feijão Carioca Tipo 1 1kg (Camil / Kicaldo)",
        "short_name": "Feijão Carioca 1kg",
        "category": "mercearia",
        "category_label": "🍚 Cesta Básica & Mercearia",
        "keywords": ["feijao", "feijão", "feijao carioca", "kicaldo", "camil"],
        "unit": "pct 1kg",
        "savegnago": {"price": 7.89, "original_price": 8.99},
        "copercana": {"price": 7.49, "original_price": 8.49},
        "paulistao": {"price": 6.99, "original_price": 7.99},
    },
    {
        "id": "oleo_soja",
        "name": "Óleo de Soja Refinado 900ml (Liza / Soya)",
        "short_name": "Óleo de Soja 900ml",
        "category": "mercearia",
        "category_label": "🍚 Cesta Básica & Mercearia",
        "keywords": ["oleo", "óleo", "oleo de soja", "soya", "liza"],
        "unit": "un 900ml",
        "savegnago": {"price": 6.89, "original_price": 7.59},
        "copercana": {"price": 6.79, "original_price": 7.49},
        "paulistao": {"price": 6.39, "original_price": 6.99},
    },
    {
        "id": "cafe_500g",
        "name": "Café Torrado e Moído Tradicional 500g (Pilão / 3 Corações)",
        "short_name": "Café 500g",
        "category": "mercearia",
        "category_label": "🍚 Cesta Básica & Mercearia",
        "keywords": ["cafe", "café", "pilao", "pilão", "3 coracoes", "tres coracoes"],
        "unit": "pct 500g",
        "savegnago": {"price": 18.90, "original_price": 22.90},
        "copercana": {"price": 17.90, "original_price": 21.90},
        "paulistao": {"price": 16.80, "original_price": 19.90},
    },
    {
        "id": "acucar_1kg",
        "name": "Açúcar Refinado 1kg (União / Caravelas)",
        "short_name": "Açúcar 1kg",
        "category": "mercearia",
        "category_label": "🍚 Cesta Básica & Mercearia",
        "keywords": ["acucar", "açúcar", "uniao", "união", "caravelas"],
        "unit": "pct 1kg",
        "savegnago": {"price": 4.49, "original_price": 4.99},
        "copercana": {"price": 4.39, "original_price": 4.89},
        "paulistao": {"price": 4.15, "original_price": 4.69},
    },
    {
        "id": "molho_tomate",
        "name": "Molho de Tomate Tradicional Sachê 300g (Elefante / Fugini)",
        "short_name": "Molho de Tomate 300g",
        "category": "mercearia",
        "category_label": "🍚 Cesta Básica & Mercearia",
        "keywords": ["molho", "molho de tomate", "extrato", "elefante", "fugini"],
        "unit": "un 300g",
        "savegnago": {"price": 2.29, "original_price": 2.79},
        "copercana": {"price": 2.19, "original_price": 2.69},
        "paulistao": {"price": 1.95, "original_price": 2.49},
    },
    {
        "id": "macarrao_500g",
        "name": "Macarrão com Ovos Espaguete 500g (Dona Benta / Adria)",
        "short_name": "Macarrão 500g",
        "category": "mercearia",
        "category_label": "🍚 Cesta Básica & Mercearia",
        "keywords": ["macarrao", "macarrão", "espaguete", "adria", "dona benta"],
        "unit": "pct 500g",
        "savegnago": {"price": 3.99, "original_price": 4.59},
        "copercana": {"price": 3.89, "original_price": 4.49},
        "paulistao": {"price": 3.49, "original_price": 4.19},
    },

    # -------------------------------------------------------------
    # 2. OVOS & LATICÍNIOS
    # -------------------------------------------------------------
    {
        "id": "ovos_30un",
        "name": "Ovos Brancos Grandes (Bandeja c/ 30 unidades)",
        "short_name": "Ovos Brancos (Cartela c/ 30)",
        "category": "mercearia",
        "category_label": "🥚 Ovos & Laticínios",
        "keywords": ["ovo", "ovos", "cartela de ovos", "bandeja de ovos", "ovos brancos", "ovo branco"],
        "unit": "cartela 30un",
        "savegnago": {"price": 19.90, "original_price": 23.90},
        "copercana": {"price": 18.90, "original_price": 22.90},
        "paulistao": {"price": 17.50, "original_price": 20.90},
    },
    {
        "id": "ovos_vermelhos_20un",
        "name": "Ovos Vermelhos Selecionados (Bandeja c/ 20 unidades)",
        "short_name": "Ovos Vermelhos (Cartela c/ 20)",
        "category": "mercearia",
        "category_label": "🥚 Ovos & Laticínios",
        "keywords": ["ovos vermelhos", "ovo vermelho", "ovos caipiras", "ovo caipira"],
        "unit": "cartela 20un",
        "savegnago": {"price": 16.90, "original_price": 19.90},
        "copercana": {"price": 16.49, "original_price": 18.90},
        "paulistao": {"price": 15.50, "original_price": 17.90},
    },
    {
        "id": "leite_1l",
        "name": "Leite Longa Vida UHT Integral 1L (Piracanjuba / Italac)",
        "short_name": "Leite UHT Integral 1L",
        "category": "mercearia",
        "category_label": "🥚 Ovos & Laticínios",
        "keywords": ["leite", "leite integral", "leite uht", "piracanjuba", "italac", "leite caixa"],
        "unit": "un 1L",
        "savegnago": {"price": 4.89, "original_price": 5.49},
        "copercana": {"price": 4.79, "original_price": 5.29},
        "paulistao": {"price": 4.49, "original_price": 4.99},
    },
    {
        "id": "manteiga_200g",
        "name": "Manteiga de Primeira Qualidade com Sal 200g (Aviação / Scala)",
        "short_name": "Manteiga c/ Sal 200g",
        "category": "mercearia",
        "category_label": "🥚 Ovos & Laticínios",
        "keywords": ["manteiga", "aviacao", "aviação", "scala", "margarina"],
        "unit": "un 200g",
        "savegnago": {"price": 12.90, "original_price": 14.90},
        "copercana": {"price": 12.49, "original_price": 13.90},
        "paulistao": {"price": 11.80, "original_price": 13.20},
    },
    {
        "id": "queijo_mussarela",
        "name": "Queijo Mussarela Fatiado Resfriado (Preço por Kg)",
        "short_name": "Mussarela Fatiada (Kg)",
        "category": "mercearia",
        "category_label": "🥚 Ovos & Laticínios",
        "keywords": ["mussarela", "mucarela", "muçarela", "queijo", "queijo mussarela"],
        "unit": "kg",
        "savegnago": {"price": 41.90, "original_price": 48.90},
        "copercana": {"price": 42.90, "original_price": 49.90},
        "paulistao": {"price": 38.90, "original_price": 44.90},
    },

    # -------------------------------------------------------------
    # 3. AÇOUGUE & CARNES
    # -------------------------------------------------------------
    {
        "id": "picanha_kg",
        "name": "Picanha Bovina Resfriada Peça / Kg",
        "short_name": "Picanha Bovina (Kg)",
        "category": "acougue",
        "category_label": "🥩 Açougue & Carnes",
        "keywords": ["picanha", "picanha bovina", "picanha churrasco"],
        "unit": "kg",
        "savegnago": {"price": 68.90, "original_price": 89.90},
        "copercana": {"price": 62.90, "original_price": 82.90},
        "paulistao": {"price": 57.90, "original_price": 74.90},
    },
    {
        "id": "contrafile_kg",
        "name": "Contrafilé Bovino Resfriado (Bife / Peça) Kg",
        "short_name": "Contrafilé Bovino (Kg)",
        "category": "acougue",
        "category_label": "🥩 Açougue & Carnes",
        "keywords": ["contrafile", "contrafilé", "contra file"],
        "unit": "kg",
        "savegnago": {"price": 39.90, "original_price": 49.90},
        "copercana": {"price": 38.90, "original_price": 47.90},
        "paulistao": {"price": 36.90, "original_price": 45.90},
    },
    {
        "id": "alcatra_kg",
        "name": "Alcatra com Maminha Bovina Kg",
        "short_name": "Alcatra Bovina (Kg)",
        "category": "acougue",
        "category_label": "🥩 Açougue & Carnes",
        "keywords": ["alcatra", "alcatra bovina", "maminha"],
        "unit": "kg",
        "savegnago": {"price": 42.90, "original_price": 52.90},
        "copercana": {"price": 41.90, "original_price": 49.90},
        "paulistao": {"price": 38.90, "original_price": 46.90},
    },
    {
        "id": "carne_moida_kg",
        "name": "Carne Moída Patinho Bovino Resfriado Kg",
        "short_name": "Carne Moída Patinho (Kg)",
        "category": "acougue",
        "category_label": "🥩 Açougue & Carnes",
        "keywords": ["carne moida", "carne moída", "patinho", "moida", "moída"],
        "unit": "kg",
        "savegnago": {"price": 34.90, "original_price": 41.90},
        "copercana": {"price": 33.90, "original_price": 39.90},
        "paulistao": {"price": 31.90, "original_price": 37.90},
    },
    {
        "id": "frango_file_kg",
        "name": "Filé de Peito de Frango Resfriado Kg",
        "short_name": "Filé de Peito de Frango (Kg)",
        "category": "acougue",
        "category_label": "🥩 Açougue & Carnes",
        "keywords": ["frango", "file de peito", "peito de frango", "file de frango"],
        "unit": "kg",
        "savegnago": {"price": 17.90, "original_price": 21.90},
        "copercana": {"price": 16.90, "original_price": 20.90},
        "paulistao": {"price": 15.80, "original_price": 18.90},
    },
    {
        "id": "linguica_toscana_kg",
        "name": "Linguiça Toscana para Churrasco Kg (Seara / Aurora)",
        "short_name": "Linguiça Toscana (Kg)",
        "category": "acougue",
        "category_label": "🥩 Açougue & Carnes",
        "keywords": ["linguica", "linguiça", "toscana", "linguica toscana", "seara", "aurora"],
        "unit": "kg",
        "savegnago": {"price": 19.90, "original_price": 24.90},
        "copercana": {"price": 18.90, "original_price": 23.90},
        "paulistao": {"price": 16.90, "original_price": 21.90},
    },

    # -------------------------------------------------------------
    # 4. LIMPEZA & LAVANDERIA
    # -------------------------------------------------------------
    {
        "id": "sabao_omo_liquido_3l",
        "name": "Sabão Líquido OMO Lavagem Perfeita 3 Litros",
        "short_name": "OMO Líquido 3L",
        "category": "limpeza",
        "category_label": "🧼 Limpeza & Lavanderia",
        "keywords": ["sabao liquido", "sabão líquido", "omo", "omo liquido", "omo líquido", "sabao omo"],
        "unit": "galão 3L",
        "savegnago": {"price": 38.90, "original_price": 52.90},
        "copercana": {"price": 39.90, "original_price": 54.90},
        "paulistao": {"price": 36.90, "original_price": 49.90},
    },
    {
        "id": "sabao_omo_po_1_6kg",
        "name": "Sabão em Pó OMO Lavagem Perfeita Caixa 1,6kg",
        "short_name": "OMO em Pó 1.6kg",
        "category": "limpeza",
        "category_label": "🧼 Limpeza & Lavanderia",
        "keywords": ["sabao em po", "sabão em pó", "omo po", "omo em pó"],
        "unit": "cx 1.6kg",
        "savegnago": {"price": 24.90, "original_price": 29.90},
        "copercana": {"price": 23.90, "original_price": 28.90},
        "paulistao": {"price": 21.90, "original_price": 26.50},
    },
    {
        "id": "amaciante_downy_comfort",
        "name": "Amaciante Concentrado Downy / Comfort 1,5L",
        "short_name": "Amaciante 1.5L",
        "category": "limpeza",
        "category_label": "🧼 Limpeza & Lavanderia",
        "keywords": ["amaciante", "downy", "comfort", "amaciante concentrado"],
        "unit": "frasco 1.5L",
        "savegnago": {"price": 23.90, "original_price": 29.90},
        "copercana": {"price": 22.90, "original_price": 28.90},
        "paulistao": {"price": 21.50, "original_price": 26.90},
    },
    {
        "id": "detergente_ype",
        "name": "Detergente Líquido Ypê 500ml (Neutro / Coco / Maçã)",
        "short_name": "Detergente Ypê 500ml",
        "category": "limpeza",
        "category_label": "🧼 Limpeza & Lavanderia",
        "keywords": ["detergente", "ype", "ypê", "detergente ype", "detergente ypê"],
        "unit": "frasco 500ml",
        "savegnago": {"price": 2.49, "original_price": 2.99},
        "copercana": {"price": 2.39, "original_price": 2.89},
        "paulistao": {"price": 2.15, "original_price": 2.65},
    },
    {
        "id": "papel_higienico_neve",
        "name": "Papel Higiênico Neve Folha Dupla / Tripla Pacote c/ 12 Rolos",
        "short_name": "Papel Neve 12 Rolos",
        "category": "limpeza",
        "category_label": "🧼 Limpeza & Lavanderia",
        "keywords": ["papel", "papel higienico", "papel higiênico", "neve", "papel neve"],
        "unit": "pct 12 rolos",
        "savegnago": {"price": 22.90, "original_price": 28.90},
        "copercana": {"price": 21.90, "original_price": 26.90},
        "paulistao": {"price": 19.90, "original_price": 24.90},
    },
    {
        "id": "desinfetante_pinho_sol",
        "name": "Desinfetante Pinho Sol / Veja Multiuso 1L",
        "short_name": "Pinho Sol / Veja 1L",
        "category": "limpeza",
        "category_label": "🧼 Limpeza & Lavanderia",
        "keywords": ["desinfetante", "pinho sol", "pinho", "veja", "multiuso"],
        "unit": "frasco 1L",
        "savegnago": {"price": 9.90, "original_price": 12.90},
        "copercana": {"price": 9.49, "original_price": 11.90},
        "paulistao": {"price": 8.80, "original_price": 10.90},
    },

    # -------------------------------------------------------------
    # 5. BEBIDAS (CERVEJAS & VINHOS)
    # -------------------------------------------------------------
    {
        "id": "heineken_lata_350ml",
        "name": "Cerveja Heineken Puro Malte Lata 350ml",
        "short_name": "Heineken Lata 350ml",
        "category": "cerveja",
        "category_label": "🍺 Bebidas & Cervejas",
        "keywords": ["heineken", "heineken lata", "cerveja heineken"],
        "unit": "lata 350ml",
        "savegnago": {"price": 5.39, "original_price": 5.89},
        "copercana": {"price": 5.59, "original_price": 5.99},
        "paulistao": {"price": 5.29, "original_price": 5.79},
    },
    {
        "id": "spaten_lata_350ml",
        "name": "Cerveja Spaten Munich Helles Puro Malte Lata 350ml",
        "short_name": "Spaten Lata 350ml",
        "category": "cerveja",
        "category_label": "🍺 Bebidas & Cervejas",
        "keywords": ["spaten", "spaten lata", "cerveja spaten"],
        "unit": "lata 350ml",
        "savegnago": {"price": 4.69, "original_price": 5.19},
        "copercana": {"price": 4.59, "original_price": 5.09},
        "paulistao": {"price": 4.49, "original_price": 4.99},
    },
    {
        "id": "corona_330ml",
        "name": "Cerveja Corona Extra Long Neck 330ml",
        "short_name": "Corona Long Neck 330ml",
        "category": "cerveja",
        "category_label": "🍺 Bebidas & Cervejas",
        "keywords": ["corona", "corona extra", "cerveja corona"],
        "unit": "long neck 330ml",
        "savegnago": {"price": 6.49, "original_price": 7.19},
        "copercana": {"price": 6.19, "original_price": 6.89},
        "paulistao": {"price": 5.99, "original_price": 6.59},
    },
    {
        "id": "amstel_lata_350ml",
        "name": "Cerveja Amstel Puro Malte Lata 350ml",
        "short_name": "Amstel Lata 350ml",
        "category": "cerveja",
        "category_label": "🍺 Bebidas & Cervejas",
        "keywords": ["amstel", "amstel lata", "cerveja amstel"],
        "unit": "lata 350ml",
        "savegnago": {"price": 3.99, "original_price": 4.39},
        "copercana": {"price": 3.99, "original_price": 4.39},
        "paulistao": {"price": 3.79, "original_price": 4.19},
    },
    {
        "id": "casillero_cabernet",
        "name": "Vinho Chileno Casillero del Diablo Cabernet Sauvignon 750ml",
        "short_name": "Casillero del Diablo 750ml",
        "category": "vinho",
        "category_label": "🍷 Vinhos & Espumantes",
        "keywords": ["casillero", "casillero del diablo", "vinho casillero"],
        "unit": "garrafa 750ml",
        "savegnago": {"price": 49.90, "original_price": 64.90},
        "copercana": {"price": 51.90, "original_price": 66.90},
        "paulistao": {"price": 47.90, "original_price": 59.90},
    },
    {
        "id": "concha_toro_reservado",
        "name": "Vinho Chileno Concha y Toro Reservado Tinto 750ml",
        "short_name": "Concha y Toro Reservado 750ml",
        "category": "vinho",
        "category_label": "🍷 Vinhos & Espumantes",
        "keywords": ["concha y toro", "reservado", "vinho reservado"],
        "unit": "garrafa 750ml",
        "savegnago": {"price": 33.90, "original_price": 39.90},
        "copercana": {"price": 34.90, "original_price": 41.90},
        "paulistao": {"price": 31.90, "original_price": 37.90},
    },
    {
        "id": "coca_cola_2l",
        "name": "Refrigerante Coca-Cola Pet 2 Litros",
        "short_name": "Coca-Cola 2L",
        "category": "cerveja",
        "category_label": "🍺 Bebidas & Cervejas",
        "keywords": ["coca", "coca cola", "coca-cola", "refrigerante"],
        "unit": "pet 2L",
        "savegnago": {"price": 9.49, "original_price": 10.49},
        "copercana": {"price": 9.29, "original_price": 10.19},
        "paulistao": {"price": 8.79, "original_price": 9.69},
    }
]

def find_staple_in_catalog(query: str) -> Optional[Dict[str, Any]]:
    """Encontra o item correspondente no catálogo básico oficial."""
    clean = query.lower().strip()
    words = set(clean.split())
    
    for item in BASIC_CATALOG:
        # Match direto em id ou short_name
        if clean in item["short_name"].lower() or item["short_name"].lower() in clean:
            return item
        # Match em keywords
        for kw in item["keywords"]:
            if kw in clean or clean in kw:
                return item
        # Match de palavras
        for w in words:
            if len(w) >= 3 and w in item["keywords"]:
                return item
    return None

def get_categories_grouped() -> Dict[str, List[Dict[str, Any]]]:
    """Retorna itens agrupados por categoria para navegação interativa."""
    grouped = {}
    for item in BASIC_CATALOG:
        cat_label = item["category_label"]
        if cat_label not in grouped:
            grouped[cat_label] = []
        grouped[cat_label].append(item)
    return grouped
