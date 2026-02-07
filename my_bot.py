# my_bot.py
import os
import logging
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# === Telegram Bot Logic ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет клавиатуру с кнопками при команде /start"""
    keyboard = [
        ["Кнопка 1", "Кнопка 2"],
        ["Кнопка 3", "Кнопка 4"]
    ]
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите кнопку — она появится в поле ввода"
    )
    await update.message.reply_text(
        "Нажмите любую кнопку — её текст автоматически появится в поле ввода!",
        reply_markup=reply_markup
    )

def main():
    # Получаем токен из переменной окружения (на Render задаётся вручную)
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        raise ValueError("Переменная окружения TELEGRAM_BOT_TOKEN не установлена!")

    # Инициализация бота
    application = Application.builder().token(TOKEN).build()

    # Обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # Запуск polling в отдельном потоке
    def run_bot():
        logger.info("Запуск Telegram-бота...")
        application.run_polling(drop_pending_updates=True)

    bot_thread = Thread(target=run_bot, daemon=True)
    bot_thread.start()

    # === Фейковый HTTP-сервер для Render ===
    class HealthCheckHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"OK")

        def log_message(self, format, *args):
            # Отключаем логирование запросов health-check'а
            return

    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("", port), HealthCheckHandler)
    logger.info(f"Фейковый HTTP-сервер запущен на порту {port} для Render")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Сервер остановлен.")
        server.shutdown()

if __name__ == "__main__":
    main()
