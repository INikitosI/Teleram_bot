import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import asyncio

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токен из переменных окружения
TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    logger.error("BOT_TOKEN не установлен!")
    raise ValueError("Установите переменную окружения BOT_TOKEN")

# Простой HTTP-сервер для поддержания активности на Render
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'Bot is alive!')
    
    def log_message(self, format, *args):
        pass  # Отключаем логирование запросов

def run_health_server():
    """Запуск HTTP-сервера на порту 10000"""
    port = 10000
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    logger.info(f"Health server started on port {port}")
    server.serve_forever()

# Обработчики команд бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    await update.message.reply_html(
        f"Привет, {user.mention_html()}! 👋\n"
        f"Я простой бот, работающий на Render.\n"
        f"Мой ID: {update.effective_chat.id}"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    await update.message.reply_text("Доступные команды:\n/start - Начать общение\n/help - Помощь")

def main():
    """Основная функция запуска бота"""
    logger.info("Starting bot...")
    
    # Запускаем HTTP-сервер в отдельном потоке
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    # Создаем приложение бота
    application = Application.builder().token(TOKEN).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Запускаем бота
    logger.info("Bot started successfully!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
