from telegram.ext import Updater, MessageHandler, Filters

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

def handle_message(update, context):
    user_text = update.message.text
    resolved = resolve_input(user_text)

    query = resolved["query"]

    if resolved["store"] == "amazon" and len(query) == 10:
        title = asin_to_title(query)
        if title:
            query = title

    offers = compare_prices(query)

    if not offers:
        update.message.reply_text("❌ No prices found.")
        return

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
        update.message.reply_text("❌ No relevant results.")
        return

    offers.sort(key=lambda x: x["price"])

    best = offers[0]
    top3 = offers[:3]

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

    update.message.reply_text(msg, parse_mode="Markdown")

updater = Updater(BOT_TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

print("🤖 Bot running...")
updater.start_polling()
updater.idle()
