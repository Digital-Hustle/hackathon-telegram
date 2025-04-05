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


def download_template_keyboard():
    buttons = [
        [InlineKeyboardButton(text="‹ Назад", callback_data="menu")]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def info_keyboard():
    buttons = [
        [InlineKeyboardButton(text="📈 Загрузить и рассчитать", callback_data="calculate")],
        [InlineKeyboardButton(text="‹ Назад", callback_data="menu")]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def calculate_keyboard():
    buttons = [
        [InlineKeyboardButton(text="‹ Назад", callback_data="menu")]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def auth_back_keyboard():
    buttons = [
        [InlineKeyboardButton(text="‹ Назад", callback_data="profile")]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def profile_keyboard(is_login=False):
    if is_login:
        buttons = [
            [InlineKeyboardButton(text="📊 История", callback_data="login")],
            [InlineKeyboardButton(text="🚪 Выйти из аккаунта", callback_data="logout")],
            [InlineKeyboardButton(text="‹ Назад", callback_data="menu")]
        ]
    else:
        buttons = [
            [InlineKeyboardButton(text="👤 Войти", callback_data="login")],
            [InlineKeyboardButton(text="🆕 Зарегестриоваться", callback_data="register")],
            [InlineKeyboardButton(text="‹ Назад", callback_data="menu")]
        ]


    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard