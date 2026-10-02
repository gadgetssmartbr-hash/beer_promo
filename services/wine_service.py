"""
Serviço de busca de ofertas em lojas especializadas em vinhos (Wine, Evino, Sonoma, Divvino).
"""
from typing import List, Dict, Any

def get_wine_clubs_promos() -> List[Dict[str, Any]]:
    return [
        {
            "store": "🍷 Wine.com.br",
            "title": "Kits Promocionais de Vinhos Importados (Chile/Argentina/Portugal)",
            "deal_type": "Compre 3 com até 40% OFF / Frete Grátis Clube Wine",
            "url": "https://www.wine.com.br/vinhos/ofertas",
            "tips": "Utilize cupons de primeira compra (geralmente R$ 50 OFF em R$ 150+)."
        },
        {
            "store": "🍇 Evino",
            "title": "Combos 'Leve Mais por Menos' & Vinhos Selecionados",
            "deal_type": "Descontos de até 50% em garrafas individuais e kits",
            "url": "https://www.evino.com.br/promocoes",
            "tips": "Frete para Sertãozinho/SP com entrega rastreada e opções expressas."
        },
        {
            "store": "🍾 Divvino & Sonoma",
            "title": "Seleção de Rótulos Premium e Espumantes",
            "deal_type": "Cashback e descontos no PIX",
            "url": "https://www.divvino.com.br",
            "tips": "Excelente para vinhos finos de guarda e presentes."
        }
    ]
