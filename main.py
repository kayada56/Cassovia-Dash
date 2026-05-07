import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import BOT_TOKEN
from database import init_db, add_user

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    # Логика регистрации
    add_user(message.from_user.id, message.from_user.username)
    
    await message.answer(
        f"Привет, {message.from_user.first_name}!\n"
        "Ты успешно зарегистрирован в Cassovia Dash."
    )

async def main():
    init_db()
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен.")