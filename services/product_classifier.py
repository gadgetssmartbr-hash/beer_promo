"""
Classificador de Intenção e Categorias de Produtos.
Diferencia Bebidas (cervejas, vinhos, destilados) de Itens de Supermercado Geral / Cesta Básica da Família
(ovos, leite, carnes, limpeza, mercearia, higiene).
"""
import re
import urllib.parse
from typing import Dict, Any, List

BEVERAGE_KEYWORDS = {
    "cerveja", "cervejas", "chopp", "chope", "vinho", "vinhos", "espumante", "espumantes",
    "whisky", "whiskey", "vodka", "vodca", "gin", "gim", "cachaça", "rum", "tequila",
    "licor", "campari", "aperol", "heineken", "spaten", "stella", "corona", "amstel",
    "brahma", "skol", "bohemia", "budweiser", "original", "eisenbahn", "becks", "colorado",
    "baden baden", "roleta russa", "antarctica", "petra", "itaipava", "devassa",
    "casillero", "concha y toro", "salton", "chandon", "miolo", "periquita", "malbec",
    "cabernet", "carmenere", "merlot", "sauvignon", "tinto", "rose", "branco", "prosecco",
    "energetico", "monster", "red bull", "refrigerante", "coca cola", "guarana"
}

CLEANING_KEYWORDS = {
    "sabao", "sabão", "omo", "ariel", "brilhante", "ypê", "ype", "detergente",
    "amaciante", "downy", "comfort", "papel higienico", "papel higiênico", "neve",
    "desinfetante", "pinho", "veja", "agua sanitaria", "água sanitária", "qboa",
    "cloro", "multiuso", "esponja", "bombril", "lustra moveis", "saco de lixo"
}

MEAT_KEYWORDS = {
    "carne", "carnes", "picanha", "alcatra", "contrafile", "contrafilé", "patinho",
    "acem", "acém", "maminha", "fraldinha", "costela", "linguica", "linguiça",
    "frango", "peito de frango", "coxa", "sobrecoxa", "filé de peito", "carne moida",
    "carne moída", "cupim", "bife", "churrasco", "bacon", "pernil", "lombo"
}

BASIC_GROCERY_KEYWORDS = {
    "ovo", "ovos", "leite", "arroz", "feijao", "feijão", "oleo", "óleo",
    "cafe", "café", "acucar", "açúcar", "sal", "farinha", "macarrao", "macarrão",
    "molho de tomate", "manteiga", "margarina", "queijo", "mussarela", "presunto",
    "pao", "pão", "iogurte", "requeijao", "requeijão", "azeite", "extrato de tomate",
    "biscoito", "bolacha", "achocolatado", "toddy", "nescau", "milho", "ervilha"
}

HYGIENE_KEYWORDS = {
    "sabonete", "shampoo", "condicionador", "creme dental", "pasta de dente",
    "colgate", "desodorante", "rexona", "dove", "fio dental", "escova de dente",
    "absorvente", "gilete", "lamina de barbear", "fralda", "lenco umedecido"
}

def classify_product_query(query: str) -> Dict[str, Any]:
    """
    Analisa a consulta e retorna o tipo de produto, canal ideal de busca e se é local ou online.
    """
    clean = query.lower().strip()
    words = set(re.findall(r'\b\w+\b', clean))
    
    # 1. Verifica Bebidas
    is_beverage = any(kw in clean or kw in words for kw in BEVERAGE_KEYWORDS)
    if is_beverage:
        return {
            "type": "BEBIDA",
            "category_name": "Bebidas (Cervejas, Vinhos & Destilados)",
            "is_local_only": False,
            "has_ze_delivery": True,
            "has_marketplaces": True,
            "icon": "🍻"
        }
        
    # 2. Verifica Carnes / Açougue
    is_meat = any(kw in clean or kw in words for kw in MEAT_KEYWORDS)
    if is_meat:
        return {
            "type": "SUPERMERCADO_ACOUGUE",
            "category_name": "Açougue & Carnes",
            "is_local_only": True,
            "has_ze_delivery": False,
            "has_marketplaces": False,
            "icon": "🥩"
        }

    # 3. Verifica Limpeza
    is_cleaning = any(kw in clean or kw in words for kw in CLEANING_KEYWORDS)
    if is_cleaning:
        return {
            "type": "SUPERMERCADO_LIMPEZA",
            "category_name": "Limpeza & Lavanderia",
            "is_local_only": False,  # Pode comprar no Savegnago/Copercana ou Amazon/ML
            "has_ze_delivery": False,
            "has_marketplaces": True,
            "icon": "🧼"
        }

    # 4. Verifica Cesta Básica & Alimentos
    is_grocery = any(kw in clean or kw in words for kw in BASIC_GROCERY_KEYWORDS)
    if is_grocery:
        return {
            "type": "SUPERMERCADO_ALIMENTOS",
            "category_name": "Cesta Básica & Mercearia",
            "is_local_only": True,
            "has_ze_delivery": False,
            "has_marketplaces": False,
            "icon": "🥚"
        }

    # 5. Verifica Higiene
    is_hygiene = any(kw in clean or kw in words for kw in HYGIENE_KEYWORDS)
    if is_hygiene:
        return {
            "type": "SUPERMERCADO_HIGIENE",
            "category_name": "Higiene & Cuidados Pessoais",
            "is_local_only": False,
            "has_ze_delivery": False,
            "has_marketplaces": True,
            "icon": "🧴"
        }

    # Padrão: Supermercado Local Geral
    return {
        "type": "SUPERMERCADO_GERAL",
        "category_name": "Supermercado & Família",
        "is_local_only": True,
        "has_ze_delivery": False,
        "has_marketplaces": False,
        "icon": "🛒"
    }

def get_store_links_for_product(query: str) -> List[Dict[str, Any]]:
    """
    Gera links de compra contextualmente corretos para o produto pesquisado.
    Para itens de supermercado (ovos, leite, carnes, arroz), retorna Savegnago, Copercana e Paulistão.
    Apenas para bebidas inclui Zé Delivery.
    """
    classification = classify_product_query(query)
    encoded = urllib.parse.quote_plus(query)
    links = []

    # 1. Supermercados Locais de Sertãozinho (SEMPRE presentes para tudo)
    links.append({
        "store": "🛒 Savegnago Supermercados",
        "title": f"Buscar '{query}' no Savegnago Online Sertãozinho",
        "price": "Preço local / Encarte",
        "free_shipping": "🛵 Delivery Local em Sertãozinho",
        "is_full": "📍 Savegnago",
        "link": f"https://www.savegnago.com.br/busca?ft={encoded}"
    })

    links.append({
        "store": "🏪 Supermercados Copercana",
        "title": f"Consultar '{query}' na Copercana Sertãozinho",
        "price": "Clube Copermais",
        "free_shipping": "🛵 Lojas Sertãozinho",
        "is_full": "📍 Copercana",
        "link": "https://www.supermercadoscopercana.com.br"
    })

    links.append({
        "store": "🏬 Paulistão Atacadista",
        "title": f"Consultar '{query}' no Paulistão Atacadista",
        "price": "Preço de Atacado & Volume",
        "free_shipping": "📍 Sertãozinho / Loja Física",
        "is_full": "⚡ Preço Atacado",
        "link": "https://www.paulistaoatacadista.com.br/jornal-de-ofertas/sertaozinho"
    })

    # 2. Se for BEBIDA, adiciona Zé Delivery e Mercado Livre
    if classification["type"] == "BEBIDA":
        links.append({
            "store": "⚡ Zé Delivery (Sertãozinho)",
            "title": f"Pedir '{query}' gelada no Zé Delivery",
            "price": "Preço de distribuidora",
            "free_shipping": "⏱️ Entrega em ~35 min",
            "is_full": "❄️ Gelada",
            "link": f"https://www.ze.delivery/produtos?q={encoded}"
        })
        links.append({
            "store": "📦 Mercado Livre Full",
            "title": f"Comprar '{query}' no Mercado Livre",
            "price": "Kits e Fardos",
            "free_shipping": "🚚 Frete Rápido Full",
            "is_full": "⚡ Full",
            "link": f"https://lista.mercadolivre.com.br/{encoded}_OrderId_PRICE*ASC_CustId_0_ItemType_N_Installments_NO*INTEREST_Shipping_fulfillment"
        })

    # 3. Se for LIMPEZA ou HIGIENE, adiciona Amazon Prime e Mercado Livre
    elif classification["type"] in ["SUPERMERCADO_LIMPEZA", "SUPERMERCADO_HIGIENE"]:
        links.append({
            "store": "📦 Amazon Brasil (Prime)",
            "title": f"Comprar '{query}' com Frete Grátis na Amazon",
            "price": "Preço Promocional Prime",
            "free_shipping": "📦 Frete Grátis Prime",
            "is_full": "⭐ Amazon",
            "link": f"https://www.amazon.com.br/s?k={encoded}"
        })
        links.append({
            "store": "📦 Mercado Livre Full",
            "title": f"Comprar '{query}' no Mercado Livre Full",
            "price": "Embalagens Econômicas",
            "free_shipping": "⚡ Entrega Rápida",
            "is_full": "⚡ Full",
            "link": f"https://lista.mercadolivre.com.br/{encoded}_OrderId_PRICE*ASC_CustId_0_ItemType_N_Installments_NO*INTEREST_Shipping_fulfillment"
        })

    return links
