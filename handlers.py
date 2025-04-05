from aiogram import F, Router
from aiogram.enums import ContentType
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
from states import *
from config import *
from keyboards import *
router = Router()


@router.message(Command('start'))
async def start_handler(message: types.Message, state: FSMContext) -> None:
    try:
        await state.clear()
        user_id = message.from_user.id
        await message.reply("kuku", reply_markup=menu_keyboard())

    except Exception as e:
        await error_handler(user_id, e)


@router.message(F.text.in_(['👤 Мой профиль', '👤 My profile']))
async def show_profile(message: types.Message, state: FSMContext) -> None:
    try:
        await message.delete()
    except:
        pass
    await state.clear()
    ###

async def error_handler(user_id: int, message: types.Message) -> None:
    await bot.send_message(user_id, message.text)