from aiogram.utils.keyboard import InlineKeyboardBuilder

async def show_button_categories(button_info):
    """
    Создает инлайн-кнопки для отображения гороскопов по категориям.

    :param button_info: Список с информацией о кнопках (текст и callback_data)
    :return: Маркап с инлайн-кнопками
    """
    builder = InlineKeyboardBuilder()

    # Итерируем по каждой кнопке
    for index, (text, callback_data) in enumerate(button_info):
        builder.button(text=text, callback_data=f"show_horoscope_{callback_data}")

    # Возвращаем кнопки с корректным количеством кнопок в строке (по 3 кнопки)
    return builder.adjust(3).as_markup()


async def show_button_back():
    """
    Создает кнопку "Назад" для возвращения в меню категорий.

    :return: Маркап с кнопкой "Назад"
    """
    builder = InlineKeyboardBuilder()

    # Добавляем кнопку для возвращения в меню категорий
    builder.button(text="Назад ↩️", callback_data="show_categories")

    return builder.adjust(1).as_markup()
