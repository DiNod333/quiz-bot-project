import asyncio

import aiosqlite

db = None

async def create_table():
    global db
    # Создаем соединение с базой данных (если она не существует, то она будет создана)
    db = await aiosqlite.connect('quiz_bot.db')
    # Выполняем SQL-запрос к базе данных
    await db.execute('''
            CREATE TABLE IF NOT EXISTS quiz_state (
                user_id INTEGER PRIMARY KEY,
                question_index INTEGER,
                correct_answers INTEGER DEFAULT 0,
                total_questions INTEGER DEFAULT 0,
                last_score INTEGER DEFAULT 0
            )
    ''')
    # Сохраняем изменения
    await db.commit()

async def update_quiz_index(user_id, index, correct_answers, total_questions):
    # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
    await db.execute('''
        INSERT OR REPLACE INTO quiz_state (
            user_id,
            question_index,
            correct_answers,
            total_questions
        ) VALUES (?, ?, ?, ?)''', (user_id, index, correct_answers, total_questions)
    )
    # Сохраняем изменения
    await db.commit()

async def get_quiz_index(user_id): # получаем текущий индекс вопроса из БД
    # Получаем запись для заданного пользователя
    async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id,)) as cursor:
        # Возвращаем результат
        result = await cursor.fetchone()
        if result is not None:
            return result[0]
        else:
            return 0

async def get_statistics(user_id):
    async with db.execute('SELECT correct_answers, total_questions FROM quiz_state WHERE user_id = ?', (user_id,)) as cursor:
        result = await cursor.fetchone()
        if result is not None:
            return{
                'correct_answers': result[0],
                'total_questions': result[1]
            }
        else:
            return {
                'correct_answers': 0,
                'total_questions': 0
            }