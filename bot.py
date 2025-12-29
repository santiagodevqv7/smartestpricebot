from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from telegram.request import HTTPXRequest

from input_resolver import resolve_input
from price_comparator import compare_prices
from amazon_utils import asin_to_title

import urllib.parse

def build_purchase_url(store: str, query: str, link: str | None):
    if link:
        return link

    q = urllib.parse.quote_plus(query)

    fallback = {
        "Amazon": f"https://www.amazon.com/s?k={q}",
        "Walmart": f"https://www.walmart.com/search?q={q}",
        "Best Buy": f"https://www.bestbuy.com/site/searchpage.jsp?st={q}",
        "eBay": f"https://www.ebay.com/sch/i.html?_nkw={q}",
        "Target": f"https://www.target.com/s?searchTerm={q}",
        "Swappa": f"https://swappa.com/search?q={q}",
        "Back Market": f"https://www.backmarket.com/en-us/search?q={q}",
    }

    return fallback.get(store)

import os
BOT_TOKEN = os.getenv("BOT_TOKEN")

request = HTTPXRequest(connect_timeout=20, read_timeout=20)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    resolved = resolve_input(user_text)

    # 1. Resolver query final
    query = resolved["query"]

    if resolved["store"] == "amazon" and len(query) == 10:
        title = asin_to_title(query)
        if title:
            query = title

    # 2. Buscar precios
    offers = compare_prices(query)

    if not offers:
        await update.message.reply_text("❌ No se encontraron precios.")
        return

    # 3. Filtrar tiendas permitidas (MVP)
    ALLOWED_STORES = {
        "Amazon",
        "Walmart",
        "Best Buy",
        "Target",
        "eBay",
        "Swappa",
        "Back Market"
    }

    offers = [
        o for o in offers
        if o.get("price") is not None
        and o.get("store") in ALLOWED_STORES
    ]

    if not offers:
        await update.message.reply_text("❌ No hay resultados relevantes.")
        return

    # 4. Ordenar por precio (menor a mayor)
    offers.sort(key=lambda x: x["price"])

    best = offers[0]
    top3 = offers[:3]

    # 5. Build final message (INITIALIZE msg FIRST)
    msg = "🛒 *SmartestPriceBot*\n"
    msg += f"🔍 Product: *{query.title()}*\n\n"

    msg += "🏆 *Best price found*\n"
    
    best_url = build_purchase_url(
    best["store"],
    query,
    best.get("link")
)

    msg += f"🥇 *{best['store']}* — *${best['price']}*\n"
    if best_url:
        msg += f"👉 [Buy here]({best_url})\n\n"
    else:
        msg += "\n"

    msg += "📊 *Quick comparison*\n"
    for o in top3:

        url = build_purchase_url(o["store"], query, o.get("link"))
        if url:
            msg += f"• {o['store']} — ${o['price']} ([link]({url}))\n"
        else:
            msg += f"• {o['store']} — ${o['price']}\n"

    await update.message.reply_text(msg, parse_mode="Markdown")
 
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
)

print("🤖 Bot corriendo...")
app.run_polling()
