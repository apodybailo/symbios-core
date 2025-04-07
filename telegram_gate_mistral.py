from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from ollama_engine import ask_mistral
import os

TELEGRAM_TOKEN = "8179721094:AAH762vsblgKaNdCAFhs50Xh2H4UjRRf5bk"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔮 Модуль Mistral активний. Використовуй /mistral [запит]")

async def mistral_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("⚠️ Введи запит після /mistral.")
        return
    response = ask_mistral(prompt)
    await update.message.reply_text(f"🧠 Mistral:
{response}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mistral", mistral_command))

    app.run_webhook(
        listen="0.0.0.0",
        port=8443,
        webhook_url=os.getenv("TG_WEBHOOK", "https://your-ngrok-url.ngrok.io")
    )