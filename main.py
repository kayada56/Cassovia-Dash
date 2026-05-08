import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import BOT_TOKEN, ADMIN_ID
from database import init_db, add_user, get_all_users
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext 

bot = Bot(token=BOT_TOKEN)

class TicketState(StatesGroup):
    waiting_for_text = State()

def main_menu():
    builder = ReplyKeyboardBuilder()
    # Добавляем кнопки в ряд
    builder.row(types.KeyboardButton(text="📊 Мой профиль"))
    builder.row(types.KeyboardButton(text="📝 Оставить тикет на починку/добавление"))
    builder.row(types.KeyboardButton(text="ℹ️ О проекте"), types.KeyboardButton(text="🆘 Помощь"))
    # Возвращаем готовую клавиатуру, которая подстраивается под экран
    return builder.as_markup(resize_keyboard=True)

dp = Dispatcher()



@dp.message(Command("done"))
async def complete_ticket(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    args = message.text.split()
    if len(args) < 2:
        await message.answer("⚠️ Напишите ID тикета: `/done 1`")
        return

    ticket_id = args[1]

    import sqlite3
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    
    cursor.execute("SELECT user_id, text, status FROM tickets WHERE id = ?", (ticket_id,))
    ticket_data = cursor.fetchone()
    
    if not ticket_data:
        await message.answer("❌ Тикет вообще не найден в базе.")
        conn.close()
        return

    user_id, ticket_text, status = ticket_data

    
    if status == 'Closed':
        await message.answer(f"⚠️ Тикет **#{ticket_id}** уже был закрыт ранее!")
        conn.close()
        return

    # Если дошли сюда — значит он Open. Закрываем!
    from database import close_ticket
    close_ticket(ticket_id)
    conn.close()

    try:
        await bot.send_message(user_id, f"✅ Ваша заявка выполнена: _{ticket_text}_")
    except:
        pass

    await message.answer(f"✅ Тикет **#{ticket_id}** закрыт, юзер уведомлен!")

    
    try:
        await bot.send_message(
            user_id, 
            f"✅ **Ваша заявка исполнена!**\n\n"
            f"Заявка: _{ticket_text}_\n"
            f"всё готово. Спасибо за фидбек! 😎"
        )
    except Exception as e:
        print(f"Не удалось отправить уведомление юзеру: {e}")

    await message.answer(f"✅ Тикет **#{ticket_id}** закрыт, юзер уведомлен!")

@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    from database import get_stats
    total_users, total_tickets, open_tickets = get_stats()

    text = (
        "🖥 **Панель управления Cassovia Dash**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 Всего пользователей: `{total_users}`\n"
        f"📝 Всего заявок: `{total_tickets}`\n"
        f"⏳ В ожидании (Open): `{open_tickets}`\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 Используйте `/send`, чтобы сделать рассылку."
    )
    
    await message.answer(text, parse_mode="Markdown")


@dp.message(Command("tickets"))
async def view_tickets(message: types.Message):
    # Проверка на админа
    if message.from_user.id != ADMIN_ID:
        return
    
    import sqlite3
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, user_id, text FROM tickets WHERE status = 'Open' ORDER BY id DESC LIMIT 10")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await message.answer("✅ Новых заявок пока нет.")
        return

    res = "📩 **Список активных заявок:**\n"
    res += "━━━━━━━━━━━━━━━━━━━━\n"
    for row in rows:
        res += f"🆔 **Тикет #{row[0]}**\n📝 {row[2]}\n\n"
    
    await message.answer(res)

      
@dp.message(Command("start"))
async def start_command(message: types.Message):
    # Логика регистрации
    add_user(message.from_user.id, message.from_user.username)
    
    await message.answer(
        f"Привет, {message.from_user.first_name}!\n"
        "Ты успешно зарегистрирован в Cassovia Dash.",
        reply_markup=main_menu()  # <--- ВОТ ЭТА СТРОКА ОБЯЗАТЕЛЬНА
    )


@dp.message(lambda message: "Оставить тикет на починку/добавление" in message.text)
async def start_ticket(message: types.Message, state: FSMContext):
    await message.answer("Опишите ваш баг или предложение одним сообщением:")
    await state.set_state(TicketState.waiting_for_text)



@dp.message(TicketState.waiting_for_text)
async def process_ticket(message: types.Message, state: FSMContext):
    from database import add_ticket 
    
    add_ticket(message.from_user.id, message.text) # Сохраняем в БД
    
    
    await bot.send_message(ADMIN_ID, f"🔔 **Новая заявка!**\nОт: @{message.from_user.username}\nТекст: {message.text}")
    
    await message.answer("✅ Ваша заявка принята! Админ скоро её рассмотрит.")
    await state.clear()


@dp.message(Command("send"))
async def broadcast(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    # Извлекаем текст после команды /send
    broadcast_text = message.text.replace("/send", "").strip()
    
    if not broadcast_text:
        await message.answer("⚠️ Введите текст рассылки: `/send Всем привет!`", parse_mode="Markdown")
        return

    import sqlite3
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users")
    users = cursor.fetchall()
    conn.close()

    count = 0
    for user in users:
        try:
            await bot.send_message(user[0], f"📢 **Объявление от Cassovia Dash:**\n\n{broadcast_text}", parse_mode="Markdown")
            count += 1
        except Exception:
            pass # Если юзер заблокировал бота, просто пропускаем

    await message.answer(f"✅ Рассылка завершена! Сообщение получили {count} пользователей.")



# 1. Кнопка Профиль
@dp.message(lambda message: "Мой профиль" in message.text)
async def my_profile(message: types.Message):
    print(f"[LOG] Юзер @{message.from_user.username} чекнул профиль")
    await message.answer(
        f"👤 **Профиль пользователя**:\n\n"
        f"🆔 Ваш ID: `{message.from_user.id}`\n"
        f"👤 Имя: {message.from_user.first_name}\n"
        f"🔗 Ник: @{message.from_user.username}"
    )

# 2. Кнопка О проекте
@dp.message(lambda message: "О проекте" in message.text)
async def about_project(message: types.Message):
    text = (
        "🚀 **Cassovia Dash** — это помощник для тебя.\n"
        "Разработано специально для мониторинга и удобного доступа к информации.\n\n"
        "👉 [Перейти на официальный канал](https://t.me/+NS-VLiX_izU2NTFi)\n"
        "📦 [GitHub проекта](https://github.com/kayada56/Cassovia-Dash)"
    )
    
    
    await message.answer(
        text, 
        parse_mode="Markdown", 
        disable_web_page_preview=True
    )

# 3. Кнопка Помощь
@dp.message(lambda message: "Помощь" in message.text)
async def help_command(message: types.Message):
    await message.answer(
        "🆘 **Поддержка**\n\n"
        "Если есть баг — ждем апдейт хуле 😿\n\n"
        "Команды:\n"
        "/start — Перезапустить меню\n"
        "оставьте свой тикет в главном меню"
    )


@dp.message()
async def echo_all(message: types.Message):
    await message.answer(
        "Пожалуйста, воспользуйся кнопками в меню ниже!",
        reply_markup=main_menu() 
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

     