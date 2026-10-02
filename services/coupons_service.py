"""
Serviço de cupons e vantagens em apps de entrega e marketplaces para Sertãozinho.
"""
from typing import List, Dict, Any

def get_active_coupons_and_tips() -> List[Dict[str, Any]]:
    return [
        {
            "service": "⚡ Zé Delivery (Sertãozinho)",
            "coupons": [
                "CUPOM NOVO: 'BEMVINDO' / 'ZENOVO' (R$ 10 a R$ 15 OFF na 1ª compra)",
                "PONTOS ZÉ: Troque tampinhas/pontos no app por descontos de R$ 5, R$ 10 e R$ 20",
                "HORÁRIO DE PICO DE OFERTAS: Quinta a Sábado a partir das 17h"
            ],
            "app_url": "https://www.ze.delivery"
        },
        {
            "service": "🍔 iFood Bebidas & Supermercados (Sertãozinho)",
            "coupons": [
                "CLUBE IFOOD: Pacotes de cupons de 25% OFF e R$ 10 OFF em mercados locais",
                "PROMOÇÃO DA SEMANA: Frete grátis em lojas parceiras de Sertãozinho"
            ],
            "app_url": "https://www.ifood.com.br"
        },
        {
            "service": "📦 Mercado Livre (Mercado Envios Full)",
            "coupons": [
                "FRETE GRÁTIS: Em produtos elegíveis e carrinhos acima de R$ 79",
                "CUPOM SUPERMERCADO: Fique atento aos banners de 10% a 20% OFF no Supermercado Livre"
            ],
            "app_url": "https://www.mercadolivre.com.br"
        },
        {
            "service": "🍷 Wine & Evino",
            "coupons": [
                "WINE: 'BEMVINDO50' ou cupom de indicação (desconto imediato no primeiro kit)",
                "EVINO: 'PRIMEIRACOMPRA' / Cupom via App com 15% extra no carrinho"
            ],
            "app_url": "https://www.wine.com.br"
        }
    ]
