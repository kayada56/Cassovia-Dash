import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import BOT_TOKEN, ADMIN_ID
from database import init_db, add_user, get_all_users
from aiogram.utils.keyboard import ReplyKeyboardBuilder 

bot = Bot(token=BOT_TOKEN)
def main_menu():
    builder = ReplyKeyboardBuilder()
    # Добавляем кнопки в ряд
    builder.row(types.KeyboardButton(text="📊 Мой профиль"))
    builder.row(types.KeyboardButton(text="ℹ️ О проекте"), types.KeyboardButton(text="🆘 Помощь"))
    # Возвращаем готовую клавиатуру, которая подстраивается под экран
    return builder.as_markup(resize_keyboard=True)

dp = Dispatcher()

@dp.message(Command("admin"))
async def admin_stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return 

    users = get_all_users()
    count = len(users)
    
    text = f"📊 **Статистика Cassovia Dash**\n\nВсего пользователей: {count}\n\n"
    for user in users:
        text += f"ID: {user[0]} | @{user[1]} | {user[2]}\n"
    
    await message.answer(text) 
      
@dp.message(Command("start"))
async def start_command(message: types.Message):
    # Логика регистрации
    add_user(message.from_user.id, message.from_user.username)
    
    await message.answer(
        f"Привет, {message.from_user.first_name}!\n"
        "Ты успешно зарегистрирован в Cassovia Dash.",
        reply_markup=main_menu()  # <--- ВОТ ЭТА СТРОКА ОБЯЗАТЕЛЬНА
    )






# 1. Кнопка Профиль
@dp.message(lambda message: "Мой профиль" in message.text)
async def my_profile(message: types.Message):
    await message.answer(
        f"👤 **Профиль пользователя**:\n\n"
        f"🆔 Ваш ID: `{message.from_user.id}`\n"
        f"👤 Имя: {message.from_user.first_name}\n"
        f"🔗 Ник: @{message.from_user.username}"
    )

# 2. Кнопка О проекте
@dp.message(lambda message: "О проекте" in message.text)
async def about_project(message: types.Message):
    await message.answer(
        "🚀 **Cassovia Dash** — это дефолтный помощничек для тебя\n"
        "Разработано специально для мониторинга и удобного доступа к информации."
    )

# 3. Кнопка Помощь
@dp.message(lambda message: "Помощь" in message.text)
async def help_command(message: types.Message):
    await message.answer(
        "🆘 **Поддержка**\n\n"
        "Если есть баг — ждем апдейт хуле 😎\n\n"
        "Команды:\n"
        "/start — Перезапустить меню\n"
        "/admin — Панель управления"
    )

# --- 




async def main():
    init_db()
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен.")

     