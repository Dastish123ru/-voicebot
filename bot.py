python
import os
from aiogram import Bot, Dispatcher, types, executor
from gtts import gTTS
import speech_recognition as sr

API_TOKEN = '7647091828:AAGOGqNOtHGRYnTbagsbB5VuSMgU6Rsv9_A'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(content_types=types.ContentType.VOICE)
async def handle_voice(message: types.Message):
    file_info = await bot.get_file(message.voice.file_id)
    file_path = file_info.file_path
    await bot.download_file(file_path, "input.ogg")

    # Конвертация ogg в wav (SpeechRecognition не работает с ogg)
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

@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_text(message: types.Message):
    text = message.text
    tts = gTTS(text, lang='ru')
    tts.save('voice.ogg')
    with open('voice.ogg', 'rb') as voice:
        await message.answer_voice(voice)
    os.remove('voice.ogg')

if __name__ == '__main__':
    executor.start_polling(dp)
