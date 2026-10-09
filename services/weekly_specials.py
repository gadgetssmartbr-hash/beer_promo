"""
Guia de Dias Temáticos e Encartes Semanais de Ofertas em Sertãozinho/SP.
Mapeia os dias tradicionais de descontos e promoções do Savegnago, Copercana e Paulistão Atacadista.
"""
from datetime import datetime
from typing import Dict, Any, List

WEEKLY_SCHEDULE = {
    "segunda": {
        "day_name": "Segunda-feira",
        "highlights": [
            {"store": "Savegnago", "theme": "Segunda da Limpeza & Higiene", "badge": "🧼 Limpeza", "color": "sky", "desc": "Descontos em sabão líquido, amaciantes, papel higiênico e desinfetantes."},
            {"store": "Paulistão Atacadista", "theme": "Segunda do Comerciante & Food Service", "badge": "📦 Volume", "color": "amber", "desc": "Preços especiais em embalagens institucionais e caixas fechadas."}
        ]
    },
    "terca": {
        "day_name": "Terça-feira",
        "highlights": [
            {"store": "Copercana", "theme": "Terça e Quarta Verde", "badge": "🥬 Hortifruti", "color": "emerald", "desc": "Feira completa com frutas, legumes e verduras direto dos produtores cooperados."},
            {"store": "Paulistão Atacadista", "theme": "Terça da Feira & Hortifruti Atacado", "badge": "🥬 Feira", "color": "emerald", "desc": "Sacos e caixas de batata, cebola, tomate e frutas com preço de atacado."}
        ]
    },
    "quarta": {
        "day_name": "Quarta-feira",
        "highlights": [
            {"store": "Savegnago", "theme": "Quarta e Quinta do Hortifruti", "badge": "🥬 Super Feira", "color": "emerald", "desc": "A maior feira da rede com bananas, tomates, maçãs e legumes frescos."},
            {"store": "Copercana", "theme": "Quarta Verde (2º Dia)", "badge": "🥬 Hortifruti", "color": "emerald", "desc": "Continuação da feira de hortifruti com preços reduzidos."}
        ]
    },
    "quinta": {
        "day_name": "Quinta-feira",
        "highlights": [
            {"store": "Paulistão Atacadista", "theme": "Quinta do Açougue & Carnes", "badge": "🥩 Açougue", "color": "rose", "desc": "Cortes nobres bovinos, picanha, contrafilé e frango com desconto especial."},
            {"store": "Savegnago", "theme": "Quinta do Hortifruti & Padaria", "badge": "🥖 Pães & Feira", "color": "amber", "desc": "Fechamento da feira e ofertas no setor de padaria e laticínios."}
        ]
    },
    "sexta": {
        "day_name": "Sexta-feira",
        "highlights": [
            {"store": "Savegnago", "theme": "Sexta e Sábado do Churrasco & Cerveja", "badge": "🍺 Cerveja & Carnes", "color": "rose", "desc": "Ofertas em picanha, cervejas puro malte, carvão e linguiças para o fim de semana."},
            {"store": "Paulistão Atacadista", "theme": "Sexta do Boteco & Bebidas", "badge": "🍺 Fardos de Bebidas", "color": "amber", "desc": "Fardos de cerveja (Spaten, Heineken, Amstel) e refrigerantes no menor preço."},
            {"store": "Copercana", "theme": "Sexta Especial do Cooperado", "badge": "⭐ Cooperados", "color": "teal", "desc": "Descontos no cartão Copercana e ofertas em itens de mercearia e açougue."}
        ]
    },
    "sabado": {
        "day_name": "Sábado",
        "highlights": [
            {"store": "Savegnago", "theme": "Sábado da Família & Adega", "badge": "🍷 Vinhos & Carnes", "color": "wine", "desc": "Descontos em vinhos importados, queijos, carnes nobres e cervejas artesanais."},
            {"store": "Copercana", "theme": "Sábado do Churrasco", "badge": "🥩 Carnes", "color": "rose", "desc": "Cortes especiais de açougue e cervejas geladas."},
            {"store": "Paulistão Atacadista", "theme": "Sábado do Carrinho Cheio", "badge": "🛒 Cesta Básica", "color": "sky", "desc": "Ofertas em volume para abastecer o mês da família."}
        ]
    },
    "domingo": {
        "day_name": "Domingo",
        "highlights": [
            {"store": "Savegnago", "theme": "Domingo de Ofertas Relâmpago", "badge": "⚡ Relâmpago", "color": "amber", "desc": "Ofertas exclusivas de domingo em carnes, aves e bebidas."},
            {"store": "Copercana", "theme": "Domingo em Família", "badge": "🥖 Padaria & Assados", "color": "teal", "desc": "Frango assado, massas e bebidas para o almoço de domingo."}
        ]
    }
}

def get_today_specials() -> Dict[str, Any]:
    """Retorna os dias temáticos de hoje em Sertãozinho."""
    weekday_idx = datetime.now().weekday() # 0 = Segunda, 6 = Domingo
    keys = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]
    today_key = keys[weekday_idx]
    
    today_data = WEEKLY_SCHEDULE.get(today_key, {})
    return {
        "today_key": today_key,
        "day_name": today_data.get("day_name", ""),
        "highlights": today_data.get("highlights", []),
        "all_schedule": WEEKLY_SCHEDULE
    }
