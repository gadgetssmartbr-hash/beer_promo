"""
Módulo de Inteligência e Avaliação de Preços (Termômetro de Ofertas).
Calcula se um preço está Excelente (Oportunidade), Normal (Na Média) ou Caro (Acima da Média).
"""
from typing import Dict, Any, Optional

# Benchmarks de mercado de referência para Sertãozinho / Brasil (preços médios de mercado)
MARKET_BENCHMARKS = {
    "cerveja_lata_350ml": {"fair_avg": 5.80, "good_deal": 5.10, "great_deal": 4.60},
    "cerveja_long_neck": {"fair_avg": 6.90, "good_deal": 5.90, "great_deal": 5.20},
    "cerveja_artesanal": {"fair_avg": 14.50, "good_deal": 11.90, "great_deal": 9.90},
    "vinho_dia_a_dia": {"fair_avg": 42.00, "good_deal": 32.00, "great_deal": 26.90},
    "vinho_reserva": {"fair_avg": 68.00, "good_deal": 52.00, "great_deal": 42.90},
    "espumante": {"fair_avg": 45.00, "good_deal": 35.00, "great_deal": 29.90}
}

def analyze_price_quality(
    current_price: float,
    original_price: Optional[float] = None,
    historical_min: Optional[float] = None,
    historical_avg: Optional[float] = None
) -> Dict[str, Any]:
    """
    Avalia a qualidade do preço atual em relação ao histórico e descontos.
    Retorna o veredito, nível de oportunidade, cor e recomendação de compra.
    """
    if current_price <= 0:
        return {
            "verdict": "Indisponível",
            "score": "neutral",
            "emoji": "⚪",
            "tag": "Indeterminado",
            "color": "slate",
            "savings_pct": 0,
            "advice": "Sem dados suficientes."
        }

    # Se tivermos histórico no banco
    base_comparison = historical_avg or original_price or (current_price * 1.15)
    
    diff_pct = 0.0
    if base_comparison and base_comparison > 0:
        diff_pct = round(((base_comparison - current_price) / base_comparison) * 100, 1)

    # Verifica se está próximo ou no menor preço histórico
    is_all_time_low = historical_min is not None and current_price <= (historical_min * 1.02)

    # Classificação
    if diff_pct >= 20 or is_all_time_low:
        verdict = "🔥 Oportunidade Real! (Muito Barato)"
        tag = "Excelente Preço"
        score = "great"
        emoji = "🟢"
        color = "emerald"
        advice = "Preço no menor nível registrado. Vale muito a pena comprar agora!"
    elif diff_pct >= 8:
        verdict = "👍 Bom Preço (Abaixo da Média)"
        tag = "Bom Preço"
        score = "good"
        emoji = "🟢"
        color = "teal"
        advice = "Preço vantajoso com desconto real em relação ao mercado."
    elif diff_pct >= -5:
        verdict = "⚖️ Preço Normal / Habitual"
        tag = "Preço Médio"
        score = "fair"
        emoji = "🟡"
        color = "amber"
        advice = "Dentro da média praticada no mercado. Compre apenas se estiver precisando."
    else:
        verdict = "⏳ Preço Alto (Acima da Média)"
        tag = "Preço Alto"
        score = "high"
        emoji = "🔴"
        color = "rose"
        advice = "Está mais caro que a média recente. Recomendamos aguardar nova promoção."

    return {
        "verdict": verdict,
        "tag": tag,
        "score": score,
        "emoji": emoji,
        "color": color,
        "savings_pct": diff_pct,
        "is_all_time_low": is_all_time_low,
        "advice": advice
    }
