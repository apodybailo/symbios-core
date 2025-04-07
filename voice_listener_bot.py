import os
import json
import subprocess
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import whisper

# === НАЛАШТУВАННЯ ===
BOT_TOKEN = "8179721094:AAH762vsblgKaNdCAFhs50Xh2H4UjRRf5bk"
AUTHORIZED_USER_ID = 909541793
VOICE_DIR = "voice_inputs"
LOG_FILE = "voice_log.json"
WHISPER_MODEL = whisper.load_model("base")

# === ПЕРЕКОНАЙСЯ, ЩО ДИРЕКТОРІЯ ІСНУЄ ===
os.makedirs(VOICE_DIR, exist_ok=True)

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return

    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    ogg_path = os.path.join(VOICE_DIR, f"input_{timestamp}.ogg")
    wav_path = os.path.join(VOICE_DIR, f"input_{timestamp}.wav")

    await file.download_to_drive(ogg_path)

    # 🔊 ПІДСИЛЕННЯ ЗВУКУ ПРИ КОНВЕРТАЦІЇ
    subprocess.run(["ffmpeg", "-i", ogg_path, "-filter:a", "volume=3.0", wav_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 🧠 РОЗПІЗНАВАННЯ ЧЕРЕЗ WHISPER
    result = WHISPER_MODEL.transcribe(wav_path)
    transcript = result["text"]

    # 💾 ЛОГУЄМО
    log_entry = {
        "timestamp": timestamp,
        "ogg": ogg_path,
        "wav": wav_path,
        "text": transcript
    }
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)
    else:
        logs = []
    logs.append(log_entry)
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

    # 🔁 РЕАКЦІЇ НА КОМАНДИ
    lowered = transcript.lower()
    if "наугваль, збережи пам" in lowered:
        await update.message.reply_text("💾 Памʼять збережено у LANA/CONTROL_POINTS (умовно)")
        # Тут можна викликати скрипт, який реально логуватиме це
    elif "ввімкни тінь" in lowered:
        await update.message.reply_text("🌑 Режим Тіні активовано")
        os.system("python3 shadow_mode.py &")
    elif "запусти агроядро" in lowered:
        await update.message.reply_text("🌱 АгроЯдро запускається...")
        os.system("python3 agro_core.py &")
    else:
        await update.message.reply_text(f"🗣 Розпізнано:\n{transcript}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.VOICE, voice_handler))
    app.run_polling()

