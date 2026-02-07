# my_bot.py
import os
import logging
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from http.server import BaseHTTPRequestHandler
from socketserver import TCPServer
from threading import Thread

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# === Telegram Bot Handlers ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

# === Фейковый HTTP-сервер (синхронный, но запущенный в отдельном потоке) ===

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        return  # подавляем логи

def start_http_server(port: int):
    with TCPServer(("", port), HealthCheckHandler) as httpd:
        logger.info(f"Фейковый HTTP-сервер запущен на порту {port}")
        httpd.serve_forever()

# === Основная асинхронная логика ===

async def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("Переменная окружения BOT_TOKEN не установлена!")

    # Запуск HTTP-сервера в отдельном потоке (он синхронный, но легковесный)
    port = int(os.environ.get("PORT", 10000))
    http_thread = Thread(target=start_http_server, args=(port,), daemon=True)
    http_thread.start()

    # Инициализация и запуск Telegram-бота
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))

    logger.info("Запуск Telegram-бота в режиме polling...")
    await application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
