from flask import Flask, request
import telebot
import json

API_TOKEN = '8179721094:AAH762vsblgKaNdCAFhs50Xh2H4UjRRf5bk'

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        print(f"[UPDATE] {json_string}")
        bot.process_new_updates([update])
        return '', 200
    else:
        return 'Bad request', 400

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    print(f"[MESSAGE] {message.chat.id} → {message.text}")
    bot.send_message(message.chat.id, "Я живий, брате.")

if __name__ == '__main__':
    print(">>> Запуск Webhook Бота")
    app.run(host='0.0.0.0', port=8000)
