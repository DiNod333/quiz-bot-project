from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder # для кнопок

def generate_options_keyboard(answer_options, right_answer):
    # Создаем сборщика клавиатур типа Inline
    builder = InlineKeyboardBuilder()

    # В цикле создаем 4 Inline кнопки, а точнее Callback-кнопки
    for index, option in enumerate(answer_options):
        # Присваиваем данные для колбэк запроса.
        # Если ответ верный сформируется колбэк-запрос с данными 'right_answer'
        # Иначе сформируется колбэк-запрос с данными 'wrong_answer'
        if option == right_answer:
            is_correct = "right_answer"
        else:
            is_correct = "wrong_answer"

        data = f"{is_correct}|{index}"  # Сохраняем и флаг ответа, и индекс ответа

        builder.add(types.InlineKeyboardButton(
            # Текст на кнопках соответствует вариантам ответов
            text=option,
            callback_data = data)
        )

    # Выводим по одной кнопке в столбик
    builder.adjust(1)
    return builder.as_markup()