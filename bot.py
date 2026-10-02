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
from services.price_intelligence import analyze_price_quality
from database import (
    init_db,
    add_subscriber,
    remove_subscriber,
    get_subscribers,
    get_recent_price_drops,
    get_product_history,
    add_to_watchlist,
    get_watchlist,
    remove_from_watchlist,
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
        InlineKeyboardButton("🔕 Desativar Alertas", callback_data="menu_toggle_alerts")
        if is_subscribed else
        InlineKeyboardButton("🔔 Ativar Alertas (3x/dia)", callback_data="menu_toggle_alerts")
    )
    
    keyboard = [
        # --- SEÇÃO 1: BEBIDAS & ADEGA (FOCO PRINCIPAL) ---
        [
            InlineKeyboardButton("🍺 Cervejas em Oferta", callback_data="menu_beers"),
            InlineKeyboardButton("🍷 Vinhos & Espumantes", callback_data="menu_wines"),
        ],
        [
            InlineKeyboardButton("🎟️ Cupons & Zé Delivery", callback_data="menu_coupons"),
            InlineKeyboardButton("🍇 Clubes Wine & Evino", callback_data="menu_wines"),
        ],
        # --- SEÇÃO 2: SUPERMERCADOS LOCAIS & FAMÍLIA ---
        [
            InlineKeyboardButton("⚔️ Batalha: Savegnago vs Copercana", callback_data="menu_supermarkets"),
        ],
        [
            InlineKeyboardButton("📝 Minha Lista de Compras", callback_data="menu_watchlist"),
            InlineKeyboardButton("🛒 Comparar Carrinho / Economia", callback_data="menu_basket"),
        ],
        [
            InlineKeyboardButton("🧼 Limpeza & Açougue Local", callback_data="menu_grocery"),
            InlineKeyboardButton("📊 Termômetro de Preços", callback_data="menu_history"),
        ],
        # --- UTILITÁRIOS ---
        [
            InlineKeyboardButton("🌐 Ver Microsite Web", callback_data="menu_microsite"),
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
        "🍻 *Monitor de Promoções — Sertãozinho / SP* 🍷\n\n"
        "Seu assistente para rastrear as melhores ofertas de **Bebidas (Cervejas, Vinhos & Destilados)** "
        "e comparar preços entre os **Supermercados Locais (Savegnago vs Copercana)**.\n\n"
        "⚡ *Busca em Tempo Real:* Digite o nome de qualquer produto para fazer uma varredura na hora em todas as lojas!\n\n"
        "⏰ *Varreduras automáticas:* **3x ao dia** (08h, 13h, 19h) com alertas de oportunidade!\n\n"
        "👇 *Escolha um setor abaixo ou envie o nome de um produto:*"
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
    """Exibe o histórico recente de preços e promoções registradas com análise inteligente."""
    query = update.callback_query
    await query.answer()
    
    promos = get_recent_price_drops(limit=8)
    msg_lines = ["📊 *TERMÔMETRO & HISTÓRICO DE PREÇOS:*\n"]
    
    if promos:
        for p in promos:
            orig = f"~R$ {p['original_price']:.2f}~ " if p.get("original_price") else ""
            intel = analyze_price_quality(
                current_price=p["price"],
                original_price=p.get("original_price"),
                historical_avg=p.get("original_price") or (p["price"] * 1.15)
            )
            msg_lines.append(
                f"{intel['emoji']} *{p['name']}*\n"
                f"  💰 Preço: {orig}*R$ {p['price']:.2f}* (-{p['discount_pct']:.0f}%)\n"
                f"  🏷️ *Avaliação:* _{intel['verdict']}_\n"
                f"  💡 _{intel['advice']}_\n"
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

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para busca sob demanda em tempo real (Savegnago, Copercana, Amazon, Mercado Livre)"""
    if context.args:
        query_text = " ".join(context.args)
    elif update.message and update.message.text:
        query_text = update.message.text.strip()
    else:
        return
        
    if query_text.startswith("/"):
        return

    wait_msg = await update.message.reply_text(
        f"⚡ *Buscando em tempo real no Savegnago, Copercana, Amazon e ML para:* `{query_text}`...",
        parse_mode="Markdown"
    )
    
    # Executa a busca em tempo real sob demanda
    from services.realtime_search import search_realtime_all_stores
    live_res = search_realtime_all_stores(query_text)
    
    battle = live_res["battle"]
    history_records = live_res["history_records"]
    results = live_res["marketplace_links"]
    
    msg_lines = [f"🎯 *RESULTADO EM TEMPO REAL:* `{query_text}`\n"]
    
    # 1. Batalha Direta Supermercados de Sertãozinho
    if battle.get("savegnago") or battle.get("copercana"):
        msg_lines.append("⚔️ *BATALHA EM SERTÃOZINHO:*")
        if battle.get("savegnago"):
            msg_lines.append(f"🏪 *Savegnago:* R$ {battle['savegnago']['price']:.2f}")
        if battle.get("copercana"):
            msg_lines.append(f"🏪 *Copercana:* R$ {battle['copercana']['price']:.2f}")
            
        if battle.get("winner") and battle["winner"] != "Empate":
            msg_lines.append(f"🏆 *Mais Barato:* **{battle['winner']}** (Economia de R$ {battle['diff_amount']:.2f})\n")
        elif battle.get("winner") == "Empate":
            msg_lines.append("🤝 *Mesmo preço nas duas redes!*\n")
        else:
            msg_lines.append("")

    # 2. Avaliação de Preço
    if history_records:
        msg_lines.append("📊 *HISTÓRICO & AVALIAÇÃO:*")
        for hr in history_records:
            intel = analyze_price_quality(
                current_price=hr["current_price"],
                historical_min=hr["min_price"],
                historical_avg=hr["avg_price"]
            )
            msg_lines.append(
                f"{intel['emoji']} *{hr['name']}*\n"
                f"  💰 Preço Atual: *R$ {hr['current_price']:.2f}* | Média: R$ {hr['avg_price']:.2f}\n"
                f"  🏷️ *Termômetro:* {intel['verdict']}\n"
            )
        msg_lines.append("")
        
    # 3. Links Rápidos de Compra
    msg_lines.append("🛒 *LINKS DE COMPRA DIRETA & ENTREGA:*")
    for idx, item in enumerate(results[:3], start=1):
        line = (
            f"*{idx}. {item['title']}*\n"
            f"💰 {item['price']}\n"
            f"{item['free_shipping']} {item['is_full']}\n"
            f"🔗 [Ver no {item['store']}]({item['link']})\n"
        )
        msg_lines.append(line)
        
    back_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Comparar Carrinho da Família", callback_data="menu_basket")],
        [InlineKeyboardButton("🔙 Voltar ao Menu Principal", callback_data="menu_start")]
    ])
    
    await wait_msg.edit_text(
        "\n".join(msg_lines),
        reply_markup=back_keyboard,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )


async def handle_basket_comparison(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Calcula o comparativo de economia de toda a lista de compras no Savegnago vs Copercana."""
    query = update.callback_query
    if query:
        await query.answer()
        chat_id = update.effective_chat.id
    else:
        chat_id = update.effective_chat.id

    from database import get_watchlist
    from services.supermarket_comparator import compare_shopping_basket
    
    watchlist = get_watchlist(chat_id=chat_id)
    if not watchlist:
        watchlist = [
            {"item_name": "Heineken"},
            {"item_name": "Spaten"},
            {"item_name": "Casillero"},
            {"item_name": "Picanha"},
            {"item_name": "OMO"}
        ]
        is_sample = True
    else:
        is_sample = False

    res = compare_shopping_basket(watchlist)
    
    lines = [
        "🛒 *COMPARADOR DE CARRINHO: SAVEGNAGO vs COPERCANA* ⚔️\n",
        f"Simulação para **{res['total_items']} itens** da lista:\n",
        f"🏪 **Total no Savegnago:** `R$ {res['total_savegnago']:.2f}`",
        f"🏪 **Total no Copercana:** `R$ {res['total_copercana']:.2f}`",
        f"✨ **Total Comprando Fracionado (Melhor Preço):** `R$ {res['total_mixed']:.2f}`\n"
    ]
    
    if res["winner"] != "Empate":
        lines.append(
            f"🏆 *REDE MAIS ECONÔMICA:* **{res['winner']}**\n"
            f"💰 *Economia em loja única:* **R$ {res['single_store_savings']:.2f} ({res['single_store_savings_pct']}%)**\n"
            f"💡 *Economia dividindo os itens:* **R$ {res['split_store_savings']:.2f}**\n"
        )
    else:
        lines.append("🤝 **Empate técnico entre as duas redes!**\n")
        
    lines.append("📋 *DETALHAMENTO POR PRODUTO:*")
    for it in res["items"][:5]:
        lines.append(
            f"• *{it['item_name']}:*\n"
            f"  Savegnago: R$ {it['price_savegnago']:.2f} | Copercana: R$ {it['price_copercana']:.2f}\n"
            f"  👉 Mais barato no *{it['best_store']}*"
        )
        
    if is_sample:
        lines.append("\n_*(Exemplo com itens padrão. Adicione os seus com /vigiar para uma simulação personalizada!)*_")

    back_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Ver Minha Lista", callback_data="menu_watchlist")],
        [InlineKeyboardButton("🔙 Voltar ao Menu Principal", callback_data="menu_start")]
    ])

    if query:
        await query.edit_message_text(
            "\n".join(lines),
            reply_markup=back_keyboard,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
    elif update.message:
        await update.message.reply_text(
            "\n".join(lines),
            reply_markup=back_keyboard,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )


async def handle_run_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Executa a varredura nos sites imediatamente sob demanda."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("⏳ *Executando bots de busca em tempo real (Savegnago, Mercado Livre, Amazon, Wine)...*", parse_mode="Markdown")
    
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
        [InlineKeyboardButton("📊 Ver Histórico & Termômetro", callback_data="menu_history")],
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


async def handle_watchlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Exibe a lista de produtos vigiados pela família."""
    query = update.callback_query
    if query:
        await query.answer()
        chat_id = update.effective_chat.id
    else:
        chat_id = update.effective_chat.id

    watchlist = get_watchlist(chat_id=chat_id)
    
    msg_lines = ["📝 *LISTA DE MONITORAMENTO DA FAMÍLIA* 👨‍👩‍👧\n"]
    
    if watchlist:
        for idx, item in enumerate(watchlist, start=1):
            target_str = f" (Alvo: R$ {item['target_max_price']:.2f})" if item.get('target_max_price') else ""
            line = f"*{idx}. {item['item_name']}*{target_str}"
            
            if item.get("best_match"):
                bm = item["best_match"]
                disc = f" (-{bm['discount_pct']:.0f}%)" if bm.get('discount_pct') else ""
                line += f"\n  💰 Melhor Preço Atual: *R$ {bm['price']:.2f}*{disc}\n  🏪 {bm['store']} | 🔗 [Ver Oferta]({bm['link']})"
            else:
                line += "\n  🔍 _Aguardando primeira varredura nos supermercados._"
                
            msg_lines.append(line + "\n")
    else:
        msg_lines.append(
            "Sua lista ainda está vazia!\n\n"
            "💡 *Como adicionar itens:*\n"
            "Envie no chat: `/vigiar <nome do produto> [preço alvo opcional]`\n\n"
            "Exemplos:\n"
            "👉 `/vigiar Sabão Líquido Omo 3L`\n"
            "👉 `/vigiar Picanha 59.90`\n"
            "👉 `/vigiar Amaciante Downy 1.5L`\n"
            "👉 `/vigiar Azeite Extra Virgem`"
        )
        
    msg_lines.append("\n🗑️ Para remover um item, use: `/remover <nome do produto>`")

    back_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Como Adicionar Itens", callback_data="menu_how_to_watch")],
        [InlineKeyboardButton("🔙 Voltar ao Menu Principal", callback_data="menu_start")]
    ])
    
    if query:
        await query.edit_message_text(
            "\n".join(msg_lines),
            reply_markup=back_keyboard,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
    elif update.message:
        await update.message.reply_text(
            "\n".join(msg_lines),
            reply_markup=back_keyboard,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )

async def handle_grocery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Exibe ofertas de Limpeza, Açougue e Mercearia dos mercados."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("🔍 *Buscando ofertas de Limpeza e Açougue em Sertãozinho...*", parse_mode="Markdown")
    
    from database import get_all_products_with_intelligence
    all_prods = get_all_products_with_intelligence()
    
    grocery_items = [p for p in all_prods if p.get("category") in ["limpeza", "acougue", "mercearia"]]
    
    msg_lines = ["🧼 *DESTAQUES DE LIMPEZA, AÇOUGUE & MERCADO:* 🥩\n"]
    
    if grocery_items:
        for p in grocery_items[:7]:
            icon = "🧼" if p["category"] == "limpeza" else ("🥩" if p["category"] == "acougue" else "☕")
            orig = f"~R$ {p['original_price']:.2f}~ " if p.get("original_price") else ""
            disc = f" (-{p['discount_pct']:.0f}%)" if p.get("discount_pct") else ""
            msg_lines.append(
                f"{icon} *{p['name']}*\n"
                f"  💰 Preço: {orig}*R$ {p['current_price']:.2f}*{disc}\n"
                f"  🏪 {p['store']} | 🔗 [Ver Oferta]({p['link']})\n"
            )
    else:
        msg_lines.append("Nenhum item carregado no momento. Clique em '⚡ Rodar Busca Agora'!")
        
    back_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Adicionar à Lista da Família", callback_data="menu_watchlist")],
        [InlineKeyboardButton("🔙 Voltar ao Menu Principal", callback_data="menu_start")]
    ])
    
    await query.edit_message_text(
        "\n".join(msg_lines),
        reply_markup=back_keyboard,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

async def watch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /vigiar <produto> [preco_alvo]"""
    if not context.args:
        await update.message.reply_text(
            "⚠️ *Como usar o comando /vigiar:*\n\n"
            "Envie: `/vigiar <nome do produto> [preço alvo opcional]`\n\n"
            "Exemplos:\n"
            "👉 `/vigiar Sabão Líquido Omo 3L 39.90`\n"
            "👉 `/vigiar Picanha Savegnago 60.00`\n"
            "👉 `/vigiar Papel Neve`",
            parse_mode="Markdown"
        )
        return
        
    chat_id = update.effective_chat.id
    raw_text = " ".join(context.args)
    
    # Tenta extrair preço alvo se a última palavra for um número
    parts = raw_text.split()
    target_price = None
    if len(parts) > 1:
        last_part = parts[-1].replace(",", ".")
        try:
            target_price = float(last_part)
            item_name = " ".join(parts[:-1])
        except ValueError:
            item_name = raw_text
    else:
        item_name = raw_text

    add_to_watchlist(item_name=item_name, target_max_price=target_price, chat_id=chat_id)
    
    price_info = f" com preço alvo de *R$ {target_price:.2f}*" if target_price else ""
    text = (
        f"✅ *Item adicionado à Lista da Família!* 👨‍👩‍👧\n\n"
        f"📌 *Produto:* `{item_name}`{price_info}\n\n"
        f"O robô vigiará o **Savegnago, Copercana, Amazon e Mercado Livre** 4x ao dia e avisará sempre que encontrar uma boa oferta!"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Ver Minha Lista", callback_data="menu_watchlist")],
        [InlineKeyboardButton("⚡ Rodar Busca Agora", callback_data="menu_run_now")]
    ])
    
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")

async def remove_watch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /remover <produto>"""
    if not context.args:
        await update.message.reply_text("Envie: `/remover <nome do produto>` para tirar da lista.", parse_mode="Markdown")
        return
        
    chat_id = update.effective_chat.id
    item_name = " ".join(context.args)
    removed = remove_from_watchlist(item_name, chat_id=chat_id)
    
    if removed:
        await update.message.reply_text(f"🗑️ *'{item_name}'* foi removido da sua lista com sucesso.", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❓ Não encontrei *'{item_name}'* na sua lista.", parse_mode="Markdown")

async def handle_how_to_watch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = (
        "💡 *COMO USAR A LISTA DA FAMÍLIA* 👨‍👩‍👧\n\n"
        "Qualquer pessoa da família pode adicionar itens essenciais para o robô vigiar nos supermercados de Sertãozinho e na Amazon:\n\n"
        "👉 `/vigiar Sabão Líquido Omo 3L 39.90`\n"
        "👉 `/vigiar Picanha 59.90`\n"
        "👉 `/vigiar Amaciante Downy`\n"
        "👉 `/vigiar Café Pilão 500g 18.00`\n\n"
        "O robô pesquisará nas 4 rodadas diárias (08h, 12h, 16h, 20h) e notificará no chat quando houver oferta!"
    )
    
    back_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Ver Minha Lista", callback_data="menu_watchlist")],
        [InlineKeyboardButton("🔙 Voltar ao Menu Principal", callback_data="menu_start")]
    ])
    
    await query.edit_message_text(text, reply_markup=back_keyboard, parse_mode="Markdown")

async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Roteador para os botões inline"""
    query = update.callback_query
    data = query.data
    
    if data == "menu_start":
        await start_command(update, context)
    elif data == "menu_watchlist":
        await handle_watchlist(update, context)
    elif data == "menu_grocery":
        await handle_grocery(update, context)
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
    elif data == "menu_how_to_watch":
        await handle_how_to_watch(update, context)
    elif data == "menu_basket":
        await handle_basket_comparison(update, context)
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
    app.add_handler(CommandHandler(["vigiar", "adicionar"], watch_command))
    app.add_handler(CommandHandler(["minhalista", "lista"], handle_watchlist))
    app.add_handler(CommandHandler(["carrinho", "comparar", "economia"], handle_basket_comparison))
    app.add_handler(CommandHandler(["remover", "deletar"], remove_watch_command))
    app.add_handler(CommandHandler("buscar", search_command))
    app.add_handler(CommandHandler("historico", handle_history))
    app.add_handler(CommandHandler("rodaragora", handle_run_now))
    app.add_handler(CommandHandler("alertas", handle_toggle_alerts))
    app.add_handler(CallbackQueryHandler(callback_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_command))

    print("🚀 Bot de Promoções de Bebidas & Mercado (Sertãozinho) iniciado com sucesso!")
    print("⏰ Agendamento: 4 buscas diárias (08:00, 12:00, 16:00, 20:00).")
    print("💾 Banco de Dados SQLite: promotions_history.db pronto.")
    
    app.run_polling()


if __name__ == "__main__":
    main()

