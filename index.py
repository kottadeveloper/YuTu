import telebot
import yt_dlp
import os
import re
import ssl
import certifi

# Укажите ваш токен
TOKEN = "7522900529:AAE03f-5hLsjS3xCxsJTT99Fh_KN_84uXI0"
bot = telebot.TeleBot(TOKEN, threaded=False)  # Отключаем многопоточность

# Регулярное выражение для проверки ссылки YouTube
YOUTUBE_REGEX = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w-]+)"
PLAYLIST_REGEX = r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/playlist\?list=([\w-]+)"

# Папка для сохранения видео
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Настройка SSL для устранения ошибки
ssl._create_default_https_context = ssl._create_unverified_context
os.environ["SSL_CERT_FILE"] = certifi.where()

def progress_hook(d):
    if d['status'] == 'downloading':
        downloaded = d.get('downloaded_bytes', 0) / (1024 * 1024)  # в МБ
        total = d.get('total_bytes', 1) / (1024 * 1024)  # в МБ
        percent = d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100
        message = f"📥 Загружено: {downloaded:.2f} MB / {total:.2f} MB ({percent:.2f}%)"
        bot.edit_message_text(message, d['chat_id'], d['status_message_id'])
    
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Чтобы скачать видео с YouTube отправь мне ссылку, по поводу ошибок писать на номер +998-95-004-97-49 Жавохир")

@bot.message_handler(func=lambda message: re.match(YOUTUBE_REGEX, message.text) or re.match(PLAYLIST_REGEX, message.text))
def download_video(message):
    url = message.text
    chat_id = message.chat.id
    
    status_message = bot.send_message(chat_id, "⏳ Ищу видео...")
    
    try:
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'format': 'mp4',
            'nocheckcertificate': True,
            'noplaylist': True,  # Загружаем только одно видео, даже если это плейлист
            'progress_hooks': [lambda d: progress_hook({**d, 'chat_id': chat_id, 'status_message_id': status_message.message_id})]
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get('title', 'Без названия')
        
        bot.edit_message_text("🔄 Видео загружено, отправляю...", chat_id, status_message.message_id)
        bot.send_video(chat_id, open(filename, 'rb'), caption=f"🎬 {title}\n\n🤖 @DownloadYutu_bot")
        
        # Удаление файла после отправки
        os.remove(filename)
        bot.send_message(chat_id, "✅ Видео успешно отправлено!")
    
    except Exception as e:
        bot.edit_message_text(f"❌ Ошибка: {str(e)}", chat_id, status_message.message_id)

# Запуск бота без потоков
print("Бот запущен...")
bot.infinity_polling()  # Используем infinity_polling() вместо polling(none_stop=True)