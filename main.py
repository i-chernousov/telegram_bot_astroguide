import os
import asyncio
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties

from handlers import router


async def main():
    """
    Главная асинхронная функция для запуска бота.
    Загружает переменные окружения, создаёт экземпляр бота
    и запускает polling.
    """
    load_dotenv()

    # Получаем токен из переменных окружения
    token = os.getenv('TOKEN')

    # Проверяем, что токен существует
    if not token:
        raise ValueError("Токен не найден в переменных окружения.")

    # Инициализируем бота с переданным токеном и настройками
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Инициализируем Dispatcher, но не передаем bot в конструктор
    dp = Dispatcher()

    # Подключаем роутер
    dp.include_router(router)

    # Запуск бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        # Запуск главной асинхронной функции
        asyncio.run(main())

    except KeyboardInterrupt:
        # Информируем пользователя о завершении работы
        print("Бот был остановлен пользователем.")
