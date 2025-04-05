from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import types


def menu_keyboard():
    buttons = [
        [InlineKeyboardButton(text="📈 Загрузить и рассчитать", callback_data="calculate")],
        [InlineKeyboardButton(text="💡 Как это работает?", callback_data="info")],
        [InlineKeyboardButton(text="🛟 Техничесская поддержка", callback_data="support")],
        [InlineKeyboardButton(text="📥 Скачать шаблоны", callback_data="download_template")],
        [InlineKeyboardButton(text="👤 Мой профиль", callback_data="profile")]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def support_keyboard():
    buttons = [
        [InlineKeyboardButton(text="‹ Назад", callback_data="menu")]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard