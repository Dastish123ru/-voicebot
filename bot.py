import os
import asyncio
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from aiogram import Bot, Dispatcher, types
from gtts import gTTS
import speech_recognition as sr

API_TOKEN = '7647091828:AAGOGqNOtHGRYnTbagsbB5VuSMgU6Rsv9_A'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Фиктивный веб-сервер чтобы Render не убивал сервис
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')
    def log_message(self, format, *args):
        pass

def run_dummy_server():
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), DummyHandler)
    server.serve_forever()

@dp.message(lambda message: message.voice is not None)
async def handle_voice(message: types.Message):
    file_info = await bot.get_file(message.voice.file_id)
    file_path = file_info.file_path
    await bot.download_file(file_path, "input.ogg")

    os.system("ffmpeg -i input.ogg input.wav -y")

    recognizer = sr.Recognizer()
    with sr.AudioFile("input.wav") as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio, language="ru-RU")
    except Exception:
        text = "Не удалось распознать голосовое сообщение."

    tts = gTTS(text, lang='ru')
    tts.save('voice.ogg')
    with open('voice.ogg', 'rb') as voice:
        await message.answer_voice(voice)

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
    Thread(target=run_dummy_server, daemon=True).start()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
