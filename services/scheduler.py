"""
Agendador de Tarefas Híbrido:
1. Supermercados Locais de Sertãozinho (Savegnago, Copercana, Paulistão): 3x ao dia (08:00, 13:00, 19:00).
2. Bebidas e Vinhos em Marketplaces (Mercado Livre, Amazon, Wine, Evino): Varredura horária (minuto 30).
"""
import os
import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Bot

from services.scrapers import run_all_scrapers, run_marketplaces_scrapers
from database import get_subscribers, get_recent_price_drops

logger = logging.getLogger(__name__)

async def run_scheduled_scraping(bot: Bot = None):
    """
    Executa a rotina completa diária de busca (supermercados locais + marketplaces).
    Dispara notificações no Telegram com as melhores ofertas reais e quedas de preço.
    """
    now = datetime.now()
    now_str = now.strftime("%d/%m/%Y às %H:%M")
    hour = now.hour
    
    if hour < 12:
        edition_title = "🌅 *RADAR MATINAL DE OFERTAS*"
    elif hour < 18:
        edition_title = "☀️ *RADAR DA TARDE — MERCADO & BEBIDAS*"
    else:
        edition_title = "🌙 *RADAR NOTURNO — ADEGA & HAPPY HOUR*"

    event_banner = _get_special_event_banner(now)
    if event_banner:
        edition_title = f"{event_banner} | {edition_title}"

    logger.info(f"⏰ [SCHEDULER GERAL] Iniciando busca completa diária ({now_str})...")
    
    # Executa os scrapers em thread separada para não travar o loop assíncrono
    summary = await asyncio.to_thread(run_all_scrapers)
    logger.info(f"✅ [SCHEDULER GERAL] Concluído: {summary['total_scraped']} itens analisados.")

    if not bot:
        return

    # 1. Verifica alertas individuais por preço-alvo de cada usuário
    await check_and_notify_target_alerts(bot)

    subscribers = get_subscribers()
    if not subscribers:
        logger.info("ℹ️ Nenhum usuário inscrito para receber notificações agendadas.")
        return

    price_drops = summary.get("price_drops", [])
    top_promos = summary.get("top_promos", [])
    if not top_promos:
        top_promos = get_recent_price_drops(limit=8)

    # Filtra promoções com desconto real comprovado
    real_promos = [
        item for item in top_promos 
        if item.get("discount_pct", 0) >= 10 or item.get("original_price", 0) > item.get("price", 0) * 1.10
    ]

    lines = [
        f"{edition_title} 🎯\n",
        f"📅 _{now_str} • Sertãozinho e Marketplaces Online_\n"
    ]
    
    if price_drops:
        lines.append("📉 *QUEDAS DE PREÇO RECENTES:*")
        for drop in price_drops[:4]:
            lines.append(
                f"• *{drop['name']}* ({drop['store']})\n"
                f"  De ~R$ {drop['old_price']:.2f}~ por *R$ {drop['new_price']:.2f}* 📉\n"
                f"  🔗 [Acessar Oferta]({drop['link']})"
            )
        lines.append("")
        
    if real_promos:
        lines.append("🔥 *MELHORES DESCONTOS REAIS ATIVOS:*")
        for item in real_promos[:5]:
            orig = f"~R$ {item['original_price']:.2f}~ " if item.get('original_price') else ""
            disc = f"(-{item['discount_pct']:.0f}%)" if item.get('discount_pct') else "🔥"
            lines.append(
                f"• *{item['name']}*\n"
                f"  💰 {orig}*R$ {item['price']:.2f}* {disc}\n"
                f"  🏪 {item['store']} | 🔗 [Acessar Oferta]({item['link']})"
            )
    else:
        lines.append("⚡ Preços estáveis nas redes locais hoje. Confira o comparador no site.")

    lines.append("\n🌐 Compare carrinhos e cervejas importadas no [Microsite](https://gadgetssmartbr-hash.github.io/beer_promo/).")
    
    text = "\n".join(lines)
    
    for chat_id in subscribers:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
            logger.info(f"📨 Notificação geral enviada com sucesso para chat {chat_id}.")
        except Exception as e:
            logger.error(f"Erro ao enviar notificação geral para chat {chat_id}: {e}")

async def check_and_notify_target_alerts(bot: Bot):
    """
    Verifica se algum produto atingiu o preço alvo configurado pelos usuários.
    Envia mensagens diretas personalizadas para cada usuário.
    """
    from database import check_target_hits_for_watchlist
    hits = check_target_hits_for_watchlist()
    if not hits:
        return

    logger.info(f"🎯 [TARGET ALERTS] {len(hits)} alertas de preço alvo disparados!")
    for h in hits:
        chat_id = h["chat_id"]
        savings_text = f" (Economia de R$ {h['savings']:.2f} por unidade!)" if h.get("savings", 0) > 0 else ""
        pack_text = f"\n📦 Embalagem: {h['unit_pricing'].get('pack_label', '')}" if h.get("is_pack") else ""
        unit_display = h.get("unit_price_display") or f"R$ {h['current_price']:.2f}"
        
        msg = (
            f"🎯 *ALERTA DE PREÇO ALVO ATINGIDO!* 🔔\n\n"
            f"O produto que você estava vigiando atingiu o seu preço desejado:\n"
            f"📌 *{h['item_name']}*\n"
            f"🏷️ *{h['product_name']}*\n\n"
            f"🎯 Seu Preço Alvo: *R$ {h['target_price']:.2f}*\n"
            f"💰 Preço Encontrado: *{unit_display}*{savings_text}\n"
            f"🏪 Loja: *{h['store']}*{pack_text}\n\n"
            f"👉 [CLIQUE AQUI PARA APROVEITAR A OFERTA]({h['link']})\n\n"
            f"⚡ _Monitorado automaticamente pelo robô de Sertãozinho._"
        )
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=msg,
                parse_mode="Markdown",
                disable_web_page_preview=False
            )
            logger.info(f"🎯 Alerta alvo enviado com sucesso para {chat_id}.")
        except Exception as e:
            logger.error(f"Erro ao enviar alerta de preço alvo para {chat_id}: {e}")

_EVENT_STATE = {"last_signature": ""}
_IMPORTED_BEER_KEYWORDS = (
    "guinness", "paulaner", "erdinger", "leffe", "hoegaarden",
    "blue moon", "duvel", "chimay", "la trappe", "delirium",
    "franziskaner", "weihenstephaner"
)


def _get_special_event_banner(now: datetime) -> str:
    """Retorna selo de destaque para grandes eventos sazonais (11.11 e Black Friday)."""
    if now.month == 11 and now.day == 11:
        return "🎉 *ESPECIAL 11.11*"
    if now.month == 11 and 20 <= now.day <= 30:
        return "🖤 *ESPECIAL BLACK FRIDAY*"
    return ""


def _is_event_featured_item(category: str, name: str) -> bool:
    """Seleciona vinhos e cervejas importadas/especiais elegíveis aos destaques de evento."""
    if category == "vinho":
        return True
    if category == "cerveja":
        lower_name = name.lower()
        return any(kw in lower_name for kw in _IMPORTED_BEER_KEYWORDS)
    return False


def _get_active_event_highlights(today_str: str, min_discount: float = 30.0, limit: int = 5):
    """Busca ofertas ativas hoje na Amazon com desconto >= min_discount em vinhos e cervejas importadas."""
    from database import get_connection

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.name, p.category, p.store, p.link, ph.price, ph.original_price, ph.discount_pct
            FROM price_history ph
            JOIN products p ON p.id = ph.product_id
            JOIN (
                SELECT product_id, MAX(id) AS latest_id
                FROM price_history
                WHERE date(recorded_at) = ?
                GROUP BY product_id
            ) latest ON latest.latest_id = ph.id
            WHERE p.store LIKE '%Amazon%'
              AND ph.discount_pct >= ?
              AND ph.original_price IS NOT NULL
              AND ph.original_price > ph.price
            ORDER BY ph.discount_pct DESC, ph.price ASC
        """, (today_str, min_discount))
        rows = [dict(r) for r in cursor.fetchall()]

    return [r for r in rows if _is_event_featured_item(r["category"], r["name"])][:limit]


async def _send_markdown_broadcast(bot: Bot, subscribers, text: str, log_prefix: str, disable_preview: bool = True):
    """Envia mensagem Markdown para os inscritos com tratamento de erro individual."""
    for chat_id in subscribers:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="Markdown",
                disable_web_page_preview=disable_preview
            )
            logger.info(f"{log_prefix} enviado para {chat_id}.")
        except Exception as e:
            logger.error(f"Erro ao enviar {log_prefix} para chat {chat_id}: {e}")


async def run_scheduled_marketplaces_hourly(bot: Bot = None):
    """
    Executa a rotina horária de bebidas e vinhos nos Marketplaces Online.
    Notifica no Telegram se houver quedas de preço imediatas, destaques ativos em mega eventos ou alertas atingidos.
    """
    now = datetime.now()
    now_str = now.strftime("%d/%m/%Y %H:%M")
    event_banner = _get_special_event_banner(now)
    logger.info(f"⚡ [SCHEDULER MARKETPLACES] Iniciando varredura horária de bebidas ({now_str})...")

    summary = await asyncio.to_thread(run_marketplaces_scrapers)
    logger.info(f"✅ [SCHEDULER MARKETPLACES] Concluído: {summary['total_scraped']} itens analisados.")

    if not bot:
        return

    # 1. Verifica alertas individuais por preço-alvo
    await check_and_notify_target_alerts(bot)

    subscribers = get_subscribers()
    if not subscribers:
        return

    price_drops = summary.get("price_drops", [])
    if price_drops:
        header_prefix = f"{event_banner} | " if event_banner else ""
        lines = [
            f"{header_prefix}⚡ *OFERTA RELÂMPAGO REAL — MARKETPLACES ({now_str})* 📦\n",
            "Queda de preço confirmada em bebidas e vinhos nos marketplaces online:\n"
        ]
        for drop in price_drops[:5]:
            lines.append(
                f"• *{drop['name']}* ({drop['store']})\n"
                f"  De ~R$ {drop['old_price']:.2f}~ por *R$ {drop['new_price']:.2f}* 💥\n"
                f"  🔗 [Acessar Oferta]({drop['link']})"
            )
        lines.append("\n🌐 Linha do tempo atualizada no [Microsite](https://gadgetssmartbr-hash.github.io/beer_promo/).")
        await _send_markdown_broadcast(bot, subscribers, "\n".join(lines), "📨 Alerta horário")
        return

    if not event_banner:
        logger.info("ℹ️ [SCHEDULER MARKETPLACES] Nenhuma queda de preço detectada nesta hora. Notificação silenciosa.")
        return

    today_str = now.strftime("%Y-%m-%d")
    highlights = await asyncio.to_thread(_get_active_event_highlights, today_str, 30.0, 5)
    if not highlights:
        logger.info("ℹ️ [SCHEDULER MARKETPLACES] Sem quedas novas nem destaques ativos >= 30% no evento.")
        return

    signature = f"{today_str}:" + "|".join(
        f"{h['name']}:{h['price']:.2f}:{h['discount_pct']:.1f}" for h in highlights
    )
    if signature == _EVENT_STATE["last_signature"]:
        logger.info("ℹ️ [SCHEDULER MARKETPLACES] Destaques do evento idênticos ao último envio; evitando repetição.")
        return

    _EVENT_STATE["last_signature"] = signature
    lines = [
        f"{event_banner} | 🔥 *DESTAQUES ATIVOS AMAZON PRIME ({now_str})* 🏷️\n",
        "Vinhos e cervejas importadas com desconto real de *30% ou mais* no radar:\n"
    ]
    for item in highlights:
        lines.append(
            f"• *{item['name']}*\n"
            f"  De ~R$ {item['original_price']:.2f}~ por *R$ {item['price']:.2f}* *(-{item['discount_pct']:.0f}%)* 💥\n"
            f"  🔗 [Acessar na Amazon]({item['link']})"
        )
    lines.append("\n🌐 Linha do tempo atualizada no [Microsite](https://gadgetssmartbr-hash.github.io/beer_promo/).")
    await _send_markdown_broadcast(bot, subscribers, "\n".join(lines), "🔥 Destaque sazonal")


async def run_sommelier_amazon_wine_hourly(bot: Bot = None):
    """
    Varredura horária omni-channel de Vinhos Tintos Secos Finos.
    Monitora Amazon Prime, Mercado Livre Full, Wine, Evino, Grand Cru, Mistral e Savegnago.
    Avalia rótulos de alta qualidade, notas de degustação e despacha a melhor oferta
    para os usuários a cada 1 hora com entrega rápida.
    """
    from services.scrapers.amazon_scraper import scrape_amazon_wine_deals
    from services.scrapers.wine_scraper import scrape_wine_evino_deals
    from services.wine_sommelier import get_next_hourly_sommelier_wine, format_wine_sommelier_card
    from database import save_price_record

    logger.info("🍷 [SOMMELIER WINE HOURLY] Iniciando varredura omni-channel de vinhos tintos secos...")

    # 1. Busca e atualiza novos vinhos nos marketplaces e adegas
    try:
        new_wines = await asyncio.to_thread(scrape_amazon_wine_deals)
        wine_clubs = await asyncio.to_thread(scrape_wine_evino_deals)
        all_incoming = (new_wines or []) + (wine_clubs or [])

        for item in all_incoming:
            save_price_record(
                name=item["name"],
                category=item["category"],
                store=item["store"],
                price=item["price"],
                original_price=item.get("original_price"),
                link=item.get("link", "")
            )
        logger.info(f"🍷 [SOMMELIER WINE HOURLY] {len(all_incoming)} vinhos atualizados de múltiplas plataformas.")
    except Exception as e:
        logger.error(f"Erro ao buscar vinhos nas lojas: {e}")

    if not bot:
        return

    # 2. Seleciona a oferta em destaque para esta hora (rotacionando lojas e priorizando descontos)
    chosen_wine = get_next_hourly_sommelier_wine()
    if not chosen_wine:
        logger.info("ℹ️ Nenhum vinho tinto seco selecionado para envio nesta hora.")
        return

    card_text = format_wine_sommelier_card(chosen_wine)
    event_banner = _get_special_event_banner(datetime.now())
    if event_banner:
        card_text = f"{event_banner}\n{card_text}"

    # 3. Dispara para os inscritos (garantindo o chat 1292185101)
    subscribers = set(get_subscribers())
    subscribers.add(1292185101)

    await _send_markdown_broadcast(
        bot,
        subscribers,
        card_text,
        f"🍷 [SOMMELIER WINE HOURLY] Oferta de vinho ({chosen_wine.get('store')})",
        disable_preview=False
    )


async def start_scheduler_job(app):
    """Configura e inicia o agendador de tarefas híbrido."""
    scheduler = AsyncIOScheduler()
    
    # 1. Varredura Completa Geral: 3x ao dia (08:00, 13:00, 19:00)
    scheduled_general_hours = [8, 13, 19]
    for hour in scheduled_general_hours:
        trigger = CronTrigger(hour=hour, minute=0)
        scheduler.add_job(
            run_scheduled_scraping,
            trigger=trigger,
            args=[app.bot],
            name=f"scraping_geral_{hour}h",
            misfire_grace_time=3600  # Permite até 1h de tolerância, nunca descarta a execução
        )
        logger.info(f"📅 [Geral] Agendada busca completa para as {hour:02d}:00 (grace=3600s).")

    # 2. Varredura Horária de Marketplaces: no minuto 30 (para não colidir com o geral das 08h, 13h, 19h)
    trigger_hourly = CronTrigger(minute=30, hour="8-23")
    scheduler.add_job(
        run_scheduled_marketplaces_hourly,
        trigger=trigger_hourly,
        args=[app.bot],
        name="scraping_marketplaces_hourly",
        misfire_grace_time=3600  # Permite até 1h de tolerância, nunca descarta a execução
    )
    logger.info("⚡ [Marketplaces] Agendada varredura no minuto :30 de cada hora (08h às 23h, grace=3600s).")

    # 3. Varredura Horária do Sommelier Amazon (Vinhos Tintos Secos): no minuto 15 de cada hora
    trigger_wine = CronTrigger(minute=15, hour="8-23")
    scheduler.add_job(
        run_sommelier_amazon_wine_hourly,
        trigger=trigger_wine,
        args=[app.bot],
        name="sommelier_amazon_wine_hourly",
        misfire_grace_time=3600
    )
    logger.info("🍷 [Sommelier Amazon] Agendada busca de vinhos tintos secos a cada 1 hora (minuto :15, 08h às 23h, grace=3600s).")

    scheduler.start()
    logger.info("⏰ Scheduler híbrido ativado com sucesso (Geral 3x/dia + Marketplaces hora:30 + Sommelier hora:15).")
