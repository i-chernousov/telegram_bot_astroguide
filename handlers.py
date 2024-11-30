import sqlite3 as sq
from datetime import datetime
import requests
from bs4 import BeautifulSoup

from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import CommandStart

from keyboards import show_button_categories, show_button_back

# Инициализация роутера
router = Router()

@router.message(CommandStart())
async def start_message(message: Message):
    """Обработчик команды /start."""
    with sq.connect("base_astroguide") as date_base:
        cursor = date_base.cursor()

        # Получаем информацию о сообщении
        message_info = cursor.execute("""
            SELECT image_message, text_message 
            FROM message_info
        """).fetchone()

        # Получаем информацию о кнопках
        button_info = cursor.execute("""
            SELECT name_button, callback_button 
            FROM button_info
        """).fetchall()

    # Удаляем сообщение пользователя
    await message.delete()

    # Отправляем ответ с изображением и кнопками
    await message.answer_photo(
        photo=message_info[0],
        caption=message_info[1],
        reply_markup=await show_button_categories(button_info)
    )


@router.callback_query(F.data.startswith("show_horoscope_"))
async def callback_show_horoscope(callback: CallbackQuery):
    """Обработчик для гороскопа по выбранному знаку зодиака."""
    id_horoscope = callback.data.split("_")[2]

    with sq.connect("base_astroguide") as date_base:
        cursor = date_base.cursor()

        # Проверяем, есть ли записи на сегодня
        parser_info = cursor.execute("""
            SELECT * FROM parser_info WHERE date_parser = ?
        """, (datetime.today().date(),)).fetchone()

        if parser_info is None:
            # Если нет записей на сегодня, парсим гороскопы
            zodiac_signs = [
                "aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio",
                "sagittarius", "capricorn", "aquarius", "pisces"
            ]
            base_text = []

            # Парсим гороскопы для всех знаков зодиака
            for index, sign in enumerate(zodiac_signs):
                url = requests.get(f"https://horo.mail.ru/prediction/{sign}/today/")
                soup = BeautifulSoup(url.text, "lxml")
                main_content = soup.find('main', class_=f'e45a4c1552 be13d659a4 navigationContainer_{index + 1} dcced6f448')
                paragraphs = main_content.find_all('div', class_='b6a5d4949c e45a4c1552')

                # Извлекаем текст гороскопа
                paragraph_1 = paragraphs[0].find('p').text.strip()
                paragraph_2 = paragraphs[1].find('p').text.strip()
                base_text.append(f"{paragraph_1}\n\n{paragraph_2}")

            # Вставляем данные в базу данных
            cursor.execute("""
                INSERT INTO parser_info (date_parser, sign_1, sign_2, sign_3, sign_4, sign_5, sign_6, sign_7, sign_8, sign_9, sign_10, sign_11, sign_12)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (datetime.today().date(), *base_text))

        # Получаем информацию о гороскопе для выбранного знака
        message_info = cursor.execute("""
            SELECT image_horoscope, name_horoscope 
            FROM horoscope_info 
            WHERE id_horoscope = ?
        """, (id_horoscope,)).fetchone()

        # Получаем гороскоп для выбранного знака
        parser_info = cursor.execute(f"""
            SELECT sign_{id_horoscope} FROM parser_info WHERE date_parser = ?
        """, (datetime.today().date(),)).fetchone()

        # Формируем сообщение
        edit_message = InputMediaPhoto(
            media=message_info[0],
            caption=f"<b>Показан гороскоп для - {message_info[1]}</b>\n\n{parser_info[0]}\n\n"
                    f"<b>Информация предоставлена сайтом horo.mail.ru</b>"
        )

    # Отправляем обновленное сообщение
    await callback.answer()
    await callback.message.edit_media(media=edit_message, reply_markup=await show_button_back())


@router.callback_query(F.data.startswith("show_categories"))
async def callback_show_categories(callback: CallbackQuery):
    """Обработчик для отображения категорий."""
    with sq.connect("base_astroguide") as date_base:
        cursor = date_base.cursor()

        # Получаем информацию о сообщении
        message_info = cursor.execute("""
            SELECT image_message, text_message 
            FROM message_info
        """).fetchone()

        # Получаем информацию о кнопках
        button_info = cursor.execute("""
            SELECT name_button, callback_button 
            FROM button_info
        """).fetchall()

    # Формируем ответ с изображением и текстом
    edit_message = InputMediaPhoto(
        media=message_info[0],
        caption=f"{message_info[1]}"
    )

    # Отправляем обновленное сообщение с кнопками
    await callback.answer()
    await callback.message.edit_media(media=edit_message, reply_markup=await show_button_categories(button_info))
