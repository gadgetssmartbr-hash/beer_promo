"""
Agendador de Tarefas Híbrido:
1. Supermercados Locais de Sertãozinho (Savegnago, Copercana, Paulistão): 3x ao dia (08:00, 13:00, 19:00).
2. Bebidas e Vinhos em Marketplaces (Mercado Livre, Amazon, Wine, Evino): Varredura de HORA EM HORA (08:00 às 23:00)
   para capturar ofertas relâmpago e quedas de preço instantâneas!
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
    """Executa a rotina completa de busca (supermercados locais + marketplaces) e dispara resumo geral."""
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    logger.info(f"⏰ [SCHEDULER GERAL] Iniciando busca completa diária ({now_str})...")
    
    summary = run_all_scrapers()
    logger.info(f"✅ [SCHEDULER GERAL] Concluído: {summary['total_scraped']} itens analisados.")

    if not bot:
        return

    subscribers = get_subscribers()
    if not subscribers:
        logger.info("ℹ️ Nenhum usuário inscrito para receber notificações agendadas.")
        return

    lines = [
        f"🔔 *ATUALIZAÇÃO GERAL DE OFERTAS ({now_str})*\n",
        f"Varredura completa nos **Supermercados de Sertãozinho** e **Marketplaces Online**!\n"
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
            
    lines.append("\n💡 *Dica:* Digite o nome de qualquer produto para fazer uma busca em tempo real agora mesmo.")
    
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
            logger.error(f"Erro ao enviar notificação geral para chat {chat_id}: {e}")

async def run_scheduled_marketplaces_hourly(bot: Bot = None):
    """Executa a rotina horária de busca de bebidas e vinhos nos Marketplaces Online."""
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    logger.info(f"⚡ [SCHEDULER MARKETPLACES] Iniciando varredura horária de bebidas ({now_str})...")
    
    summary = run_marketplaces_scrapers()
    logger.info(f"✅ [SCHEDULER MARKETPLACES] Concluído: {summary['total_scraped']} itens analisados.")

    # Notifica os usuários apenas se houver queda de preço/oferta relâmpago nova detectada nesta hora
    if summary["price_drops"] and bot:
        subscribers = get_subscribers()
        if not subscribers:
            return
            
        lines = [
            f"⚡ *ALERTA RELÂMPAGO — MARKETPLACES ({now_str})* 📦\n",
            f"Detectamos queda de preço em bebidas nos marketplaces online!\n"
        ]
        for drop in summary["price_drops"]:
            lines.append(
                f"• *{drop['name']}* ({drop['store']})\n"
                f"  De ~R$ {drop['old_price']:.2f}~ por *R$ {drop['new_price']:.2f}*\n"
                f"  🔗 [Acessar Oferta]({drop['link']})"
            )
        lines.append("\n🌐 Confira todos os preços atualizados no Microsite.")
        
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
                logger.error(f"Erro ao enviar alerta horário para chat {chat_id}: {e}")

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
            name=f"scraping_geral_{hour}h"
        )
        logger.info(f"📅 [Geral] Agendada busca completa para as {hour:02d}:00.")

    # 2. Varredura Horária de Marketplaces (Bebidas e Vinhos): de hora em hora entre 08h e 23h
    trigger_hourly = CronTrigger(minute=0, hour="8-23")
    scheduler.add_job(
        run_scheduled_marketplaces_hourly,
        trigger=trigger_hourly,
        args=[app.bot],
        name="scraping_marketplaces_hourly"
    )
    logger.info("⚡ [Marketplaces] Agendada varredura de HORA EM HORA (08h às 23h).")

    scheduler.start()
    logger.info("⏰ Scheduler híbrido ativado com sucesso (Geral 3x/dia + Marketplaces 1x/hora).")
