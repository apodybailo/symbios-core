#!/usr/bin/env python3
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction
from pydub import AudioSegment
import requests
import time
from gtts import gTTS
import uuid

# Logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Env
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID", "0"))

# Paths
VOICE_INPUT_DIR = "voice_inputs"
os.makedirs(VOICE_INPUT_DIR, exist_ok=True)

# Helpers
async def transcribe_audio(file_path):
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    with open(file_path, "rb") as f:
        transcript = openai.Audio.transcribe("whisper-1", f)
    return transcript["text"]

def generate_response(prompt):
    try:
        resp = requests.post("http://localhost:11434/api/generate", json={"model": "mistral", "prompt": prompt, "stream": False})
        return resp.json().get("response", "").strip()
    except Exception as e:
        return f"[Mistral Error] {e}"

def speak(text, out_path):
    tts = gTTS(text=text, lang="uk")
    tts.save(out_path)

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧠 Symbios активний. Надішли голосове або текст.")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        await update.message.reply_text("⛔ Недостатньо прав.")
        return

    file = await update.message.voice.get_file()
    ogg_path = os.path.join(VOICE_INPUT_DIR, f"{uuid.uuid4()}.ogg")
    mp3_path = ogg_path.replace(".ogg", ".mp3")

    await update.message.chat.send_action(action=ChatAction.TYPING)
    file.download_to_drive(ogg_path)
    AudioSegment.from_ogg(ogg_path).export(mp3_path, format="mp3")

    text = await transcribe_audio(mp3_path)
    reply = generate_response(text)

    tts_path = ogg_path.replace(".ogg", "_reply.mp3")
    speak(reply, tts_path)

    await update.message.reply_text(f"📜: {text}")
    await update.message.reply_text(f"🤖: {reply}")
    await update.message.reply_voice(voice=open(tts_path, "rb"))

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        await update.message.reply_text("⛔ Недостатньо прав.")
        return

    await update.message.chat.send_action(action=ChatAction.TYPING)
    reply = generate_response(update.message.text)
    tts_path = os.path.join(VOICE_INPUT_DIR, f"{uuid.uuid4()}_reply.mp3")
    speak(reply, tts_path)

    await update.message.reply_text(reply)
    await update.message.reply_voice(voice=open(tts_path, "rb"))

# App
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", "10000")),
        webhook_url=WEBHOOK_URL,
        webhook_path="/webhook"
    )

if __name__ == "__main__":
    main()
