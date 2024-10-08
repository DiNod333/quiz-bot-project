from db import update_quiz_index, get_quiz_index, get_statistics, db
from utils import generate_options_keyboard

import asyncio
from aiogram import types
from aiogram import F # взаимодействие с определёнными кнопками с текстом
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.filters.command import Command #для хэндлеров

# Структура квиза
quiz_data = [
    {
        'question': "Что такое Python?",
        'options': ['Язык программирования', 'Тип данных', 'Музыкальный инструмент', 'Змея на английском'],
        'correct_option': 0
    },
    {
        'question': 'Какой тип данных используется для хранения целых чисел?',
        'options': ['int', 'float', 'str', 'natural'],
        'correct_option': 0
    },
    {
        'question': 'Какой из следующих типов данных в Python является неизменяемым?',
        'options': ['Список (list)', 'Словарь (dict)', 'Множество (set)', 'Кортеж (tuple)'],
        'correct_option': 3
    },
    {
        'question': 'Какую функцию нужно использовать, чтобы вывести что-то на экран?',
        'options': ['input()', 'print()', 'output()', 'echo()'],
        'correct_option': 1
    },
    {
        'question': 'Какое ключевое слово используется для определения функции в Python?',
        'options': ['def', 'function', 'lambda', 'func'],
        'correct_option': 0
    },
    {
        'question': 'Что делает функция input() в Python?',
        'options': ['Выводит текст на экран', 'Прерывает выполнение программы', 'Ожидает ввода данных от пользователя', 'Возвращает случайное число'],
        'correct_option': 2
    },
    {
        'question': 'Какой оператор используется для проверки равенства в Python?',
        'options': ['==', '=', '!=', '<>'],
        'correct_option': 0
    },
    {
        'question': 'Какой модуль используется для работы с файлами в Python?',
        'options': ['file', 'files', 'os', 'filesystem'],
        'correct_option': 2
    },
    {
        'question': 'Что такое lambda-функция в Python?',
        'options': ['Функция, которая возвращает ноль', 'Функция без имени', 'Цикл, который никогда не заканчивается', 'Случайное число'],
        'correct_option': 1
    },
    {
        'question': 'Какое ключевое слово используется для обработки исключений?',
        'options': ['catch', 'try', 'except', 'error'],
        'correct_option': 2
    },
    {
        'question': 'Какой метод используется для добавления элемента в список?',
        'options': ['add()', 'append()', 'insert()', 'push()'],
        'correct_option': 1
    },
    {
        'question': 'Какое ключевое слово используется для создания класса?',
        'options': ['def', 'class', 'object', 'function'],
        'correct_option': 1
    }
]

async def register_handlers(dspr):
    @dspr.message(Command("start"))
    async def cmd_start(message: types.message):
        await message.answer("Привет! Я бот для проведения квиза. Введите /quiz, чтобы начать, или /statistics, для просмотра статистики.")

        # Создаем сборщика клавиатур типа Reply
        builder = ReplyKeyboardBuilder()
        # Добавляем в сборщик одну кнопку
        builder.add(types.KeyboardButton(text="Начать игру"))
        builder.add(types.KeyboardButton(text="Статистика"))
        # Создаём сообщение с привязанным с ней кнопкой
        await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))

    # Хэндлер на команды /quiz
    @dspr.message(F.text=="Начать игру")
    @dspr.message(Command("quiz"))
    async def cmd_quiz(message: types.message):
        # Отправляем новое сообщение без кнопок
        await message.answer(f"Давайте начнем квиз!")
        # Запускаем новый квиз
        await new_quiz(message)

    @dspr.message(F.text=="Статистика")
    @dspr.message(Command("statistics"))
    async def show_statistics(message: types.message):
        statistics = await get_statistics(message.from_user.id)
        # Преобразование статистики в строку для отображения
        stats_text = (
            f"Ваша статистика:\n"
            f"Правильных ответов: {statistics['correct_answers']}\n"
            f"Всего вопросов: {statistics['total_questions']}\n"
            f"Процент правильных ответов: {round((statistics['correct_answers'] / statistics['total_questions']) * 100, 2)}%"
            if statistics['total_questions'] > 0 else "Статистика пуста."
        )
        # Отправляем сообщение с текстом статистики
        await message.answer(stats_text)

    @dspr.callback_query()
    async def handle_answer(callback: types.CallbackQuery):
        # редактируем текущее сообщение с целью убрать кнопки (reply_markup=None)
        await callback.bot.edit_message_reply_markup(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            reply_markup=None
        )

        correct_answers = 0  # Счётчик правильных ответов
        total_questions = len(quiz_data)  # Общее количество вопросов

        callback_data = callback.data.split("|")
        answer_flag = callback_data[0] # "right_answer" или "wrong_answer"
        
        user_answer_index = int(callback_data[1])  # Индекс выбранного пользователем ответа

        # Получение текущего вопроса для данного пользователя
        current_question_index = await get_quiz_index(callback.from_user.id)

        user_answer = quiz_data[current_question_index]['options'][user_answer_index]

        # Сообщаем, какой ответ был выбран
        await callback.message.answer(f"Вы выбрали: {user_answer}")

        # Получаем текущую статистику
        statistics = await get_statistics(callback.from_user.id)
        correct_answers = statistics['correct_answers']  # Получаем количество правильных ответов
        total_questions = statistics['total_questions']  # Всего вопросов

        if answer_flag == "right_answer":
            await callback.message.answer("Верно!")
            correct_answers += 1
        else:
            correct_option = quiz_data[current_question_index]['correct_option']
            correct_answer = quiz_data[current_question_index]['options'][correct_option]
            await callback.message.answer(f"Неправильно. Правильный ответ: {correct_answer}")

        # Обновление индекса вопроса в БД
        current_question_index += 1
        await update_quiz_index(callback.from_user.id, current_question_index, correct_answers, total_questions)

        # Проверяем достигнут ли конец квиза
        if current_question_index < len(quiz_data):
            # Следующий вопрос
            await get_question(callback.message, callback.from_user.id)
        else:
            # Уведомление об окончании квиза
            await callback.message.answer("Это был последний вопрос. Квиз завершен!")
            if db is not None:
                await db.close()

async def new_quiz(message):
    # получаем id пользователя, отправившего сообщение
    user_id = message.from_user.id

    # Инициализируем текущий индекс вопроса в 0
    current_question_index = 0
    correct_answers = 0  # Сброс количества правильных ответов
    total_questions = len(quiz_data)  # Общее количество вопросов в квизе
    await update_quiz_index(user_id, current_question_index, correct_answers, total_questions)

    # запрашиваем новый вопрос для квиза
    await get_question(message, user_id)

async def get_question(message, user_id):

    # Запрашиваем из базы текущий индекс для вопроса
    current_question_index = await get_quiz_index(user_id)
    # Получаем индекс правильного ответа для текущего вопроса
    correct_index = quiz_data[current_question_index]['correct_option']
    # Получаем список вариантов ответа для текущего вопроса
    opts = quiz_data[current_question_index]['options']

    # Функция генерации кнопок для текущего вопроса квиза
    # В качестве аргументов передаем варианты ответов и значение правильного ответа (не индекс!)
    kb = generate_options_keyboard(opts, opts[correct_index])
    # Отправляем в чат сообщение с вопросом, прикрепляем сгенерированные кнопки
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)