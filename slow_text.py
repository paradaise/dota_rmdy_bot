import os
import edge_tts
import asyncio
from telegram import Update
from telegram.ext import ContextTypes

# Убедитесь, что папка temp существует
os.makedirs("temp", exist_ok=True)


async def text_to_slow_speech(text: str, user_id: int) -> str:
    """Преобразует текст в замедленную речь с мужским голосом через edge_tts"""
    mp3_path = f"temp/{user_id}_speech.mp3"

    voice = "ru-RU-DmitryNeural"
    rate = "-50%"

    try:
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        await communicate.save(mp3_path)
        if os.path.exists(mp3_path):
            return mp3_path

    except Exception as e:
        print(f"Ошибка в text_to_slow_speech: {e}")
        return None


async def slow_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /slow_text"""
    if not context.args:
        await update.message.reply_text(
            "❌ Укажите текст после команды, например: <code>/slow_text Привет</code>",
            parse_mode="HTML",
        )
        return

    text = " ".join(context.args)
    try:
        slowed_path = await text_to_slow_speech(text, update.effective_user.id)

        if slowed_path:
            await update.message.reply_voice(
                voice=open(slowed_path, "rb"),
                caption=f"🗣 <b>Замееееедленный голос:</b> <i>{text}</i>",
                parse_mode="HTML",
            )

            # Удаляем временные файлы
            if os.path.exists(slowed_path):
                os.remove(slowed_path)

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")
