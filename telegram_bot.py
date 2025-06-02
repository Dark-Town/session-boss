import logging
import requests
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Load bot token from .env file
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Optional: restrict access
AUTHORIZED_USERS = []  # Example: [123456789]

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send /getcode <phone_number> to get your WhatsApp code.")

async def getcode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if AUTHORIZED_USERS and user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("🚫 Access denied.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("Usage: /getcode <phone_number>")
        return

    phone_number = context.args[0]

    try:
        response = requests.get(f"http://localhost:7860/code?number={phone_number}")
        if response.status_code == 200:
            await update.message.reply_text(f"✅ Your XMD Code:\n{response.text.strip()}")
        else:
            await update.message.reply_text("❌ Could not get the code. Make sure the server is running.")
    except Exception as e:
        logging.error("Error connecting to session server: %s", e)
        await update.message.reply_text("❌ Server connection error.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("getcode", getcode))
    print("🤖 Telegram bot is running...")
    app.run_polling()
