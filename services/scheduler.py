"""
Agendador de Tarefas: Executa a busca nos sites 4 vezes ao dia (08:00, 12:00, 16:00, 20:00)
e envia notificações de promoções aos inscritos no Telegram.
"""
import os
import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Bot

from services.scrapers import run_all_scrapers
from database import get_subscribers, get_recent_price_drops

logger = logging.getLogger(__name__)

async def run_scheduled_scraping(bot: Bot = None):
    """Executa a rotina de busca de ofertas e dispara alertas."""
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    logger.info(f"⏰ [SCHEDULER] Iniciando busca agendada de promoções ({now_str})...")
    
    # Executa os scrapers e salva no SQLite
    summary = run_all_scrapers()
    logger.info(f"✅ [SCHEDULER] Concluído: {summary['total_scraped']} itens analisados.")

    if not bot:
        return

    subscribers = get_subscribers()
    if not subscribers:
        logger.info("ℹ️ Nenhum usuário inscrito para receber notificações agendadas.")
        return

    # Monta a mensagem de resumo
    lines = [
        f"🔔 *ATUALIZAÇÃO DE OFERTAS ({now_str})*\n",
        f"Realizamos a varredura nos supermercados de Sertãozinho e marketplaces!\n"
    ]
    
    if summary["price_drops"]:
        lines.append("🔥 *QUEDAS DE PREÇO DETECTADAS:*")
        for drop in summary["price_drops"][:5]:
            lines.append(
                f"• *{drop['name']}* ({drop['store']})\n"
                f"  De ~R$ {drop['old_price']:.2f}~ por *R$ {drop['new_price']:.2f}*\n"
                f"  🔗 [Acessar Oferta]({drop['link']})"
            )
        lines.append("")
    else:
        lines.append("✨ *DESTAQUES DA RODADA:*")
        for item in summary["top_promos"][:4]:
            orig = f"~R$ {item['original_price']:.2f}~ " if item.get('original_price') else ""
            lines.append(
                f"• *{item['name']}*\n"
                f"  💰 {orig}*R$ {item['price']:.2f}* (-{item['discount_pct']:.0f}%)\n"
                f"  🏪 {item['store']} | 🔗 [Ver]({item['link']})"
            )
            
    lines.append("\n💡 *Dica:* Envie o nome de qualquer bebida para pesquisar preços atuais.")
    
    text = "\n".join(lines)
    
    for chat_id in subscribers:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
        except Exception as e:
            logger.error(f"Erro ao enviar notificação para chat {chat_id}: {e}")

async def start_scheduler_job(app):
    """Inicia o agendador após o loop de eventos estar ativo (post_init)."""
    scheduler = AsyncIOScheduler()
    scheduled_hours = [8, 12, 16, 20]
    
    for hour in scheduled_hours:
        trigger = CronTrigger(hour=hour, minute=0)
        scheduler.add_job(
            run_scheduled_scraping,
            trigger=trigger,
            args=[app.bot],
            name=f"scraping_job_{hour}h"
        )
        logger.info(f"📅 Agendada busca diária para as {hour:02d}:00.")

    scheduler.start()
    logger.info("⏰ Scheduler 4x/dia ativado com sucesso.")
