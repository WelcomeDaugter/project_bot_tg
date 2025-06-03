import asyncio
from aiogram import Router, types, html, F
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from keyboards.keyboard import get_help, help_button, reg
from handlers.middleware import RegistrationMiddleware
from aiogram.fsm.state import StatesGroup, State
import re
from bd import get_db_connection, is_registered
import hashlib
import sqlite3

common_router = Router()

@common_router.message(Command("start"))
async def cmd_start(message: types.Message):
    if not await is_registered(message.from_user.id):
        await message.answer(
            f"Привет, для начала зарегистрируйся",
            parse_mode=ParseMode.HTML,
            reply_markup=reg()
        )
    else:
        await message.answer(f"Напиши /menu, чтобы продолжить")

class RegisterState(StatesGroup):
    username = State()
    password = State()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@common_router.message(F.text == "Зарегистрироваться")
@common_router.message(Command("reg"))
async def start_register(message: Message, state: FSMContext):
    await message.answer(f"Придумайте username:")
    await state.set_state(RegisterState.username)

@common_router.message(RegisterState.username)
async def register_name(message: Message, state: FSMContext):
    username = message.text

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            await message.answer("❌ Этот username уже занят. Выберите другой.")
            return

    await state.update_data(username=username)
    await message.answer(
        f"👾 Отлично! Твой username: {username}\n"
        f"🔑 Теперь придумай пароль:\n"
        f"- Не менее 8 символов\n"
        f"- Хотя бы 1 цифра"
    )
    await state.set_state(RegisterState.password)

@common_router.message(RegisterState.password)
async def register_password(message: Message, state: FSMContext):
    password = message.text
    data = await state.get_data()

    if len(password) < 8:
        await message.answer("❌ Пароль слишком короткий! Нужно минимум 8 символов")
        return

    if not re.search(r'\d', password):
        await message.answer("❌ В пароле должна быть хотя бы 1 цифра!")
        return

    await state.update_data(password=password)

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (user_id, username, password) VALUES (?, ?, ?)",
                (message.from_user.id, data['username'], hash_password(password))
            )
            conn.commit()

        await state.update_data(password=password)
        data = await state.get_data()
        reg_name = data.get("username")
        reg_password = data.get("password")

        await message.answer(
            "🎉 Регистрация завершена!\n"
            f" Username: {reg_name}\n"
            f" Password: {'*' * len(reg_password)}",
            reply_markup=ReplyKeyboardRemove()
        )
        await asyncio.sleep(1)
        await message.answer("Напиши /menu, чтобы продолжить")

    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: users.user_id" in str(e):
            await message.answer("❌ Вы уже зарегистрированы! Используйте /start")
        elif "UNIQUE constraint failed: users.username" in str(e):
            await message.answer("❌ Этот username уже занят! Начните заново /reg")
        else:
            await message.answer("❌ Ошибка базы данных. Попробуйте позже.")

    await state.clear()

@common_router.message(Command("menu"))
async def cmd_menu(message: types.Message):
    if await is_registered(message.from_user.id):
        await message.answer(
            f"Эй, приветствую тебя {html.bold(html.quote(message.from_user.full_name))}!",
            parse_mode=ParseMode.HTML
        )
        await asyncio.sleep(1)
        await message.answer(
            "Нажми на «/help», чтобы узнать мои возможности",
            reply_markup=get_help()
        )
    else:
        await message.answer("Для начала пройдите регистрацию /reg")

@common_router.message(Command("help"))
async def cmd_help(message: Message):
    if await is_registered(message.from_user.id):
        await asyncio.sleep(1)
        await message.answer(
            "Выберите действие:",
            reply_markup=help_button()
        )
    else:
        await message.answer("Для начала пройдите регистрацию /reg")

@common_router.message(lambda message: message.text == "Цены криптовалют")
async def handle_crypto_price_button(message: Message, state: FSMContext):
    from handlers.crypto import price_command
    await price_command(message, state)