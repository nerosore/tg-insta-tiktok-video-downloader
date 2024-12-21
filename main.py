import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from yt_dlp import YoutubeDL

# Replace with your Telegram bot token
BOT_TOKEN = ""

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Function to download the video
def download_video(url: str, download_path: str) -> str:
    logger.info(f"Начинаю загрузку для URL: {url}")
    ydl_opts = {
        "outtmpl": f"{download_path}/%(title)s.%(ext)s",
        "format": "bestvideo+bestaudio/best",
    }
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_path = ydl.prepare_filename(info_dict)
        logger.info(f"Видео скачано успешно: {video_path}")
        return video_path

# Start command
async def start(update: Update, context: CallbackContext) -> None:
    logger.info(f"Пользователь {update.effective_user.id} запустил бота.")
    await update.message.reply_text("Пришли мне ссылку на видео в Instagram или TikTok и я скачаю его для тебя!")

# Handle video link
async def handle_link(update: Update, context: CallbackContext) -> None:
    url = update.message.text
    chat_id = update.message.chat_id

    logger.info(f"Получена ссылка от пользователя {update.effective_user.id}: {url}")

    # Check if the URL is valid
    if "instagram.com" in url or "tiktok.com" in url:
        await update.message.reply_text("Скачиваю видео, подожди")
        try:
            # Download the video
            download_path = "./downloads"
            os.makedirs(download_path, exist_ok=True)
            video_path = download_video(url, download_path)

            # Send the video back to the user
            await context.bot.send_video(chat_id=chat_id, video=open(video_path, "rb"))
            logger.info(f"Видео отправлено пользователю {update.effective_user.id}")

            # Clean up
            os.remove(video_path)
            logger.info(f"Очищено видео: {video_path}")
        except Exception as e:
            logger.error(f"Ошибка скачивания или отправки видео для URL {url}: {e}")
            await update.message.reply_text(f"Возникла ошибка: {e}")
    else:
        pass

# Main function
def main():
    logger.info("Запуск бота...")

    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    # Start the Bot
    logger.info("Бот запущен и обновляет сообщения...")
    application.run_polling()

if __name__ == "__main__":
    main()
