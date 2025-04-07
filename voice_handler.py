import tempfile
from telegram import Update
from telegram.ext import ContextTypes
from voice_utils_local import convert_ogg_to_wav, transcribe_audio, generate_tts
from mistral_interface import generate_with_mistral

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_ogg:
        await file.download_to_drive(temp_ogg.name)

        wav_path = convert_ogg_to_wav(temp_ogg.name)
        text = transcribe_audio(wav_path)

        if not text:
            await update.message.reply_text("⚠️ Не вдалося розпізнати аудіо.")
            return

        response = generate_with_mistral(text)

        tts_path = generate_tts(response)
        if tts_path:
            await update.message.reply_voice(voice=open(tts_path, "rb"))
        else:
            await update.message.reply_text(response)
