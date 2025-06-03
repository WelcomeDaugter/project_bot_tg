from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton
from aiogram import types
def get_help() -> ReplyKeyboardMarkup:
    kb = [
        [
            types.KeyboardButton(text="/help"),
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb, resize_keyboard=True, input_field_placeholder="Выбери /help "
    )
    return keyboard

def help_button() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Цены криптовалют")],
            [KeyboardButton(text="График криптовалют")]
        ],
        resize_keyboard=True, input_field_placeholder="Нажмите нужную кнопку"
    )

def reg() -> ReplyKeyboardMarkup:
    register_keyboard = [
    [
        types.KeyboardButton(text="/reg"),
    ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=register_keyboard, resize_keyboard=True, one_time_keyboard=True, input_field_placeholder="Для продолжения нажмите на кнопку"
    )
    return keyboard