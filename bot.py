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
        # --- SEÇÃO 2: SUPERMERCADOS LOCAIS & LISTA DA FAMÍLIA ---
        [
            InlineKeyboardButton("🛒 Simulador de Economia (3 Lojas)", callback_data="menu_basket"),
            InlineKeyboardButton("📸 Foto / Scanner no Mercado", callback_data="menu_scanner"),
        ],
        [
            InlineKeyboardButton("📋 Lista Básica de Supermercado", callback_data="menu_basic_basket"),
            InlineKeyboardButton("⚔️ Batalha 3 Redes", callback_data="menu_supermarkets"),
        ],
        [
            InlineKeyboardButton("📝 Minha Lista da Família", callback_data="menu_watchlist"),
            InlineKeyboardButton("🧼 Limpeza & Açougue Local", callback_data="menu_grocery"),
        ],
        [
            InlineKeyboardButton("📊 Termômetro de Preços", callback_data="menu_history"),
            InlineKeyboardButton("⚡ Rodar Busca Agora", callback_data="menu_run_now"),
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
        "🍻 *Monitor & Inteligência de Preços — Sertãozinho / SP* 🍷\n\n"
        "Seu assistente inteligente para economizar nas compras de **Bebidas (Cervejas, Vinhos)** "
        "e nos **Supermercados Locais (Savegnago, Copercana e Paulistão Atacadista)**.\n\n"
        "⚡ *Busca em Tempo Real:* Digite o nome de qualquer item (ex: `Ovos`, `Heineken`, `Picanha`, `Sabão OMO`) "
        "e o bot compara na hora as lojas da cidade!\n\n"
        "📋 *Lista Básica:* Consulte preços dos itens essenciais do dia a dia pelo botão **'Lista Básica de Supermercado'**.\n\n"
        "⏰ *Varreduras automáticas:* **3x ao dia** (08h, 13h, 19h)!\n\n"
        "👇 *Escolha uma opção ou digite o nome do produto:*"
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

async def handle_basic_basket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Exibe o menu de departamentos da Lista Básica de Supermercado em Sertãozinho."""
    query = update.callback_query
    if query:
        await query.answer()
    
    text = (
        "📋 *LISTA BÁSICA DE SUPERMERCADO & CESTA DA FAMÍLIA* 🛒\n\n"
        "Acompanhe e compare preços médios e ofertas dos itens essenciais do dia a dia "
        "entre **Savegnago, Copercana e Paulistão Atacadista** em Sertãozinho/SP.\n\n"
        "👇 *Escolha um departamento para ver os preços:* "
    )
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🥚 Ovos & Laticínios", callback_data="cat_ovos"),
            InlineKeyboardButton("🍚 Cesta Básica & Mercearia", callback_data="cat_mercearia"),
        ],
        [
            InlineKeyboardButton("🥩 Açougue & Carnes", callback_data="cat_carnes"),
            InlineKeyboardButton("🧼 Limpeza & Lavanderia", callback_data="cat_limpeza"),
        ],
        [
            InlineKeyboardButton("🍺 Bebidas & Cervejas", callback_data="cat_bebidas"),
            InlineKeyboardButton("🍷 Vinhos & Espumantes", callback_data="cat_vinhos"),
        ],
        [
            InlineKeyboardButton("🛒 Comparar Carrinho Completo", callback_data="menu_basket"),
        ],
        [
            InlineKeyboardButton("🔙 Voltar ao Menu Principal", callback_data="menu_start"),
        ]
    ])
    
    if query:
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode="Markdown")
    elif update.message:
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")

async def handle_basic_category(update: Update, context: ContextTypes.DEFAULT_TYPE, cat_key: str):
    """Exibe os itens de uma categoria específica com comparação entre Savegnago, Copercana e Paulistão."""
    query = update.callback_query
    await query.answer()
    
    from services.basic_basket import BASIC_CATALOG
    
    cat_map = {
        "cat_ovos": ("🥚 *OVOS & LATICÍNIOS*", ["ovos_30un", "ovos_vermelhos_20un", "leite_1l", "manteiga_200g", "queijo_mussarela"]),
        "cat_mercearia": ("🍚 *CESTA BÁSICA & MERCEARIA*", ["arroz_5kg", "feijao_1kg", "oleo_soja", "cafe_500g", "acucar_1kg", "molho_tomate", "macarrao_500g"]),
        "cat_carnes": ("🥩 *AÇOUGUE & CARNES*", ["picanha_kg", "contrafile_kg", "alcatra_kg", "carne_moida_kg", "frango_file_kg", "linguica_toscana_kg"]),
        "cat_limpeza": ("🧼 *LIMPEZA & LAVANDERIA*", ["sabao_omo_liquido_3l", "sabao_omo_po_1_6kg", "amaciante_downy_comfort", "detergente_ype", "papel_higienico_neve", "desinfetante_pinho_sol"]),
        "cat_bebidas": ("🍺 *BEBIDAS & CERVEJAS*", ["heineken_lata_350ml", "spaten_lata_350ml", "corona_330ml", "amstel_lata_350ml", "coca_cola_2l"]),
        "cat_vinhos": ("🍷 *VINHOS & ESPUMANTES*", ["casillero_cabernet", "concha_toro_reservado"])
    }
    
    title, item_ids = cat_map.get(cat_key, ("📋 *ITENS ESSENCIAIS*", []))
    matched_items = [it for it in BASIC_CATALOG if it["id"] in item_ids]
    
    lines = [f"{title} — Comparativo Sertãozinho:\n"]
    
    for it in matched_items:
        sav_p = it["savegnago"]["price"]
        cop_p = it["copercana"]["price"]
        pau_p = it["paulistao"]["price"]
        
        prices = [("Savegnago", sav_p), ("Copercana", cop_p), ("Paulistão Atacadista", pau_p)]
        prices.sort(key=lambda x: x[1])
        best_store, best_price = prices[0]
        
        lines.append(
            f"📌 *{it['name']}*\n"
            f"  🏪 Savegnago: R$ {sav_p:.2f}\n"
            f"  🏪 Copercana: R$ {cop_p:.2f}\n"
            f"  🏪 Paulistão: R$ {pau_p:.2f}\n"
            f"  👉 🏆 *Mais Barato:* **{best_store}** (R$ {best_price:.2f})\n"
        )
        
    lines.append("💡 _Para vigiar ou comparar sua lista personalizada, use /vigiar ou /carrinho._")
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Ver Outros Departamentos", callback_data="menu_basic_basket")],
        [InlineKeyboardButton("🛒 Comparar Carrinho", callback_data="menu_basket")],
        [InlineKeyboardButton("🔙 Menu Principal", callback_data="menu_start")]
    ])
    
    await query.edit_message_text("\n".join(lines), reply_markup=keyboard, parse_mode="Markdown")

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para busca sob demanda em tempo real com inteligência de intenção."""
    if context.args:
        query_text = " ".join(context.args)
    elif update.message and update.message.text:
        query_text = update.message.text.strip()
    else:
        return
        
    if query_text.startswith("/"):
        return

    wait_msg = await update.message.reply_text(
        f"⚡ *Buscando em tempo real nos supermercados e lojas para:* `{query_text}`...",
        parse_mode="Markdown"
    )
    
    # Executa a busca em tempo real sob demanda
    from services.realtime_search import search_realtime_all_stores
    live_res = search_realtime_all_stores(query_text)
    
    classification = live_res["classification"]
    battle = live_res["battle"]
    history_records = live_res["history_records"]
    store_links = live_res["store_links"]
    
    is_beverage = classification["type"] == "BEBIDA"
    
    if is_beverage:
        msg_lines = [f"🍻 *RESULTADO DE BEBIDAS:* `{query_text}`\n"]
    else:
        msg_lines = [
            f"🛒 *RESULTADO LOCAL (SERTÃOZINHO):* `{query_text}`",
            f"📂 *Setor:* _{classification['category_name']}_\n"
        ]
    
    # 1. Batalha Direta Supermercados de Sertãozinho (Savegnago vs Copercana vs Paulistão)
    has_local = battle.get("savegnago") or battle.get("copercana") or battle.get("paulistao")
    if has_local:
        msg_lines.append("⚔️ *BATALHA DE PREÇOS EM SERTÃOZINHO:*")
        if battle.get("savegnago"):
            msg_lines.append(f"  🏪 *Savegnago:* R$ {battle['savegnago']['price']:.2f}")
        if battle.get("copercana"):
            msg_lines.append(f"  🏪 *Copercana:* R$ {battle['copercana']['price']:.2f}")
        if battle.get("paulistao"):
            msg_lines.append(f"  🏪 *Paulistão Atacadista:* R$ {battle['paulistao']['price']:.2f}")
            
        if battle.get("winner") and battle["winner"] != "Empate":
            diff = battle.get('diff_amount', 0.0)
            diff_text = f" (Economia de R$ {diff:.2f})" if diff > 0 else ""
            msg_lines.append(f"  👉 🏆 *Mais Barato:* **{battle['winner']}**{diff_text}\n")
        elif battle.get("winner") == "Empate":
            msg_lines.append("  👉 🤝 *Mesmo preço nas redes locais!*\n")
        else:
            msg_lines.append("")

    # 2. Avaliação de Preço e Histórico
    if history_records:
        msg_lines.append("📊 *TERMÔMETRO DE PREÇOS:*")
        for hr in history_records:
            intel = analyze_price_quality(
                current_price=hr["current_price"],
                historical_min=hr["min_price"],
                historical_avg=hr["avg_price"]
            )
            msg_lines.append(
                f"  {intel['emoji']} *{hr['name']}*\n"
                f"  💰 Preço Atual: *R$ {hr['current_price']:.2f}* | Média: R$ {hr['avg_price']:.2f}\n"
                f"  🏷️ *Avaliação:* {intel['verdict']}\n"
            )
        msg_lines.append("")
        
    # 3. Links Diretos de Compra & Atendimento
    msg_lines.append("🛒 *ONDE ENCONTRAR / PEDIR:*")
    for idx, item in enumerate(store_links[:4], start=1):
        line = (
            f"*{idx}. {item['title']}*\n"
            f"  🏷️ {item['price']} • {item['free_shipping']}\n"
            f"  🔗 [Acessar {item['store']}]({item['link']})\n"
        )
        msg_lines.append(line)
        
    back_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"➕ Vigiar Preço de '{query_text[:18]}'", callback_data=f"watch_quick:{query_text}")],
        [InlineKeyboardButton("📋 Ver Lista Básica Completa", callback_data="menu_basic_basket")],
        [InlineKeyboardButton("🛒 Comparar Carrinho da Família", callback_data="menu_basket")],
        [InlineKeyboardButton("🔙 Voltar ao Menu Principal", callback_data="menu_start")]
    ])
    
    await wait_msg.edit_text(
        "\n".join(msg_lines),
        reply_markup=back_keyboard,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )



async def handle_basket_comparison(update: Update, context: ContextTypes.DEFAULT_TYPE, preset: str = None):
    """Calcula o comparativo de economia de toda a lista de compras no Savegnago vs Copercana vs Paulistão Atacadista."""
    query = update.callback_query
    if query:
        await query.answer()
        chat_id = update.effective_chat.id
        if not preset and query.data.startswith("basket_preset:"):
            preset = query.data.split("basket_preset:", 1)[1]
    else:
        chat_id = update.effective_chat.id

    from database import get_watchlist
    from services.supermarket_comparator import compare_shopping_basket
    from services.basic_basket import BASIC_CATALOG
    
    preset_title = "Minha Lista Personalizada"
    if preset == "cesta":
        preset_title = "🍚 Cesta Essencial da Família"
        items = [{"item_name": it["name"]} for it in BASIC_CATALOG if it.get("preset_basket")]
    elif preset == "churrasco":
        preset_title = "🥩 Churrasco de Fim de Semana"
        items = [{"item_name": it["name"]} for it in BASIC_CATALOG if it.get("preset_bbq")]
    elif preset == "limpeza":
        preset_title = "🧼 Faxina & Higiene Completa"
        items = [{"item_name": it["name"]} for it in BASIC_CATALOG if it.get("preset_cleaning")]
    else:
        watchlist = get_watchlist(chat_id=chat_id)
        if not watchlist:
            items = [{"item_name": it["name"]} for it in BASIC_CATALOG if it.get("preset_basket")]
            preset_title = "🍚 Cesta Essencial (Padrão)"
        else:
            items = watchlist
            preset_title = "📝 Sua Lista de Vigia"

    res = compare_shopping_basket(items)
    total_paulistao = res.get("total_paulistao", 0.0)
    
    lines = [
        f"🛒 *SIMULADOR DE ECONOMIA:* `{preset_title}` ⚔️\n",
        f"Simulação para **{res['total_items']} itens** em Sertãozinho/SP:\n",
        f"🏪 **Total Savegnago:** `R$ {res['total_savegnago']:.2f}`",
        f"🏪 **Total Copercana:** `R$ {res['total_copercana']:.2f}`",
        f"🏪 **Total Paulistão Atacadista:** `R$ {total_paulistao:.2f}`",
        f"✨ **Carrinho Mix (Comprando no Menor Preço):** `R$ {res['total_mixed']:.2f}`\n"
    ]
    
    if res["winner"] and res["winner"] != "Empate":
        lines.append(
            f"🏆 *REDE MAIS ECONÔMICA:* **{res['winner']}**\n"
            f"💰 *Economia em loja única:* **R$ {res['single_store_savings']:.2f} ({res['single_store_savings_pct']}%)**\n"
            f"💡 *Economia máxima dividindo compras:* **R$ {res['split_store_savings']:.2f}**\n"
        )
    else:
        lines.append("🤝 **Empate técnico entre as redes!**\n")
        
    lines.append("📋 *ONDE COMPRAR CADA ITEM (MELHOR PREÇO):*")
    for it in res["items"][:6]:
        lines.append(
            f"• *{it['item_name'][:32]}*\n"
            f"  👉 🏆 Comprar no **{it['best_store']}** por *R$ {it['best_price']:.2f}*"
        )
        
    if len(res["items"]) > 6:
        lines.append(f"\n_...e mais {len(res['items']) - 6} itens calculados no total!_")

    lines.append("\n👇 *Simular outros pacotes de compra:*")

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🍚 Cesta Essencial", callback_data="basket_preset:cesta"),
            InlineKeyboardButton("🥩 Churrasco", callback_data="basket_preset:churrasco"),
        ],
        [
            InlineKeyboardButton("🧼 Faxina & Limpeza", callback_data="basket_preset:limpeza"),
            InlineKeyboardButton("📝 Minha Lista", callback_data="menu_watchlist"),
        ],
        [
            InlineKeyboardButton("🌐 Ver Simulador Interativo no Microsite", callback_data="menu_microsite"),
        ],
        [
            InlineKeyboardButton("🔙 Voltar ao Menu Principal", callback_data="menu_start")
        ]
    ])

    if query:
        await query.edit_message_text(
            "\n".join(lines),
            reply_markup=keyboard,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
    elif update.message:
        await update.message.reply_text(
            "\n".join(lines),
            reply_markup=keyboard,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )

async def handle_scanner_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu explicativo do scanner de fotos e código de barras no mercado."""
    query = update.callback_query
    if query:
        await query.answer()
        
    text = (
        "📸 *COMPARADOR DE PREÇOS NO SUPERMERCADO* 🛒\n\n"
        "Está no corredor do mercado e quer saber se o preço está realmente bom?\n\n"
        "1️⃣ **Envie uma Foto pelo Telegram:**\n"
        "   Tire uma foto do produto ou da etiqueta de preço e envie aqui com o nome e valor como legenda (ex: `Heineken 350ml 5.19` ou `Sabão OMO 36.90`).\n\n"
        "2️⃣ **Scanner de Código de Barras (Câmera ao Vivo):**\n"
        "   Acesse o Microsite Web e use a câmera do celular para ler o código EAN-13 da embalagem em segundos!\n\n"
        "3️⃣ **Busca Instantânea por Texto:**\n"
        "   Ou apenas digite o nome de qualquer item no chat para receber a cotação de Sertãozinho na hora."
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Abrir Leitor de Câmera no Microsite", callback_data="menu_microsite")],
        [InlineKeyboardButton("🛒 Simular Carrinho de Economia", callback_data="menu_basket")],
        [InlineKeyboardButton("🔙 Menu Principal", callback_data="menu_start")]
    ])
    
    if query:
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode="Markdown")
    elif update.message:
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")

async def handle_photo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa fotos enviadas pelo usuário (produto, etiqueta de preço ou código de barras no mercado)."""
    caption = (update.message.caption or "").strip()
    
    if caption:
        query_text = caption
        from services.realtime_search import search_realtime_all_stores
        live_res = search_realtime_all_stores(query_text)
        battle = live_res["battle"]
        
        # Tenta extrair preço visto na loja
        parts = query_text.split()
        seen_price = None
        for p in reversed(parts):
            p_clean = p.replace("R$", "").replace("$", "").replace(",", ".").strip()
            try:
                seen_price = float(p_clean)
                break
            except ValueError:
                continue
                
        lines = [
            "📸 *ANÁLISE DE PRODUTO NO MERCADO:*\n",
            f"🔎 *Item identificado:* `{query_text}`\n"
        ]
        
        if seen_price:
            lines.append(f"🏷️ *Preço visto na gôndola:* `R$ {seen_price:.2f}`\n")
            
        lines.append("⚔️ *PREÇOS NAS REDES DE SERTÃOZINHO:*")
        sav_p = battle.get("savegnago", {}).get("price") if battle.get("savegnago") else None
        cop_p = battle.get("copercana", {}).get("price") if battle.get("copercana") else None
        pau_p = battle.get("paulistao", {}).get("price") if battle.get("paulistao") else None
        
        if sav_p: lines.append(f"  🏪 *Savegnago:* R$ {sav_p:.2f}")
        if cop_p: lines.append(f"  🏪 *Copercana:* R$ {cop_p:.2f}")
        if pau_p: lines.append(f"  🏪 *Paulistão Atacadista:* R$ {pau_p:.2f}")
        
        if seen_price and (sav_p or cop_p or pau_p):
            local_prices = [p for p in [sav_p, cop_p, pau_p] if p]
            min_local = min(local_prices)
            if seen_price < min_local:
                diff = min_local - seen_price
                lines.append(f"\n🟢 *EXCELENTE OPORTUNIDADE!* O preço de R$ {seen_price:.2f} nesta loja está mais barato que toda a concorrência (você economiza R$ {diff:.2f})! Pode comprar! 🚀")
            elif seen_price == min_local:
                lines.append(f"\n🟡 *BOM PREÇO!* Empatado com o menor preço praticado na cidade (R$ {min_local:.2f}).")
            else:
                diff = seen_price - min_local
                lines.append(f"\n🔴 *ATENÇÃO:* Você encontra mais barato por R$ {min_local:.2f} em outra rede de Sertãozinho (Economia de R$ {diff:.2f})!")
        elif battle.get("winner"):
            lines.append(f"\n👉 🏆 *Mais Barato na Cidade:* **{battle['winner']}**")
            
        back_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"➕ Vigiar '{query_text[:18]}'", callback_data=f"watch_quick:{query_text}")],
            [InlineKeyboardButton("🛒 Comparar Carrinho Completo", callback_data="menu_basket")],
            [InlineKeyboardButton("🔙 Menu Principal", callback_data="menu_start")]
        ])
        
        await update.message.reply_text("\n".join(lines), reply_markup=back_keyboard, parse_mode="Markdown")
    else:
        text = (
            "📸 *FOTO RECEBIDA DO MERCADO!* 🛒\n\n"
            "Para comparar na hora com **Savegnago, Copercana e Paulistão Atacadista**, "
            "envie a foto com uma **legenda** contendo o nome do item e o valor visto na etiqueta!\n\n"
            "👉 *Exemplos de Legenda:*\n"
            "• `Heineken Lata 350ml 5.19`\n"
            "• `Sabão OMO Líquido 3L 36.90`\n"
            "• `Picanha Friboi 62.00`\n"
            "• `Ovos Brancos 30un 18.50`\n\n"
            "⚡ Ou escolha uma consulta rápida abaixo:"
        )
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🍺 Heineken", callback_data="cat_bebidas"),
                InlineKeyboardButton("🧼 Sabão OMO", callback_data="cat_limpeza"),
            ],
            [
                InlineKeyboardButton("🥩 Picanha", callback_data="cat_carnes"),
                InlineKeyboardButton("🥚 Ovos", callback_data="cat_ovos"),
            ],
            [
                InlineKeyboardButton("🌐 Abrir Scanner no Microsite Web", callback_data="menu_microsite"),
                InlineKeyboardButton("🔙 Menu Principal", callback_data="menu_start")
            ]
        ])
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")


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
    elif data == "menu_basic_basket":
        await handle_basic_basket(update, context)
    elif data.startswith("cat_"):
        await handle_basic_category(update, context, data)
    elif data.startswith("watch_quick:"):
        item_name = data.split("watch_quick:", 1)[1]
        chat_id = update.effective_chat.id
        add_to_watchlist(item_name=item_name, chat_id=chat_id)
        await query.answer(f"✅ '{item_name}' adicionado à sua lista!", show_alert=True)
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
    elif data == "menu_basket" or data.startswith("basket_preset:"):
        await handle_basket_comparison(update, context)
    elif data == "menu_scanner":
        await handle_scanner_menu(update, context)
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
    app.add_handler(CommandHandler(["basica", "cesta", "produtos", "essenciais"], handle_basic_basket))
    app.add_handler(CommandHandler(["vigiar", "adicionar"], watch_command))
    app.add_handler(CommandHandler(["minhalista", "lista"], handle_watchlist))
    app.add_handler(CommandHandler(["carrinho", "comparar", "economia", "simulador"], handle_basket_comparison))
    app.add_handler(CommandHandler(["scanner", "foto", "camera"], handle_scanner_menu))
    app.add_handler(CommandHandler(["remover", "deletar"], remove_watch_command))
    app.add_handler(CommandHandler("buscar", search_command))
    app.add_handler(CommandHandler("historico", handle_history))
    app.add_handler(CommandHandler("rodaragora", handle_run_now))
    app.add_handler(CommandHandler("alertas", handle_toggle_alerts))
    app.add_handler(CallbackQueryHandler(callback_router))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_command))

    print("🚀 Bot de Promoções de Bebidas & Mercado (Sertãozinho) iniciado com sucesso!")
    print("⏰ Agendamento: 3 buscas diárias (08:00, 13:00, 19:00).")
    print("💾 Banco de Dados SQLite: promotions_history.db pronto.")
    
    app.run_polling()


if __name__ == "__main__":
    main()


