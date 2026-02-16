import asyncio
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import database as db
from handlers import router

load_dotenv()

async def main():
    # Инициализация БД
    await db.init_db()
    
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()
    
    dp.include_router(router)

    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")