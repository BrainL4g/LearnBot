import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.exceptions import TelegramAPIError
from dotenv import load_dotenv
import sys
from datetime import datetime

# Настройка логирования
logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  handlers=[
    logging.FileHandler('bot.log'),
    logging.StreamHandler(sys.stdout)
  ]
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

# Получение токена бота
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
  logger.error("BOT_TOKEN не найден в .env файле")
  sys.exit(1)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# Создание клавиатуры
def get_main_keyboard() -> ReplyKeyboardMarkup:
  builder = ReplyKeyboardBuilder()
  builder.add(KeyboardButton(text="Проверить статус"))
  builder.add(KeyboardButton(text="Получить время"))
  builder.add(KeyboardButton(text="Помощь"))
  builder.adjust(2)
  return builder.as_markup(resize_keyboard=True)


# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
  logger.info(f"Пользователь {message.from_user.id} запустил бота")
  await message.answer(
    "Привет! Я тестовый бот. Используй команды или клавиатуру ниже.",
    reply_markup=get_main_keyboard()
  )


# Обработчик команды /help
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
  logger.info(f"Пользователь {message.from_user.id} запросил помощь")
  help_text = """
    Доступные команды:
    /start - Запустить бота
    /help - Показать это сообщение
    /status - Проверить статус бота
    /time - Получить текущее время

    Или используй кнопки клавиатуры!
    """
  await message.answer(help_text, reply_markup=get_main_keyboard())


# Обработчик команды /status
@dp.message(Command("status"))
async def cmd_status(message: types.Message):
  logger.info(f"Пользователь {message.from_user.id} запросил статус")
  try:
    # Проверка доступности API
    await bot.get_me()
    status = "🟢 Бот работает нормально"
  except TelegramAPIError as e:
    status = f"🔴 Ошибка API: {str(e)}"
    logger.error(f"Ошибка API при проверке статуса: {str(e)}")

  await message.answer(
    f"Статус бота: {status}\n"
    f"Время работы: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    reply_markup=get_main_keyboard()
  )


# Обработчик команды /time
@dp.message(Command("time"))
async def cmd_time(message: types.Message):
  logger.info(f"Пользователь {message.from_user.id} запросил время")
  current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  await message.answer(
    f"Текущее время: {current_time}",
    reply_markup=get_main_keyboard()
  )


# Обработчик текстовых сообщений
@dp.message()
async def text_handler(message: types.Message):
  text = message.text.lower()
  logger.info(f"Пользователь {message.from_user.id} отправил сообщение: {text}")

  if text == "проверить статус":
    await cmd_status(message)
  elif text == "получить время":
    await cmd_time(message)
  elif text == "помощь":
    await cmd_help(message)
  else:
    await message.answer(
      "Неизвестная команда. Используй /help для списка команд.",
      reply_markup=get_main_keyboard()
    )


# Обработчик ошибок
@dp.errors()
async def error_handler(update: types.Update, exception: Exception):
  logger.error(f"Ошибка при обработке обновления: {str(exception)}")
  try:
    if update.message:
      await update.message.answer(
        "Произошла ошибка. Попробуйте позже или свяжитесь с администратором.",
        reply_markup=get_main_keyboard()
      )
  except Exception as e:
    logger.error(f"Ошибка при отправке сообщения об ошибке: {str(e)}")
  return True


# Функция запуска бота
async def main():
  try:
    logger.info("Бот запускается...")
    bot_info = await bot.get_me()
    logger.info(f"Бот успешно запущен: @{bot_info.username}")

    # Проверка соединения с Telegram API
    try:
      await bot.get_updates(timeout=2)
      logger.info("Соединение с Telegram API успешно")
    except TelegramAPIError as e:
      logger.error(f"Ошибка соединения с Telegram API: {str(e)}")
      sys.exit(1)

    # Запуск polling
    await dp.start_polling(bot, polling_timeout=30)

  except Exception as e:
    logger.error(f"Критическая ошибка при запуске бота: {str(e)}")
    sys.exit(1)
  finally:
    await bot.session.close()


if __name__ == "__main__":
  try:
    asyncio.run(main())
  except KeyboardInterrupt:
    logger.info("Бот остановлен пользователем")
  except Exception as e:
    logger.error(f"Непредвиденная ошибка: {str(e)}")