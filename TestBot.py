from db import create_table, update_quiz_index, get_quiz_index
from handlers import register_handlers

import asyncio

import logging

from aiogram import Bot, Dispatcher #для создания объектов(bot, dispatcher)

logging.basicConfig(level=logging.INFO)

api_token = '7848743698:AAHmT5rBg2slTELeOCQAer9euy86P7GkCG4'

bot = Bot(token=api_token)
dspr = Dispatcher()

async def main():
    # Запускаем создание таблицы базы данных
    await create_table()

    await register_handlers(dspr)

    await dspr.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())