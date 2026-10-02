"""
Bot do Telegram - Rastreador de Ofertas de Cervejas e Vinhos (Sertãozinho/SP e Marketplaces)
Com suporte a Banco de Dados SQLite, Histórico de Preços e Agendamento 4x ao dia.
"""
import os
import sys
import logging
from typing import List
from dotenv import load_dotenv

# Fix encoding on Windows console
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from services import (
    search_mercadolivre,
    get_beer_deals_ml,
    get_wine_deals_ml,
    get_local_supermarkets,
    get_wine_clubs_promos,
    get_active_coupons_and_tips,
)
from services.scrapers import run_all_scrapers
from services.scheduler import start_scheduler_job
from database import (
    init_db,
    add_subscriber,
    remove_subscriber,
    get_subscribers,
    get_recent_price_drops,
    get_product_history,
)

# Carrega variáveis de ambiente
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Configuração de Logs
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_main_menu_keyboard(chat_id: int = None):
    subscribers = get_subscribers()
    is_subscribed = chat_id in subscribers if chat_id else False
    
    alert_btn = (
        InlineKeyboardButton("🔕 Desativar Alertas (4x/dia)", callback_data="menu_toggle_alerts")
        if is_subscribed else
        InlineKeyboardButton("🔔 Ativar Alertas (4x/dia)", callback_data="menu_toggle_alerts")
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🍺 Ofertas de Cervejas", callback_data="menu_beers"),
            InlineKeyboardButton("🍷 Ofertas de Vinhos", callback_data="menu_wines"),
        ],
        [
            InlineKeyboardButton("🛒 Mercados em Sertãozinho", callback_data="menu_supermarkets"),
            InlineKeyboardButton("🎟️ Cupons & Zé Delivery", callback_data="menu_coupons"),
        ],
        [
            InlineKeyboardButton("📊 Histórico de Preços", callback_data="menu_history"),
            InlineKeyboardButton("⚡ Rodar Busca Agora", callback_data="menu_run_now"),
        ],
        [
            InlineKeyboardButton("🌐 Acessar Microsite Web", callback_data="menu_microsite"),
            alert_btn,
        ],
        [
            InlineKeyboardButton("🔄 Atualizar Menu", callback_data="menu_start"),
        ]
    ]

    return InlineKeyboardMarkup(keyboard)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Menu Inicial"""
    chat_id = update.effective_chat.id
    # Auto-inscreve o usuário ao dar /start para comodidade
    add_subscriber(chat_id, update.effective_user.username if update.effective_user else "")

    welcome_text = (
        "🍻 *Olá! Bem-vindo ao Rastreador de Ofertas de Bebidas!* 🍷\n\n"
        "Estou configurado para encontrar as melhores promoções de **Cervejas e Vinhos** "
        "com entrega em **Sertãozinho/SP**, cobrindo Savegnago, Copercana, Zé Delivery, Mercado Livre, Wine, Evino e Amazon.\n\n"
        "⏰ *Agendamento Ativo:* Buscas automáticas rodando **4x ao dia** (08:00, 12:00, 16:00, 20:00) com histórico salvo!\n\n"
        "👇 *Escolha uma das opções abaixo ou envie o nome de uma bebida para buscar:*"
    )
    if update.message:
        await update.message.reply_text(
            welcome_text,
            reply_markup=get_main_menu_keyboard(chat_id),
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
    elif update.callback_query:
        await update.callback_query.edit_message_text(
            welcome_text,
            reply_markup=get_main_menu_keyboard(chat_id),
            parse_mode="Markdown",
            disable_web_page_preview=True
        )

async def handle_beers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("🔍 *Buscando ofertas de cervejas com entrega rápida...*", parse_mode="Markdown")
    
    deals = get_beer_deals_ml()
    
    msg_lines = ["🍺 *OFERTAS EM DESTAQUE - CERVEJAS:*\n"]
    if deals:
        for idx, item in enumerate(deals, start=1):
            line = (
                f"*{idx}. {item['title']}*\n"
                f"💰 Preço: *{item['price']}*{item['discount']}\n"
                f"{item['free_shipping']} {item['is_full']}\n"
                f"🔗 [Ver oferta no {item['store']}]({item['link']})\n"
            )
            msg_lines.append(line)
    else:
        msg_lines.append("Nenhuma oferta encontrada no momento. Tente novamente em instantes.")

    msg_lines.append("\n💡 *Dica Zé Delivery Sertãozinho:* Peça pelo app Zé Delivery para receber gelada em ~35min.")
    
    back_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Voltar ao Menu Principal", callback_data="menu_start")]
    ])
    
    await query.edit_message_text(
        "\n".join(msg_lines),
        reply_markup=back_keyboard,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

async def handle_wines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("🔍 *Buscando ofertas de vinhos e kits promocionais...*", parse_mode="Markdown")
    
    deals = get_wine_deals_ml()
    clubs = get_wine_clubs_promos()
    
    msg_lines = ["🍷 *OFERTAS EM DESTAQUE - VINHOS & KITS:*\n"]
    
    if deals:
        for idx, item in enumerate(deals, start=1):
            line = (
                f"*{idx}. {item['title']}*\n"
                f"💰 Preço: *{item['price']}*{item['discount']}\n"
                f"{item['free_shipping']} {item['is_full']}\n"
                f"🔗 [Ver oferta no {item['store']}]({item['link']})\n"
            )
            msg_lines.append(line)
            
    msg_lines.append("\n🍇 *LOJAS ESPECIALIZADAS & CLUBES:*")
    for club in clubs:
        msg_lines.append(f"\n*{club['store']}*")
        msg_lines.append(f"✨ {club['title']}")
        msg_lines.append(f"🏷️ {club['deal_type']}")
        msg_lines.append(f"🔗 [Acessar Loja]({club['url']})")

    back_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Voltar ao Menu Principal", callback_data="menu_start")]
    ])
    
    await query.edit_message_text(
        "\n".join(msg_lines),
        reply_markup=back_keyboard,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

async def handle_supermarkets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    supermarkets = get_local_supermarkets()
    msg_lines = ["🛒 *SUPERMERCADOS COM DELIVERY EM SERTÃOZINHO/SP:*\n"]
    
    for sm in supermarkets:
        msg_lines.append(f"🏪 *{sm['name']}*")
        if "benefits" in sm:
            msg_lines.append(f"💳 Benefícios: {sm['benefits']}")
        if "highlight_categories" in sm:
            for cat in sm["highlight_categories"]:
                msg_lines.append(f"  • {cat}")
        if "website" in sm:
            msg_lines.append(f"🌐 [Acessar Site/Ofertas]({sm['website']})\n")
            
    back_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Voltar ao Menu Principal", callback_data="menu_start")]
    ])
    
    await query.edit_message_text(
        "\n".join(msg_lines),
        reply_markup=back_keyboard,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

async def handle_coupons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    coupons_data = get_active_coupons_and_tips()
    msg_lines = ["🎟️ *CUPONS, DICAS & ENTREGA RÁPIDA:*\n"]
    
    for item in coupons_data:
        msg_lines.append(f"*{item['service']}*")
        for coup in item["coupons"]:
            msg_lines.append(f"  • {coup}")
        msg_lines.append(f"📲 [Acessar Plataforma]({item['app_url']})\n")
        
    back_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Voltar ao Menu Principal", callback_data="menu_start")]
    ])
    
    await query.edit_message_text(
        "\n".join(msg_lines),
        reply_markup=back_keyboard,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

async def handle_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Exibe o histórico recente de preços e promoções registradas."""
    query = update.callback_query
    await query.answer()
    
    promos = get_recent_price_drops(limit=8)
    msg_lines = ["📊 *HISTÓRICO RECENTE DE PREÇOS & PROMOÇÕES:*\n"]
    
    if promos:
        for p in promos:
            orig = f"~R$ {p['original_price']:.2f}~ " if p.get("original_price") else ""
            msg_lines.append(
                f"• *{p['name']}*\n"
                f"  💰 {orig}*R$ {p['price']:.2f}* (-{p['discount_pct']:.0f}%)\n"
                f"  🏪 {p['store']} | 🕒 {p['recorded_at']}\n"
                f"  🔗 [Acessar Oferta]({p['link']})\n"
            )
    else:
        msg_lines.append("Ainda não há histórico registrado. Clique em '⚡ Rodar Busca Agora' para coletar a primeira rodada!")
        
    back_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ Rodar Nova Varredura", callback_data="menu_run_now")],
        [InlineKeyboardButton("🔙 Voltar ao Menu Principal", callback_data="menu_start")]
    ])
    
    await query.edit_message_text(
        "\n".join(msg_lines),
        reply_markup=back_keyboard,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

async def handle_run_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Executa a varredura nos sites imediatamente sob demanda."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("⏳ *Executando bots de busca em tempo real (Savegnago, Mercado Livre, Wine)...*", parse_mode="Markdown")
    
    summary = run_all_scrapers()
    
    lines = [
        f"✅ *VARREDURA CONCLUÍDA COM SUCESSO!*\n",
        f"📦 **Itens analisados e atualizados no histórico:** `{summary['total_scraped']}`",
        f"💾 **Preços registrados no banco SQLite:** `{summary['total_saved']}`\n"
    ]
    
    if summary["price_drops"]:
        lines.append("🔥 *QUEDAS DE PREÇO IDENTIFICADAS:*")
        for drop in summary["price_drops"][:4]:
            lines.append(f"• *{drop['name']}* ({drop['store']})\n  De ~R$ {drop['old_price']:.2f}~ por *R$ {drop['new_price']:.2f}*")
        lines.append("")
        
    lines.append("✨ *TOP OFERTAS SALVAS:*")
    for item in summary["top_promos"][:4]:
        orig = f"~R$ {item['original_price']:.2f}~ " if item.get('original_price') else ""
        lines.append(
            f"• *{item['name']}*\n"
            f"  💰 {orig}*R$ {item['price']:.2f}* (-{item['discount_pct']:.0f}%)\n"
            f"  🏪 {item['store']} | 🔗 [Ver]({item['link']})"
        )
        
    back_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Ver Histórico Completo", callback_data="menu_history")],
        [InlineKeyboardButton("🔙 Voltar ao Menu Principal", callback_data="menu_start")]
    ])
    
    await query.edit_message_text(
        "\n".join(lines),
        reply_markup=back_keyboard,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

async def handle_toggle_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ativa ou desativa notificações agendadas 4x/dia."""
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_chat.id
    username = update.effective_user.username if update.effective_user else ""
    
    subscribers = get_subscribers()
    if chat_id in subscribers:
        remove_subscriber(chat_id)
        text = "🔕 *Alertas automáticos desativados.* Você não receberá mais os resumos das 4 rodadas diárias."
    else:
        add_subscriber(chat_id, username)
        text = "🔔 *Alertas automáticos ativados com sucesso!*\n\nVocê receberá as melhores ofertas e quedas de preço 4 vezes ao dia: às **08:00, 12:00, 16:00 e 20:00**."
        
    back_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Voltar ao Menu Principal", callback_data="menu_start")]
    ])
    
    await query.edit_message_text(
        text,
        reply_markup=back_keyboard,
        parse_mode="Markdown"
    )

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para /buscar <termo> ou mensagens normais de texto com histórico"""
    if context.args:
        query_text = " ".join(context.args)
    elif update.message and update.message.text:
        query_text = update.message.text.strip()
    else:
        return
        
    if query_text.startswith("/"):
        return

    wait_msg = await update.message.reply_text(
        f"🔎 *Buscando ofertas e histórico para:* `{query_text}`...",
        parse_mode="Markdown"
    )
    
    # 1. Verifica se temos dados no histórico SQLite
    history_records = get_product_history(query_text, limit=3)
    
    # 2. Gera links diretos nos marketplaces
    results = search_mercadolivre(query_text, limit=4)
    
    msg_lines = [f"🎯 *RESULTADOS PARA:* `{query_text}`\n"]
    
    if history_records:
        msg_lines.append("📊 *HISTÓRICO NO BANCO DE DADOS:*")
        for hr in history_records:
            msg_lines.append(
                f"• *{hr['name']}*\n"
                f"  💰 Preço Atual: *R$ {hr['current_price']:.2f}*\n"
                f"  📉 Menor Preço Registrado: *R$ {hr['min_price']:.2f}* | Média: R$ {hr['avg_price']:.2f}\n"
            )
        msg_lines.append("")
        
    msg_lines.append("🛒 *LINKS DE COMPRA DIRETA & ENTREGA RÁPIDA:*")
    for idx, item in enumerate(results, start=1):
        line = (
            f"*{idx}. {item['title']}*\n"
            f"💰 {item['price']}\n"
            f"{item['free_shipping']} {item['is_full']}\n"
            f"🔗 [Ver no {item['store']}]({item['link']})\n"
        )
        msg_lines.append(line)
        
    back_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Voltar ao Menu Principal", callback_data="menu_start")]
    ])
    
    await wait_msg.edit_text(
        "\n".join(msg_lines),
        reply_markup=back_keyboard,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

async def handle_microsite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    site_url = "https://gadgetssmartbr-hash.github.io/beer_promo/"
    
    text = (
        "🌐 *MICROSITE DE PROMOÇÕES NO AR!* 🍺🍷\n\n"
        "Você pode visualizar todo o catálogo de ofertas em um painel interativo pelo navegador!\n\n"
        f"🔗 *Acesse o site:* [{site_url}]({site_url})\n\n"
        "✨ *Recursos do Microsite:*\n"
        "• Filtros por categorias (Cervejas, Vinhos, Supermercados)\n"
        "• Busca em tempo real com ordenação por menor preço e desconto\n"
        "• Links diretos para Savegnago, Mercado Livre Full, Amazon Prime e Wine\n"
        "• Atualizado automaticamente 4 vezes ao dia!"
    )
    
    back_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Abrir Microsite no Navegador", url=site_url)],
        [InlineKeyboardButton("🔙 Voltar ao Menu Principal", callback_data="menu_start")]
    ])
    
    await query.edit_message_text(
        text,
        reply_markup=back_keyboard,
        parse_mode="Markdown",
        disable_web_page_preview=False
    )


async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Roteador para os botões inline"""
    query = update.callback_query
    data = query.data
    
    if data == "menu_start":
        await start_command(update, context)
    elif data == "menu_beers":
        await handle_beers(update, context)
    elif data == "menu_wines":
        await handle_wines(update, context)
    elif data == "menu_supermarkets":
        await handle_supermarkets(update, context)
    elif data == "menu_coupons":
        await handle_coupons(update, context)
    elif data == "menu_history":
        await handle_history(update, context)
    elif data == "menu_run_now":
        await handle_run_now(update, context)
    elif data == "menu_microsite":
        await handle_microsite(update, context)
    elif data == "menu_toggle_alerts":
        await handle_toggle_alerts(update, context)


def main():
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "SEU_TOKEN_AQUI":
        print("\n" + "=" * 60)
        print("⚠️ ATENÇÃO: TELEGRAM_BOT_TOKEN não foi configurado no .env!")
        print("=" * 60 + "\n")
        return

    # Inicializa o banco de dados SQLite
    init_db()

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(start_scheduler_job).build()

    # Handlers de comandos
    app.add_handler(CommandHandler(["start", "ajuda", "menu"], start_command))
    app.add_handler(CommandHandler("buscar", search_command))
    app.add_handler(CommandHandler("historico", handle_history))
    app.add_handler(CommandHandler("rodaragora", handle_run_now))
    app.add_handler(CommandHandler("alertas", handle_toggle_alerts))
    app.add_handler(CallbackQueryHandler(callback_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_command))

    print("🚀 Bot de Promoções de Cervejas e Vinhos (Sertãozinho) iniciado com sucesso!")
    print("⏰ Agendamento: 4 buscas diárias (08:00, 12:00, 16:00, 20:00).")
    print("💾 Banco de Dados SQLite: promotions_history.db pronto.")
    
    app.run_polling()

if __name__ == "__main__":
    main()
