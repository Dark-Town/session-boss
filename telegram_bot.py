import os
import logging
import requests
from dotenv import load_dotenv
from telegram import (
    Update, InlineKeyboardMarkup, InlineKeyboardButton
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

# Load .env variables
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SESSION_SERVER_URL = os.getenv("SESSION_SERVER_URL", "https://session-boss.onrender.com")
MAX_MESSAGE_LENGTH = 4000  # Telegram max is 4096 chars

logging.basicConfig(level=logging.INFO)

# --- Start command with image and buttons ---
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

# --- Handle inline button actions ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "get_code":
        await query.message.reply_text("📱 Send `/getcode <phone_number>` to get your WhatsApp session code.", parse_mode="Markdown")

    elif query.data == "poll":
        await context.bot.send_poll(
            chat_id=query.message.chat_id,
            question="Do you like this bot?",
            options=["Yes 👍", "No 👎", "Needs Improvement 💡"],
            is_anonymous=True
        )

    elif query.data == "help":
        await query.message.reply_text("ℹ️ Use `/getcode <phone_number>` to get your WhatsApp XMD code and Mega link.")

# --- /getcode command ---
async def getcode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /getcode <phone_number>")
        return

    phone = context.args[0]
    url = f"{SESSION_SERVER_URL}/pair/code?number={phone}"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            text = response.text.strip()
            if len(text) > MAX_MESSAGE_LENGTH:
                text = text[:MAX_MESSAGE_LENGTH] + "\n\n⚠️ Output truncated due to Telegram limits."
            await update.message.reply_text(f"✅ Session Ready:\n{text}")
        else:
            await update.message.reply_text(
                f"❌ Server error:\nStatus: {response.status_code}\n{response.text[:300]}"
            )
    except Exception as e:
        logging.exception("Server connection error:")
        await update.message.reply_text(f"❌ Server connection error:\n{e}")

# --- React to any text message ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if msg.chat.type in ['group', 'supergroup']:
        await msg.reply_text("👀 I'm active here! Use `/getcode <phone>` to get your WhatsApp XMD code.")
    else:
        await msg.reply_text("💬 Need help? Just use `/getcode <your_number>` to get started.")

# --- Main entry point ---
if __name__ == '__main__':
    if not BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN is not set in .env")
        exit(1)

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("getcode", getcode))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Telegram bot is running...")
    app.run_polling()
