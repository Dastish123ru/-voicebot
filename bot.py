import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from gtts import gTTS
import speech_recognition as sr

API_TOKEN = '7647091828:AAGOGqNOtHGRYnTbagsbB5VuSMgU6Rsv9_A'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(lambda message: message.voice is not None)
async def handle_voice(message: types.Message):
    file_info = await bot.get_file(message.voice.file_id)
    file_path = file_info.file_path
    await bot.download_file(file_path, "input.ogg")

    # Конвертация ogg в wav
    os.system("ffmpeg -i input.ogg input.wav -y")

    # Распознавание речи
    recognizer = sr.Recognizer()
    with sr.AudioFile("input.wav") as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio, language="ru-RU")
    except Exception:
        text = "Не удалось распознать голосовое сообщение."

    # Озвучка ответа
    tts = gTTS(text, lang='ru')
    tts.save('voice.ogg')
    with open('voice.ogg', 'rb') as voice:
        await message.answer_voice(voice)

    # Очистка файлов
    for f in ['input.ogg', 'input.wav', 'voice.ogg']:
        if os.path.exists(f):
            os.remove(f)

@dp.message(lambda message: message.text is not None)
async def handle_text(message: types.Message):
    text = message.text
    tts = gTTS(text, lang='ru')
    tts.save('voice.ogg')
    with open('voice.ogg', 'rb') as voice:
        await message.answer_voice(voice)
    os.remove('voice.ogg')

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
