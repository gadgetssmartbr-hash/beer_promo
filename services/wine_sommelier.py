"""
Especialista Sommelier de Vinhos Tintos Secos - Amazon Brasil (Prime)
Inteligência para identificação, avaliação de qualidade, notas de degustação e harmonização.
"""
import re
from typing import List, Dict, Any, Optional

# Termos expressamente proibidos (para garantir apenas vinhos tintos secos finos)
FORBIDDEN_TERMS = [
    "suave", "doce", "demi-seco", "demi seco", "meio seco", "frisante",
    "moscatel", "espumante", "branco", "rose", "rosé", "cooler",
    "filtrado", "bordo", "pérgola", "chalise", "sangria", "pergola"
]

# Base de uvas tintas consagradas
GRAPE_PROFILES = {
    "malbec": {
        "name": "Malbec",
        "origin_hint": "Argentina",
        "body": "Encorpado e Aveludado",
        "notes": "Ameixas pretas, amoras, toques de baunilha e chocolate.",
        "pairing": "Churrasco de cortes nobres (picanha, ancho, bife de chorizo) e hambúrguer na brasa."
    },
    "cabernet sauvignon": {
        "name": "Cabernet Sauvignon",
        "origin_hint": "Chile / Internacional",
        "body": "Estruturado e Potente",
        "notes": "Cassis, frutas vermelhas maduras, pimenta negra e notas de cedro/carvalho.",
        "pairing": "Carnes vermelhas assadas, cordeiro, massas com ragù encorpado e queijos maturados."
    },
    "cabernet franc": {
        "name": "Cabernet Franc",
        "origin_hint": "Argentina / França",
        "body": "Elegante e Herbáceo",
        "notes": "Framboesas, toques de pimentão tostado, grafite e especiarias finas.",
        "pairing": "Carnes magras grelhadas, risoto de cogumelos e queijo gouda ou canastra."
    },
    "carmenere": {
        "name": "Carménère",
        "origin_hint": "Chile",
        "body": "Médio a Encorpado, Taninos Sedosos",
        "notes": "Cerejas pretas, café, cacau e suave pimentão vermelho doce.",
        "pairing": "Massas ao molho vermelho, lasanha, risoto de funghi e carnes de panela."
    },
    "syrah": {
        "name": "Syrah / Shiraz",
        "origin_hint": "Internacional",
        "body": "Intenso e Condimentado",
        "notes": "Amoras silvestres, pimenta preta em grão, defumado e alcaçuz.",
        "pairing": "Costela no bafo, carne de porco assada com ervas e pratos com pimenta."
    },
    "pinot noir": {
        "name": "Pinot Noir",
        "origin_hint": "França / Patagônia",
        "body": "Corpo Leve a Médio, Muito Elegante",
        "notes": "Morangos frescos, cerejas, folhas secas e notas terrosas sutis.",
        "pairing": "Salmão grelhado, atum selado, pato, aves nobres e risoto de queijo brie."
    },
    "tannat": {
        "name": "Tannat",
        "origin_hint": "Uruguai / Campanha Gaúcha",
        "body": "Muito Encorpado e Tânico",
        "notes": "Frutas negras maduras, couro, tabaco e taninos firmes.",
        "pairing": "Carnes com alto teor de gordura, costelão e queijos azuis (gorgonzola)."
    },
    "primitivo": {
        "name": "Primitivo di Manduria",
        "origin_hint": "Itália (Puglia)",
        "body": "Encorpado, Quente e Frutado",
        "notes": "Compota de figo, ameixa passa, alcaçuz e canela com taninos muito macios.",
        "pairing": "Pizzas artesanais, massas à carbonara ou amatriciana e queijo pecorino."
    },
    "tempranillo": {
        "name": "Tempranillo",
        "origin_hint": "Espanha (Rioja / Ribera)",
        "body": "Equilibrado e Gastronômico",
        "notes": "Cerejas maduras, baunilha, couro e notas balsâmicas de envelhecimento em carvalho.",
        "pairing": "Tapas espanholas, jamón / presunto cru, paella de carne e queijo manchego."
    },
    "touriga nacional": {
        "name": "Touriga Nacional / Corte Português",
        "origin_hint": "Portugal (Douro / Dão / Alentejo)",
        "body": "Estruturado, Floral e Elegante",
        "notes": "Pétalas de violeta, mirtilo, esteva e especiarias marcantes.",
        "pairing": "Bacalhau assado na brasa, cozido à portuguesa, cabrito e queijo da serra da estrela."
    },
    "merlot": {
        "name": "Merlot",
        "origin_hint": "Chile / Brasil / França",
        "body": "Médio, Taninos Redondos",
        "notes": "Ameixas vermelhas, toques de chocolate e baunilha.",
        "pairing": "Massas leves, filé mignon grelhado e queijos de média cura."
    }
}

# Produtores e vinícolas de referência
FAMOUS_WINERIES = [
    ("concha y toro", "Concha y Toro", "Chile", "🇨🇱"),
    ("casillero del diablo", "Casillero del Diablo", "Chile", "🇨🇱"),
    ("marques de casa concha", "Marques de Casa Concha", "Chile", "🇨🇱"),
    ("catena zapata", "Catena Zapata", "Argentina", "🇦🇷"),
    ("dv catena", "D.V. Catena", "Argentina", "🇦🇷"),
    ("alamos", "Álamos (Catena)", "Argentina", "🇦🇷"),
    ("luigi bosca", "Luigi Bosca", "Argentina", "🇦🇷"),
    ("cordero con piel de lobo", "Cordero con Piel de Lobo", "Argentina", "🇦🇷"),
    ("mosquita muerta", "Mosquita Muerta", "Argentina", "🇦🇷"),
    ("esporão", "Esporão", "Portugal", "🇵🇹"),
    ("esporao", "Esporão", "Portugal", "🇵🇹"),
    ("pé tinto", "Pé Tinto (Esporão)", "Portugal", "🇵🇹"),
    ("pe tinto", "Pé Tinto (Esporão)", "Portugal", "🇵🇹"),
    ("alandra", "Alandra (Esporão)", "Portugal", "🇵🇹"),
    ("cartuxa", "Cartuxa (Fundação Eugénio de Almeida)", "Portugal", "🇵🇹"),
    ("monte velho", "Monte Velho (Esporão)", "Portugal", "🇵🇹"),
    ("quinta de bons ventos", "Quinta de Bons Ventos", "Portugal", "🇵🇹"),
    ("bons ventos", "Bons Ventos", "Portugal", "🇵🇹"),
    ("jp azeitão", "JP Azeitão (Bacalhôa)", "Portugal", "🇵🇹"),
    ("bacalhôa", "Bacalhôa", "Portugal", "🇵🇹"),
    ("monte das ânforas", "Monte das Ânforas", "Portugal", "🇵🇹"),
    ("escudo rojo", "Escudo Rojo (Rothschild)", "Chile", "🇨🇱"),
    ("miguel torres", "Miguel Torres", "Chile", "🇨🇱"),
    ("santo graal", "Santo Graal", "Chile", "🇨🇱"),
    ("latitud 33", "Latitud 33 (Chandon)", "Argentina", "🇦🇷"),
    ("cecchi", "Cecchi Chianti", "Itália", "🇮🇹"),
    ("chianti", "Chianti Classico", "Itália", "🇮🇹"),
    ("primitivo di manduria", "Primitivo di Manduria", "Itália", "🇮🇹"),
    ("primitivo", "Primitivo Italiano", "Itália", "🇮🇹"),
    ("montepulciano", "Montepulciano d'Abruzzo", "Itália", "🇮🇹"),
    ("trapiche", "Trapiche", "Argentina", "🇦🇷"),
    ("norton", "Bodega Norton", "Argentina", "🇦🇷"),
    ("rutini", "Rutini Wines", "Argentina", "🇦🇷"),
    ("salentein", "Salentein", "Argentina", "🇦🇷"),
    ("felino", "Cobos Felino (Paul Hobbs)", "Argentina", "🇦🇷"),
    ("chac chac", "Chac Chac (Viña Las Perdices)", "Argentina", "🇦🇷"),
    ("perez cruz", "Viña Perez Cruz", "Chile", "🇨🇱"),
    ("santa helena", "Santa Helena", "Chile", "🇨🇱"),
    ("tarapacá", "Viña Tarapacá", "Chile", "🇨🇱"),
    ("tarapaca", "Viña Tarapacá", "Chile", "🇨🇱"),
    ("montes alpha", "Montes Alpha", "Chile", "🇨🇱"),
    ("casa valduga", "Casa Valduga", "Brasil", "🇧🇷"),
    ("miolo", "Miolo", "Brasil", "🇧🇷"),
]

def is_good_dry_red(name: str, price: float = 0.0) -> bool:
    """Verifica com rigor se o produto é um vinho tinto seco de boa procedência."""
    name_low = (name or "").lower()
    
    # 1. Rejeita se tiver qualquer termo de vinho suave / doce / espumante
    if any(term in name_low for term in FORBIDDEN_TERMS):
        return False
        
    # 2. Rejeita se for claramente branco, rosé ou kit que contenha branco
    if "branco" in name_low or "rosé" in name_low or "rose" in name_low or "espumante" in name_low:
        return False

    # 3. Deve ter menção a tinto ou ser de uva tinta conhecida ou de vinícola conhecida
    has_tinto = "tinto" in name_low or "red" in name_low
    has_grape = any(grape in name_low for grape in GRAPE_PROFILES.keys())
    has_winery = any(winery[0] in name_low for winery in FAMOUS_WINERIES)
    
    if not (has_tinto or has_grape or has_winery):
        return False
        
    # Preço mínimo para tinto seco fino confiável (garrafa única não pode ser 10 reais)
    if price > 0 and price < 24.0 and "kit" not in name_low:
        return False
        
    return True

def analyze_wine_profile(name: str, price: float = 0.0, original_price: Optional[float] = None) -> Dict[str, Any]:
    """Extrai informações completas de Sommelier para o vinho."""
    name_low = (name or "").lower()
    
    # Identifica país e vinícola
    country = "Chile"
    flag = "🇨🇱"
    winery_name = "Produtor Selecionado"
    
    for key, win_name, c_name, c_flag in FAMOUS_WINERIES:
        if key in name_low:
            country = c_name
            flag = c_flag
            winery_name = win_name
            break
    else:
        if "argentin" in name_low or "mendoza" in name_low:
            country, flag = "Argentina", "🇦🇷"
        elif "portug" in name_low or "douro" in name_low or "alentej" in name_low:
            country, flag = "Portugal", "🇵🇹"
        elif "chilen" in name_low or "chile" in name_low:
            country, flag = "Chile", "🇨🇱"
        elif "italian" in name_low or "itália" in name_low or "italia" in name_low:
            country, flag = "Itália", "🇮🇹"
        elif "espanh" in name_low or "rioja" in name_low:
            country, flag = "Espanha", "🇪🇸"

    # Identifica uva principal
    grape_info = {
        "name": "Corte de Uvas Nobres (Blend)",
        "body": "Médio a Encorpado",
        "notes": "Frutas vermelhas e pretas maduras, equilíbrio e taninos agradáveis.",
        "pairing": "Carnes grelhadas, massas tradicionais, risotos e queijos curados."
    }
    
    for g_key, g_data in GRAPE_PROFILES.items():
        if g_key in name_low:
            grape_info = g_data
            break

    # Identifica se é Kit e calcula preço por garrafa
    is_kit = False
    bottles_count = 1
    kit_match = re.search(r'(?:kit|cx|caixa|pack)\s*(?:c\/|com)?\s*(\d+)', name_low)
    if kit_match:
        is_kit = True
        bottles_count = int(kit_match.group(1))
    elif " 6 garrafas" in name_low or " 6 und" in name_low or " 6u" in name_low or " 6 vinhos" in name_low:
        is_kit = True
        bottles_count = 6
    elif " 3 garrafas" in name_low or " 3 vinhos" in name_low:
        is_kit = True
        bottles_count = 3

    bottle_price = round(price / bottles_count, 2) if is_kit and bottles_count > 0 else price
    
    # Classificação por faixa de preço / categoria de qualidade
    if bottle_price <= 55.0:
        tier_badge = "⭐ Custo-Benefício Campeão"
        score = 4.4
        recommendation = "Perfeito para o consumo no dia a dia, almoços de família e jantares descontraídos."
    elif bottle_price <= 120.0:
        tier_badge = "🏅 Linha Reserva Especial"
        score = 4.7
        recommendation = "Estrutura notável com passagem por madeira. Excelente para acompanhar jantares especiais e churrascos nobres."
    else:
        tier_badge = "👑 Alta Gama / Ícone"
        score = 4.9
        recommendation = "Rótulo de grande prestígio, complexo e potente. Uma experiência sensorial para ocasiões marcantes."

    # Desconto
    discount_pct = 0.0
    if original_price and original_price > price:
        discount_pct = round(((original_price - price) / original_price) * 100, 1)

    return {
        "clean_name": (name.replace("(Amazon Prime)", "")
                            .replace("(Amazon)", "")
                            .replace("(Mercado Livre Full)", "")
                            .replace("(Mercado Livre)", "")
                            .replace("(Wine.com.br)", "")
                            .replace("(Wine)", "")
                            .replace("(Evino)", "")
                            .replace("(Grand Cru)", "")
                            .replace("(Mistral)", "")
                            .replace("(Savegnago Sertãozinho)", "")
                            .replace("(Savegnago Supermercados)", "")
                            .replace("(Savegnago)", "")
                            .replace("(Pão de Açúcar Delivery)", "")
                            .replace("(Pão de Açúcar)", "")
                            .strip()),
        "winery": winery_name,
        "country": country,
        "flag": flag,
        "grape": grape_info["name"],
        "body": grape_info["body"],
        "tasting_notes": grape_info["notes"],
        "pairing": grape_info["pairing"],
        "tier": tier_badge,
        "score": score,
        "sommelier_note": recommendation,
        "is_kit": is_kit,
        "bottles_count": bottles_count,
        "bottle_price": bottle_price,
        "discount_pct": discount_pct
    }

def get_store_badge_info(store: str) -> Dict[str, str]:
    """Retorna badge visual e detalhes de entrega de acordo com a loja/plataforma."""
    s_low = (store or "").lower()
    if "amazon" in s_low:
        return {
            "badge": "📦 Amazon Prime",
            "emoji": "📦",
            "delivery": "⚡ Envio Rápido Prime (garantido para esta semana)",
            "short_name": "Amazon Prime"
        }
    elif "mercado livre" in s_low or "full" in s_low:
        return {
            "badge": "⚡ Mercado Livre Full",
            "emoji": "⚡",
            "delivery": "🚀 Entrega Full Expressa (em 24h a 48h)",
            "short_name": "Mercado Livre Full"
        }
    elif "wine" in s_low:
        return {
            "badge": "🍇 Wine.com.br",
            "emoji": "🍇",
            "delivery": "📦 Clube Wine (Envio expresso e kits promocionais)",
            "short_name": "Wine.com.br"
        }
    elif "evino" in s_low:
        return {
            "badge": "🍷 Evino",
            "emoji": "🍷",
            "delivery": "📦 Evino Entrega Ágil (combos e importações exclusivas)",
            "short_name": "Evino"
        }
    elif "grand cru" in s_low:
        return {
            "badge": "👑 Grand Cru",
            "emoji": "👑",
            "delivery": "🍾 Adega Boutique Grand Cru (vinhos de alta gama)",
            "short_name": "Grand Cru"
        }
    elif "mistral" in s_low:
        return {
            "badge": "🏛️ Mistral Importadora",
            "emoji": "🏛️",
            "delivery": "🍾 Importação Oficial Mistral (safras e vinícolas ícones)",
            "short_name": "Mistral"
        }
    elif "savegnago" in s_low:
        return {
            "badge": "🏪 Savegnago Adega",
            "emoji": "🏪",
            "delivery": "🛵 Pronta Entrega Local em Sertãozinho/SP (mesmo dia)",
            "short_name": "Savegnago Sertãozinho"
        }
    elif "pão de açúcar" in s_low or "pao de acucar" in s_low:
        return {
            "badge": "🛒 Pão de Açúcar",
            "emoji": "🛒",
            "delivery": "🛵 Delivery Especializado Pão de Açúcar",
            "short_name": "Pão de Açúcar"
        }
    else:
        return {
            "badge": f"🏬 {store}",
            "emoji": "🏬",
            "delivery": "📦 Entrega rápida nacional",
            "short_name": store
        }

def get_sommelier_curated_catalog() -> List[Dict[str, Any]]:
    """
    Catálogo permanente e omni-channel de vinhos tintos secos consagrados:
    Amazon Prime, Mercado Livre Full, Wine.com.br, Evino, Grand Cru, Mistral, Pão de Açúcar e Savegnago.
    Todos com links diretos de compra.
    """
    return [
        # --- AMAZON BRASIL (PRIME) ---
        {
            "name": "Concha y Toro Casillero Del Diablo Cabernet Sauvignon 750ml (Amazon Prime)",
            "category": "vinho",
            "store": "Amazon Brasil",
            "price": 47.40,
            "original_price": 59.90,
            "link": "https://www.amazon.com.br/Vinho-Casillero-Diablo-Cabernet-Sauvignon/dp/B07LBK41YG"
        },
        {
            "name": "Concha y Toro Casillero Del Diablo Carmenere 750ml (Amazon Prime)",
            "category": "vinho",
            "store": "Amazon Brasil",
            "price": 39.97,
            "original_price": 54.90,
            "link": "https://www.amazon.com.br/Vinho-Casillero-Diablo-Carmenere-750ml/dp/B01IT28BY2"
        },
        {
            "name": "Vinho Pé Tinto Esporão Alentejo 750ml (Amazon Prime)",
            "category": "vinho",
            "store": "Amazon Brasil",
            "price": 39.90,
            "original_price": 49.90,
            "link": "https://www.amazon.com.br/Vinho-Espor%C3%A3o-Tinto-750ml-2018/dp/B00DTRY07A"
        },
        {
            "name": "Vinho Argentino Cordero Con Piel de Lobo 750ml (Amazon Prime)",
            "category": "vinho",
            "store": "Amazon Brasil",
            "price": 44.93,
            "original_price": 64.90,
            "link": "https://www.amazon.com.br/Vinho-Argentino-Cordero-Cabernet-Sauvignon/dp/B092R993VQ"
        },
        {
            "name": "Vinho Tinto Alandra Esporão 750ml (Amazon Prime)",
            "category": "vinho",
            "store": "Amazon Brasil",
            "price": 32.50,
            "original_price": 46.00,
            "link": "https://www.amazon.com.br/Espor%C3%A3o-Vinho-Tinto-Alandra/dp/B0CHWYSRTD"
        },
        {
            "name": "Vinho Fino Tinto Português Intimista Alentejo 750ml (Amazon Prime)",
            "category": "vinho",
            "store": "Amazon Brasil",
            "price": 33.52,
            "original_price": 49.90,
            "link": "https://www.amazon.com.br/Vinho-Tinto-Portugu%C3%AAs-Intimista-Alentejo/dp/B0D4NH9363"
        },
        {
            "name": "Vinho Tinto Chileno Escudo Rojo Gran Reserva Origine Cabernet Sauvignon 750ml (Amazon Prime)",
            "category": "vinho",
            "store": "Amazon Brasil",
            "price": 188.10,
            "original_price": 240.00,
            "link": "https://www.amazon.com.br/Chileno-Reserva-Origine-Cabernet-Sauvignon/dp/B09SHY372L"
        },
        {
            "name": "DV Catena Cabernet Malbec 6 Garrafas (Amazon Prime)",
            "category": "vinho",
            "store": "Amazon Brasil",
            "price": 484.99,
            "original_price": 599.00,
            "link": "https://www.amazon.com.br/DV-Catena-Cabernet-Malbec-Garrafas/dp/B0HM7F3WLF"
        },
        {
            "name": "Concha y Toro Reservado Cabernet Sauvignon 750ml (Amazon Prime)",
            "category": "vinho",
            "store": "Amazon Brasil",
            "price": 29.79,
            "original_price": 39.90,
            "link": "https://www.amazon.com.br/Concha-Toro-Reservado-Cabernet-Sauvignon/dp/B07XLMJHRN"
        },
        {
            "name": "Montes Limited Selection Pinot Noir Vinho Tinto Chileno 750ml (Amazon Prime)",
            "category": "vinho",
            "store": "Amazon Brasil",
            "price": 154.40,
            "original_price": 199.00,
            "link": "https://www.amazon.com.br/Montes-Limited-Selection-Pinot-chileno/dp/B001M2DUIY"
        },
        {
            "name": "Tormaresca Neprica Vinho Tinto Seco Primitivo Puglia IGT 750ml (Amazon Prime)",
            "category": "vinho",
            "store": "Amazon Brasil",
            "price": 182.10,
            "original_price": 230.00,
            "link": "https://www.amazon.com.br/Tormaresca-Neprica-Primitivo-encorpado-frutado/dp/B00O0SCESO"
        },
        {
            "name": "Vinho Faustino Crianza Tinto Seco DOCa Rioja 750ml (Amazon Prime)",
            "category": "vinho",
            "store": "Amazon Brasil",
            "price": 179.55,
            "original_price": 235.00,
            "link": "https://www.amazon.com.br/Vinho-Faustino-Crianza-Tinto-750ml/dp/B009XPFHV0"
        },

        # --- MERCADO LIVRE FULL (ENTREGA 24H) ---
        {
            "name": "Kit 6 Garrafas Vinho Argentino Malbec Finca Las Moras 750ml (Mercado Livre Full)",
            "category": "vinho",
            "store": "Mercado Livre Full",
            "price": 189.90,
            "original_price": 239.40,
            "link": "https://lista.mercadolivre.com.br/kit-vinho-argentino-malbec_OrderId_PRICE*ASC_Shipping_fulfillment"
        },
        {
            "name": "Kit 4 Vinhos Tintos Chilenos Reservado Concha y Toro Cabernet Sauvignon 750ml (Mercado Livre Full)",
            "category": "vinho",
            "store": "Mercado Livre Full",
            "price": 124.90,
            "original_price": 159.60,
            "link": "https://lista.mercadolivre.com.br/kit-vinho-tinto-reservado_OrderId_PRICE*ASC_Shipping_fulfillment"
        },
        {
            "name": "Vinho Chileno Casillero del Diablo Cabernet Sauvignon 750ml (Mercado Livre Full)",
            "category": "vinho",
            "store": "Mercado Livre Full",
            "price": 44.90,
            "original_price": 59.90,
            "link": "https://lista.mercadolivre.com.br/casillero-del-diablo-cabernet_OrderId_PRICE*ASC_Shipping_fulfillment"
        },
        {
            "name": "Vinho Argentino DV Catena Cabernet Malbec Mendoza 750ml (Mercado Livre Full)",
            "category": "vinho",
            "store": "Mercado Livre Full",
            "price": 145.00,
            "original_price": 189.00,
            "link": "https://lista.mercadolivre.com.br/dv-catena-cabernet-malbec_OrderId_PRICE*ASC_Shipping_fulfillment"
        },
        {
            "name": "Vinho Tinto Português Bons Ventos Lisboa 750ml (Mercado Livre Full)",
            "category": "vinho",
            "store": "Mercado Livre Full",
            "price": 38.90,
            "original_price": 49.90,
            "link": "https://lista.mercadolivre.com.br/vinho-bons-ventos-tinto_OrderId_PRICE*ASC_Shipping_fulfillment"
        },

        # --- WINE.COM.BR (CLUBE & KITS) ---
        {
            "name": "Kit 3 Vinhos Tintos Portugueses Bons Ventos Tinto Seco 750ml (Wine.com.br)",
            "category": "vinho",
            "store": "Wine.com.br",
            "price": 109.90,
            "original_price": 179.70,
            "link": "https://www.wine.com.br/vinhos/kit-3-vinhos-bons-ventos/p24823"
        },
        {
            "name": "Vinho Tinto Chileno Toro de Piedra Gran Reserva Cabernet Sauvignon 750ml (Wine.com.br)",
            "category": "vinho",
            "store": "Wine.com.br",
            "price": 89.90,
            "original_price": 129.90,
            "link": "https://www.wine.com.br/vinhos/toro-de-piedra-gran-reserva-cabernet/p18920"
        },
        {
            "name": "Vinho Tinto Espanhol Esteban Martín D.O.P. Cariñena Garnacha Syrah 750ml (Wine.com.br)",
            "category": "vinho",
            "store": "Wine.com.br",
            "price": 42.90,
            "original_price": 69.90,
            "link": "https://www.wine.com.br/vinhos/esteban-martin-dop-carinena/p27810"
        },
        {
            "name": "Vinho Tinto Argentino Partridge Reserva Malbec 750ml Las Perdices (Wine.com.br)",
            "category": "vinho",
            "store": "Wine.com.br",
            "price": 54.90,
            "original_price": 79.90,
            "link": "https://www.wine.com.br/vinhos/partridge-reserva-malbec/p23109"
        },

        # --- EVINO (COMBOS & EXCLUSIVIDADES) ---
        {
            "name": "Kit 6 Vinhos Chilenos Gran Reserva Cabernet Sauvignon 750ml (Evino)",
            "category": "vinho",
            "store": "Evino",
            "price": 219.00,
            "original_price": 389.00,
            "link": "https://www.evino.com.br/produto/kit-6-vinhos-gran-reserva-cabernet"
        },
        {
            "name": "Vinho Tinto Italiano Primitivo di Manduria Epicuro DOP 750ml (Evino)",
            "category": "vinho",
            "store": "Evino",
            "price": 84.90,
            "original_price": 129.90,
            "link": "https://www.evino.com.br/produto/epicuro-primitivo-di-manduria-dop"
        },
        {
            "name": "Vinho Tinto Espanhol Portada Winemaker's Selection 750ml (Evino)",
            "category": "vinho",
            "store": "Evino",
            "price": 39.90,
            "original_price": 59.90,
            "link": "https://www.evino.com.br/produto/portada-winemakers-selection-tinto"
        },

        # --- GRAND CRU & MISTRAL (ALTA GAMA & ÍCONES) ---
        {
            "name": "Vinho Argentino Cobos Felino Malbec 750ml Paul Hobbs (Grand Cru)",
            "category": "vinho",
            "store": "Grand Cru",
            "price": 139.90,
            "original_price": 179.90,
            "link": "https://www.grandcru.com.br/vinho-argentino-cobos-felino-malbec/p"
        },
        {
            "name": "Vinho Italiano San Marzano Il Pumo Primitivo Salento IGP 750ml (Grand Cru)",
            "category": "vinho",
            "store": "Grand Cru",
            "price": 94.90,
            "original_price": 129.90,
            "link": "https://www.grandcru.com.br/vinho-italiano-san-marzano-il-pumo-primitivo/p"
        },
        {
            "name": "Vinho Chileno Montes Alpha Cabernet Sauvignon Valle de Colchagua 750ml (Mistral)",
            "category": "vinho",
            "store": "Mistral",
            "price": 179.00,
            "original_price": 220.00,
            "link": "https://www.mistral.com.br/vinho/montes-alpha-cabernet-sauvignon-montes"
        },
        {
            "name": "Vinho Argentino Catena Malbec Mendoza 750ml Bodega Catena Zapata (Mistral)",
            "category": "vinho",
            "store": "Mistral",
            "price": 169.00,
            "original_price": 209.00,
            "link": "https://www.mistral.com.br/vinho/catena-malbec-catena-zapata"
        },

        # --- PÃO DE AÇÚCAR DELIVERY ---
        {
            "name": "Vinho Tinto Português EA Cartuxa Alentejo 750ml (Pão de Açúcar Delivery)",
            "category": "vinho",
            "store": "Pão de Açúcar Delivery",
            "price": 79.90,
            "original_price": 99.90,
            "link": "https://www.paodeacucar.com/produto/140228/vinho-portugues-tinto-ea-cartuxa-garrafa-750ml"
        },

        # --- SAVEGNAGO ADEGA (SERTÃOZINHO / ENTREGA NO MESMO DIA) ---
        {
            "name": "Vinho Chileno Casillero del Diablo Cabernet Sauvignon 750ml (Savegnago Sertãozinho)",
            "category": "vinho",
            "store": "Savegnago Supermercados",
            "price": 46.90,
            "original_price": 59.90,
            "link": "https://www.savegnago.com.br/busca?ft=casillero+del+diablo"
        },
        {
            "name": "Vinho Tinto Português Pé Tinto Esporão 750ml (Savegnago Sertãozinho)",
            "category": "vinho",
            "store": "Savegnago Supermercados",
            "price": 38.90,
            "original_price": 47.90,
            "link": "https://www.savegnago.com.br/busca?ft=pe+tinto"
        },
        {
            "name": "Vinho Argentino Trapiche Malbec 750ml (Savegnago Sertãozinho)",
            "category": "vinho",
            "store": "Savegnago Supermercados",
            "price": 44.90,
            "original_price": 54.90,
            "link": "https://www.savegnago.com.br/busca?ft=vinho+trapiche"
        },
        {
            "name": "Vinho Chileno Santa Helena Reservado Cabernet Sauvignon 750ml (Savegnago Sertãozinho)",
            "category": "vinho",
            "store": "Savegnago Supermercados",
            "price": 29.90,
            "original_price": 37.90,
            "link": "https://www.savegnago.com.br/busca?ft=vinho+santa+helena"
        }
    ]

def get_best_sommelier_wines(store_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Combina os vinhos do banco SQLite e a curadoria permanente do Sommelier.
    Suporta filtro por loja (ex: 'amazon', 'mercadolivre', 'wine', 'evino', 'grand cru', 'mistral', 'savegnago')
    ou retorna o ranking geral das melhores ofertas de todos os sites combinados.
    """
    from database import get_connection
    wines = []
    seen_names = set()
    curated = get_sommelier_curated_catalog()
    
    # Mapeamento de links diretos verificados
    curated_map = {item["name"][:20].lower(): item["link"] for item in curated}

    with get_connection() as conn:
        cursor = conn.cursor()
        
        query = """
            SELECT p.id, p.name, p.store, p.link, ph.price, ph.original_price, ph.discount_pct, ph.recorded_at
            FROM products p
            JOIN price_history ph ON ph.product_id = p.id
            WHERE p.category = 'vinho'
              AND ph.id = (
                  SELECT id FROM price_history 
                  WHERE product_id = p.id 
                  ORDER BY recorded_at DESC, id DESC LIMIT 1
              )
        """
        params = []
        if store_filter:
            sf_low = store_filter.lower()
            if sf_low in ["amazon", "prime"]:
                query += " AND p.store LIKE '%Amazon%'"
            elif sf_low in ["mercadolivre", "ml", "full"]:
                query += " AND (p.store LIKE '%Mercado Livre%' OR p.store LIKE '%Full%')"
            elif sf_low in ["wine", "evino", "clubes"]:
                query += " AND (p.store LIKE '%Wine%' OR p.store LIKE '%Evino%')"
            elif sf_low in ["grand cru", "mistral", "boutique", "alta gama"]:
                query += " AND (p.store LIKE '%Grand Cru%' OR p.store LIKE '%Mistral%')"
            elif sf_low in ["savegnago", "local", "sertãozinho", "sertaozinho"]:
                query += " AND p.store LIKE '%Savegnago%'"
            else:
                query += " AND p.store LIKE ?"
                params.append(f"%{store_filter}%")
                
        query += " ORDER BY ph.price ASC"
        cursor.execute(query, params)
        rows = [dict(r) for r in cursor.fetchall()]

        for r in rows:
            name = r["name"]
            price = r["price"]
            link = r.get("link", "")
            
            # Validação de integridade de links da Amazon
            if "amazon" in r.get("store", "").lower():
                if not link or link in ["https://www.amazon.com.br", "https://www.amazon.com.br/"] or "/dp/" not in link:
                    matched = None
                    n_low = name[:20].lower()
                    for ck, cl in curated_map.items():
                        if ck in n_low or n_low in ck:
                            matched = cl
                            break
                    if matched:
                        link = matched
                    else:
                        continue
                        
            if is_good_dry_red(name, price):
                prof = analyze_wine_profile(name, price, r.get("original_price"))
                clean_key = (prof["clean_name"][:25] + "_" + r.get("store", "")[:10]).lower()
                if clean_key not in seen_names:
                    seen_names.add(clean_key)
                    wines.append({
                        "id": r["id"],
                        "name": r["name"],
                        "store": r["store"],
                        "link": link,
                        "price": price,
                        "original_price": r.get("original_price"),
                        "discount_pct": prof["discount_pct"],
                        "profile": prof
                    })

    # Adiciona a curadoria permanente
    for item in curated:
        # Se houver filtro de loja, valida se o item pertence à loja filtrada
        if store_filter:
            sf_low = store_filter.lower()
            st_low = item["store"].lower()
            if sf_low in ["amazon", "prime"] and "amazon" not in st_low:
                continue
            elif sf_low in ["mercadolivre", "ml", "full"] and "mercado livre" not in st_low and "full" not in st_low:
                continue
            elif sf_low in ["wine", "evino", "clubes"] and "wine" not in st_low and "evino" not in st_low:
                continue
            elif sf_low in ["grand cru", "mistral", "boutique", "alta gama"] and "grand cru" not in st_low and "mistral" not in st_low:
                continue
            elif sf_low in ["savegnago", "local", "sertãozinho"] and "savegnago" not in st_low:
                continue
                
        name = item["name"]
        price = item["price"]
        prof = analyze_wine_profile(name, price, item.get("original_price"))
        clean_key = (prof["clean_name"][:25] + "_" + item["store"][:10]).lower()
        if clean_key not in seen_names:
            seen_names.add(clean_key)
            wines.append({
                "id": None,
                "name": item["name"],
                "store": item["store"],
                "link": item["link"],
                "price": price,
                "original_price": item.get("original_price"),
                "discount_pct": prof["discount_pct"],
                "profile": prof
            })

    # Ordena: pontuação de sommelier DESC, depois preço ASC
    wines.sort(key=lambda x: (-x["profile"]["score"], x["profile"]["bottle_price"]))
    return wines

def get_best_amazon_red_wines() -> List[Dict[str, Any]]:
    """Compatibilidade retroativa: retorna exclusivamente os vinhos da Amazon."""
    return get_best_sommelier_wines(store_filter="amazon")

def format_wine_sommelier_card(wine: Dict[str, Any]) -> str:
    """Gera um card detalhado e elegante de recomendação do Sommelier para o Telegram com badge de loja."""
    prof = wine.get("profile") or analyze_wine_profile(wine["name"], wine["price"], wine.get("original_price"))
    badge_info = get_store_badge_info(wine.get("store", "Amazon Brasil"))
    
    orig_str = f"~R$ {wine['original_price']:.2f}~ " if wine.get("original_price") and wine["original_price"] > wine["price"] else ""
    disc_str = f" *(-{prof['discount_pct']:.0f}%)*" if prof.get("discount_pct", 0) > 0 else ""
    
    pack_note = ""
    if prof.get("is_kit"):
        pack_note = f"\n📦 *Caixa com {prof['bottles_count']} garrafas* (sai a *R$ {prof['bottle_price']:.2f}* por garrafa!)"
        
    lines = [
        f"🍷 *SOMMELIER ESPECIALISTA: ACHADO DE VINHO TINTO SECO* {badge_info['emoji']}\n",
        f"{prof['flag']} *{prof['clean_name']}*",
        f"🏰 *Vinícola:* {prof['winery']} • {prof['country']} {prof['flag']}",
        f"🍇 *Uva:* {prof['grape']}",
        f"⚖️ *Corpo & Estrutura:* {prof['body']}\n",
        "📝 *Avaliação do Sommelier:*",
        f"• *Perfil Sensorial:* {prof['tasting_notes']}",
        f"• *Harmonização Perfeita:* {prof['pairing']}",
        f"• *Selo:* {prof['tier']} (Nota: ⭐ {prof['score']:.1f}/5.0)",
        f"• _{prof['sommelier_note']}_\n",
        f"💰 *Preço:* {orig_str}*R$ {wine['price']:.2f}*{disc_str}{pack_note}",
        f"🏪 *Onde Comprar:* {badge_info['badge']}",
        f"🚚 *Entrega:* {badge_info['delivery']}\n",
        f"👉 [CLIQUE AQUI PARA VER E COMPRAR NO {badge_info['short_name'].upper()}]({wine['link']})"
    ]
    return "\n".join(lines)

def format_wine_sommelier_catalog(wines: List[Dict[str, Any]], limit: int = 6, title: Optional[str] = None) -> str:
    """Gera uma lista formatada de recomendações de vinhos tintos secos para comandos do bot."""
    header = title or "🍷 *ADEGA DO SOMMELIER: MELHORES VINHOS TINTOS SECOS* 🍇"
    lines = [
        f"{header}\n",
        "Seleção rigorosa de rótulos consagrados em todas as plataformas com alta pontuação:\n"
    ]
    for idx, w in enumerate(wines[:limit], start=1):
        prof = w.get("profile") or analyze_wine_profile(w["name"], w["price"], w.get("original_price"))
        badge_info = get_store_badge_info(w.get("store", ""))
        disc_str = f" (-{prof['discount_pct']:.0f}%)" if prof.get("discount_pct", 0) > 0 else ""
        orig_str = f"~R$ {w['original_price']:.2f}~ " if w.get("original_price") and w["original_price"] > w["price"] else ""
        pack_str = f" [{prof['bottles_count']}x R$ {prof['bottle_price']:.2f}/gf]" if prof.get("is_kit") else ""
        
        lines.append(
            f"*{idx}. {prof['flag']} {prof['clean_name']}*\n"
            f"  🍇 {prof['grape']} • {prof['body']}\n"
            f"  💰 {orig_str}*R$ {w['price']:.2f}*{disc_str}{pack_str} ({prof['tier']})\n"
            f"  🏪 {badge_info['badge']} • {badge_info['delivery'].split('(')[0].strip()}\n"
            f"  🍽️ _Harmoniza: {prof['pairing'][:55]}..._\n"
            f"  🔗 [Comprar na {badge_info['short_name']}]({w['link']})\n"
        )
        
    lines.append("⚡ _Atualizado de hora em hora. Para ver mais detalhes, clique no link da loja desejada._")
    return "\n".join(lines)

STATE_FILE = "services/wine_sommelier_state.json"

def get_next_hourly_sommelier_wine(store_filter: Optional[str] = None, force_next: bool = True) -> Optional[Dict[str, Any]]:
    """
    Seleciona a melhor oferta de vinho tinto seco para a notificação horária.
    Rotaciona os melhores rótulos entre diferentes lojas e prioriza quedas de preço e descontos.
    """
    import json
    import os
    
    all_wines = get_best_sommelier_wines(store_filter=store_filter)
    if not all_wines:
        return None
        
    sent_keys = []
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                sent_keys = data.get("sent_keys", [])
        except Exception:
            sent_keys = []
            
    # 1. Procura primeiro vinho com desconto ativo (>= 15%) ainda não enviado
    discounted_unseen = [
        w for w in all_wines 
        if w["profile"]["discount_pct"] >= 15 and (w["profile"]["clean_name"][:20] + "_" + w["store"][:8]).lower() not in sent_keys
    ]
    if discounted_unseen:
        chosen = discounted_unseen[0]
    else:
        # 2. Se todos já foram enviados, reseta o histórico para recomeçar o ciclo
        remaining = [w for w in all_wines if (w["profile"]["clean_name"][:20] + "_" + w["store"][:8]).lower() not in sent_keys]
        if not remaining:
            sent_keys = []
            remaining = all_wines
        chosen = remaining[0]
        
    # Registra como enviado
    chosen_key = (chosen["profile"]["clean_name"][:20] + "_" + chosen["store"][:8]).lower()
    if chosen_key not in sent_keys:
        sent_keys.append(chosen_key)
        
    try:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump({"sent_keys": sent_keys}, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
        
    return chosen
