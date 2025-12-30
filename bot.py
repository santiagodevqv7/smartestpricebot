import os
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

from price_comparator import compare_prices


BOT_TOKEN = os.getenv("BOT_TOKEN")


async def handle_message(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()

    offers = compare_prices(query)

    if not offers:
        await update.message.reply_text("❌ No prices found.")
        return

    # filtrar ofertas válidas
    offers = [o for o in offers if o.get("price")]

    if not offers:
        await update.message.reply_text("❌ No relevant results.")
        return

    offers.sort(key=lambda x: x["price"])

    best = offers[0]
    top5 = offers[:5]

    msg = "🛒 *SmartestPriceBot*\n"
    msg += f"🔍 *Product:* {query.title()}\n\n"

    msg += "🏆 *Best price found*\n"
    msg += f"🥇 *{best['store']}* — *${best['price']:.2f}*\n"

    # link si existe
    if best.get("link"):
        msg += f"👉 [Buy here]({best['link']})\n"

    msg += "\n📊 *Price comparison*\n"
    for o in top5:
        line = f"• {o['store']} — ${o['price']:.2f}"
        if o.get("link"):
            line += " ([link]({}))".format(o["link"])
        msg += line + "\n"

    msg += "\n⏱ _Save time by comparing prices automatically_"


    await update.message.reply_text(msg, parse_mode="Markdown")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    print("🤖 Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
