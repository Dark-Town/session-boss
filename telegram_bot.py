import os
import logging
import requests
from dotenv import load_dotenv
from telegram import (
    Update, InlineKeyboardMarkup, InlineKeyboardButton
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)

# Load credentials
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SESSION_SERVER_URL = os.getenv("SESSION_SERVER_URL", "https://session-boss.onrender.com")

logging.basicConfig(level=logging.INFO)

# Start command with buttons
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📥 Get WhatsApp Code", callback_data="get_code")],
        [InlineKeyboardButton("📊 Vote (Anonymous Poll)", callback_data="poll")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        with open("start.jpg", "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption="🤖 *Welcome to the WhatsApp XMD Bot!*\nUse the buttons below to continue.",
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
    except FileNotFoundError:
        await update.message.reply_text(
            "🤖 *Welcome!*\nUse the buttons below to continue.",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

# Button clicks
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "get_code":
        await query.message.reply_text("📱 Send `/getcode <phone_number>` to get your XMD code.", parse_mode="Markdown")

    elif query.data == "poll":
        await context.bot.send_poll(
            chat_id=query.message.chat_id,
            question="Do you like this bot?",
            options=["Yes 👍", "No 👎", "Needs Improvement 💡"],
            is_anonymous=True
        )

    elif query.data == "help":
        await query.message.reply_text("ℹ️ Just send `/getcode <phone_number>` to get your WhatsApp code.")

# Fetch WhatsApp code
async def getcode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /getcode <phone_number>")
        return

    phone_number = context.args[0]
    url = f"{SESSION_SERVER_URL}/pair/code?number={phone_number}"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            await update.message.reply_text(f"✅ Your XMD Code:\n{response.text.strip()}")
        else:
            await update.message.reply_text(
                f"❌ Failed to fetch code from server.\nStatus: {response.status_code}\nResponse: {response.text}"
            )
    except Exception as e:
        logging.exception("Server connection error:")
        await update.message.reply_text(f"❌ Server connection error:\n{e}")

# Main
if __name__ == '__main__':
    if not BOT_TOKEN:
        print("❌ Missing TELEGRAM_BOT_TOKEN in .env")
        exit(1)

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("getcode", getcode))

    print("🤖 Telegram bot is running...")
    app.run_polling()
