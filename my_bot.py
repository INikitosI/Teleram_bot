import os
import logging
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токен из переменных окружения
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в переменных окружения")

# Создаем Flask приложение для Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Telegram Bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    return "OK"

# Кнопки с текстом для вставки
BUTTONS = [
    ["❗ Важно", "📢 Объявление", "❓ Вопрос"],
    ["✅ Решено", "🚀 Срочно", "⚠️ Проблема"],
    ["📝 Заметка", "💡 Идея", "🔧 Техническое"]
]

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = []
    
    # Создаем кнопки
    for row in BUTTONS:
        keyboard_row = []
        for button_text in row:
            keyboard_row.append(InlineKeyboardButton(button_text, callback_data=button_text))
        keyboard.append(keyboard_row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Привет, {user.first_name}!\n\n"
        "Нажми на кнопку, чтобы вставить текст в начало сообщения.\n"
        "Затем просто начни печатать своё сообщение.",
        reply_markup=reply_markup
    )

# Обработчик нажатия кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Сохраняем выбранный текст в контексте пользователя
    selected_text = query.data
    context.user_data['prefix'] = selected_text
    
    # Отправляем сообщение с инструкцией
    await query.edit_message_text(
        text=f"✅ Выбрано: {selected_text}\n\n"
             "Теперь напишите ваше сообщение, и текст кнопки автоматически добавится в начало.",
        reply_markup=query.message.reply_markup
    )

# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    # Проверяем, есть ли сохраненный префикс
    if 'prefix' in context.user_data:
        prefix = context.user_data['prefix']
        
        # Формируем сообщение с префиксом
        formatted_message = f"{prefix}: {user_message}"
        
        # Отправляем отформатированное сообщение
        await update.message.reply_text(formatted_message)
        
        # Очищаем префикс после использования
        del context.user_data['prefix']
        
        # Показываем клавиатуру снова
        keyboard = []
        for row in BUTTONS:
            keyboard_row = []
            for button_text in row:
                keyboard_row.append(InlineKeyboardButton(button_text, callback_data=button_text))
            keyboard.append(keyboard_row)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Выберите следующую кнопку или напишите сообщение:",
            reply_markup=reply_markup
        )
    else:
        # Если префикса нет, показываем кнопки
        keyboard = []
        for row in BUTTONS:
            keyboard_row = []
            for button_text in row:
                keyboard_row.append(InlineKeyboardButton(button_text, callback_data=button_text))
            keyboard.append(keyboard_row)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Сначала выберите кнопку для добавления префикса:",
            reply_markup=reply_markup
        )

# Обработчик ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Ошибка: {context.error}")

# Основная функция
def main():
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    logger.info("Бот запускается...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    # Импортируем здесь, чтобы избежать циклических импортов
    import threading
    
    # Запускаем Flask сервер в отдельном потоке
    flask_thread = threading.Thread(
        target=lambda: app.run(host='0.0.0.0', port=10000, debug=False, use_reloader=False)
    )
    flask_thread.daemon = True
    flask_thread.start()
    
    # Запускаем бота
    main()
