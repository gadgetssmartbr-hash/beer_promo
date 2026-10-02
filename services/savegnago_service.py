"""
Serviço de ofertas dos Supermercados Savegnago e Copercana para Sertãozinho/SP.
"""
from typing import List, Dict, Any

def get_savegnago_info() -> Dict[str, Any]:
    return {
        "name": "Supermercados Savegnago (Sertãozinho)",
        "website": "https://www.savegnago.com.br",
        "tabloide_url": "https://www.savegnago.com.br/encartes",
        "delivery": "Delivery próprio via App/Site ou iFood",
        "benefits": "Descontos no Cartão Savegnago & Clube Nosso Valor",
        "highlight_categories": [
            "🍺 Cervejas: Heineken, Spaten, Stella Artois, Corona, Eisenbahn",
            "🍷 Vinhos: Tintos Nacionais, Importados (Chile, Argentina, Portugal), Espumantes Salton/Chandon"
        ]
    }

def get_copercana_info() -> Dict[str, Any]:
    return {
        "name": "Supermercados Copercana (Sertãozinho)",
        "website": "https://www.supermercadoscopercana.com.br",
        "app_name": "Clube Copermais",
        "benefits": "Preços diferenciados para cadastrados no Copermais",
        "highlight_categories": [
            "🍺 Cervejas artesanais e especiais da região",
            "🍷 Adega selecionada de vinhos nacionais e importados"
        ]
    }

def get_paulistao_info() -> Dict[str, Any]:
    return {
        "name": "Paulistão Atacadista (Sertãozinho)",
        "website": "https://www.paulistao.com.br",
        "benefits": "Preços de atacado em fardos, caixas e Clube de Vantagens",
        "highlight_categories": [
            "🍺 Cervejas em packs e fardos promocionais",
            "🥩 Carnes em peças e cortes para churrasco",
            "🧼 Produtos de limpeza em embalagens econômicas"
        ]
    }

def get_local_supermarkets() -> List[Dict[str, Any]]:
    return [
        get_savegnago_info(),
        get_copercana_info(),
        get_paulistao_info(),
        {
            "name": "Tonin Superatacado & Gricki (Sertãozinho/Região)",
            "website": "https://tonin.com.br",
            "delivery": "Retirada em loja / Compra em volume",
            "benefits": "Desconto progressivo em fardos e caixas fechadas"
        }
    ]
