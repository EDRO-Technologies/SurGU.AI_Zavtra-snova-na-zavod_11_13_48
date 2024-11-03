import os
from telegram import Update
import requests
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from backbotend.telegabot.test2rusmo import test2rusmo

# Путь для сохранения файлов
FILE_PATH = "C:\\Users\\nasty\\Desktop\\main"
DJANGO_UPLOAD_URL = "http://127.0.0.1:8000/api/upload/"

# Функция для старта бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь мне PDF файл первым сообщением, а затем текст.")

# Обработчик файла
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Получаем файл из сообщения
    document = update.message.document
    file = await document.get_file()
    
    # Создаем папку, если она не существует
    os.makedirs(FILE_PATH, exist_ok=True)
    
    # Загружаем и сохраняем файл
    file_path = os.path.join(FILE_PATH, document.file_name)
    print(document.file_name)
    await file.download_to_drive(file_path)
    await update.message.reply_text("Приступаю к чтению файла...")
    with open(file_path, 'rb') as f:
        #response = requests.post(DJANGO_UPLOAD_URL, files={'file': f})
        file_name = document.file_name  # Имя файла, который отправлен ботом
        response = requests.post(DJANGO_UPLOAD_URL, files={'file': (file_name, f)}, data={'file_name': file_name})
    if response.status_code == 201:
        file_url = response.json()['file_url']
        file_content = response.json()['file_content']
        if not file_content:
            await update.message.reply_text(f"Кажется, есть проблемы с файлом. Попробуйте выбрать другой документ.")
        else:
            await update.message.reply_text(f"Файл успешно загружен на сервер. Вот его отрывок: {file_content[:30]}")
            await update.message.reply_text("Теперь задайте вопрос по содержимому файла:")

            # Сохраняем содержимое файла для дальнейшего использования
            print("File_content: ", file_content)
            context.user_data["file_content"] = file_content
            context.user_data["file_path"] = file_path  # Сохраняем путь в user_data
    else:
        await update.message.reply_text("Ошибка чтения файла на сервере.")
    
    
    
    # await update.message.reply_text("Файл получен. Теперь отправь текст.")
    # print(context.user_data["file_content"], context.user_data["file_path"])
    
# Обработчик текста
async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("contextcontextcontextcontextcontextcontext")
    if "file_content" in context.user_data:
        file_content = context.user_data["file_content"]
        question = update.message.text
        print(question)

        # Анализ текста
        answer = test2rusmo(question, file_content)  # Вызов функции анализа

        await update.message.reply_text(f"Ответ: {answer}", 
                 parse_mode="HTML")
    else:
        await update.message.reply_text("Пожалуйста, сначала отправьте файл.")

# Основная функция для запуска бота
def main():
    # Инициализируем бота
    token = "8070505505:AAEkudp5GY07sXGItgzpzUs4zayR_0eixtI"  # Замените на ваш токен
    app = Application.builder().token(token).build()
    
    # Обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.add_handler(MessageHandler(filters.TEXT, handle_question))
    
    # Запускаем бота
    app.run_polling()

if __name__ == "__main__":
    main()
