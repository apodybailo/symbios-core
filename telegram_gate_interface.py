
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# Логування
logging.basicConfig(level=logging.INFO)

# Основна команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Mistral", callback_data='mistral')],
        [InlineKeyboardButton("Фотоархів", callback_data='lana')],
        [InlineKeyboardButton("Маячок", callback_data='geo')],
        [InlineKeyboardButton("Продукти", callback_data='groceries')],
        [InlineKeyboardButton("Відповіді", callback_data='logs')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Вибери дію:", reply_markup=reply_markup)

# Обробка натискань на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    response_map = {
        "mistral": "Готовий прийняти запит до Mistral.",
        "lana": "Відкриваю модуль LANA.",
        "geo": "Оновлюю геолокацію маячка.",
        "groceries": "Переходимо до списку покупок.",
        "logs": "Виводжу останні логи ядра.",
    }

    response = response_map.get(data, "Невідома команда.")
    await query.edit_message_text(text=response)

# Запуск бота
def main():
    import os
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()

if __name__ == "__main__":
    main()
