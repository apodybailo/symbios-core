
import os
from openai import OpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from logger import log

TELEGRAM_TOKEN = "8179721094:AAH762vsblgKaNdCAFhs50Xh2H4UjRRf5bk"
AUTHORIZED_USER_ID = 909541793
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CODE_OUTPUT_DIR = os.path.expanduser("~/YADRO_SYNC/SYMBIOS_CLOUD/CORE_YADRO/AI_PROGRAMMER/generated")
os.makedirs(CODE_OUTPUT_DIR, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return
    await update.message.reply_text("👨‍💻 AI Програміст оновлений і готовий до роботи.")

async def generate_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return

    if len(context.args) == 0:
        await update.message.reply_text("❗ Вкажи ім'я файлу після /gen")
        return

    filename = context.args[0]
    prompt = " ".join(context.args[1:]) or "напиши скрипт на Python, який виводить Hello World"

    await update.message.reply_text(f"🧠 Генерую код для `{filename}.py`...")

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ти AI-програміст. Генеруй тільки чистий Python-код."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        code = response.choices[0].message.content
        file_path = os.path.join(CODE_OUTPUT_DIR, f"{filename}.py")

        with open(file_path, "w") as f:
            f.write(code)

        await update.message.reply_text(f"✅ Код збережено: `{file_path}`")
        log(f"🧠 Згенеровано код: {file_path}")

    except Exception as e:
        await update.message.reply_text(f"❌ Помилка: {e}")
        log(f"❌ Помилка генерації коду: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gen", generate_code))
    log("👨‍💻 Оновлений AI програміст-бот запущений.")
    app.run_polling()
