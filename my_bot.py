# my_bot.py
import os
import logging
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from aiohttp import web

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# === Telegram Bot ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Кнопка 1", "Кнопка 2"], ["Кнопка 3", "Кнопка 4"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите кнопку — она появится в поле ввода!", reply_markup=reply_markup)

# === HTTP Health Check для Render ===
async def health_check(request):
    return web.Response(text="OK")

async def main():
    # Получаем токен
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN не задан!")

    # Создаём приложение Telegram
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))

    # Запускаем бота в фоне
    bot_task = asyncio.create_task(app.run_polling(drop_pending_updates=True))
    logger.info("Telegram-бот запущен в фоне.")

    # Настраиваем HTTP-сервер для Render
    http_app = web.Application()
    http_app.router.add_get('/{tail:.*}', health_check)  # ловим все GET-запросы

    port = int(os.getenv("PORT", 10000))
    runner = web.AppRunner(http_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"HTTP-сервер запущен на порту {port} для Render.")

    # Ждём завершения (бесконечно)
    try:
        await bot_task
    except asyncio.CancelledError:
        logger.info("Бот остановлен.")
    finally:
        await app.stop()
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
