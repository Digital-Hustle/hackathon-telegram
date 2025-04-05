from aiogram import F, Router
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.enums import ContentType
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
from states import *
from config import *
from keyboards import *
router = Router()


@router.message(Command('start'))
async def start_handler(message: types.Message=None, callback_query: types.CallbackQuery=None, state: FSMContext=None,) -> None:
    try:
        await state.clear()
        caption = '<b>⌛️Экономьте как никогда ранее</b>\n\nБыстро рассчитайте нужные и максимально выгодные тарифы. Прощай волокита! 👋'
        if message:
            await message.delete()
            user_id = message.from_user.id
            await message.answer(caption, reply_markup=menu_keyboard())
        if callback_query:
            user_id = callback_query.from_user.id
            await callback_query.message.edit_text(caption, reply_markup=menu_keyboard())

    except Exception as e:
        await error_handler(user_id, e)


@router.callback_query(lambda c: c.data == "menu")
async def menu_callback(callback_query: types.callback_query, state: FSMContext) -> None:
    await start_handler(state=state, callback_query=callback_query)


@router.callback_query(lambda c: c.data == "download_template")
async def download_template_callback(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    await callback_query.message.delete()
    try:
        media_group = MediaGroupBuilder()

        media_group.add_document(
            media=VERTICAL_TEMPLATE_FILE_ID,
            caption="Вертикальный шаблон"
        )
        media_group.add_document(
            media=HORIZONTAL_TEMPLATE_FILE_ID,
            caption="Горизонтальный шаблон"
        )

        await callback_query.message.answer_media_group(
            media=media_group.build()
        )

        await callback_query.message.answer(
            "✅ Шаблоны успешно отправлены!",
            reply_markup=download_template_keyboard()
        )

        await callback_query.answer()

    except Exception as e:
        await error_handler(callback_query.from_user.id, e)


@router.callback_query(lambda c: c.data == "support")
async def support_handler(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    try:
        await state.set_state(supportState.message)
        user_id = callback_query.from_user.id
        await callback_query.message.edit_text("<b>🛟 Техническая поддержка</b>\n\nНапишите интересующий Вас вопрос. Наша команда постарается ответить в самое ближайшее время.", reply_markup=support_keyboard())
    except Exception as e:
        await error_handler(user_id, e)


@router.callback_query(lambda c: c.data == "info")
async def info_handler(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    try:
        await state.set_state(supportState.message)
        user_id = callback_query.from_user.id
        await callback_query.message.edit_text("<b>💡 Как это работает?</b>\n\n1) Вы загружаете файл с вашим деталями потреблением электроэнергии\n2) Мы рассчитываем и предлагаем для Вас наиболее выгодный тариф\n3) Вы можете войти в свой личный кабинет для сохранения рассчетов", reply_markup=info_keyboard())
    except Exception as e:
        await error_handler(user_id, e)


@router.callback_query(lambda c: c.data == "calculate")
async def calculate_handler(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    try:
        await state.set_state(uploadFile.message_id)
        await state.update_data(message_id=callback_query.message.message_id)

        user_id = callback_query.from_user.id
        await callback_query.message.edit_text("<b>💡 Отправьте файл с Вашими данными?</b>\n\nФайл обязательно должен быть формата .xlsx", reply_markup=calculate_keyboard())
    except Exception as e:
        await error_handler(user_id, e)


@router.message(F.document, StateFilter(uploadFile.message_id))
async def state_upload_file(message: types.Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    await message.delete()
    try:
        document = message.document
        file_name = document.file_name
        file_ext = os.path.splitext(file_name)[1].lower() if file_name else None

        state_data = await state.get_data()
        message_id = state_data.get('message_id')

        ALLOWED_EXTENSIONS = ['.xlsx', '.xml']
        if file_ext not in ALLOWED_EXTENSIONS:
            await bot.edit_message_text(chat_id=user_id, message_id=message_id, text="<b>❌ Ошибка: Недопустимый формат файла.</b>\n\nРазрешены только .xlsx и .xml. Попробуйте еще раз:", reply_markup=calculate_keyboard())
            return

        if message_id:
            await bot.edit_message_text(
                chat_id=user_id,
                message_id=message_id,
                text="🚀 Файл получен, начинаю загрузку..."
            )

        file_path = os.path.join(DOWNLOAD_DIR, file_name)
        file = await bot.get_file(document.file_id)
        await bot.download_file(file.file_path, file_path)

        if message_id:
            await bot.edit_message_text(
                chat_id=user_id,
                message_id=message_id,
                text=f"✅ Файл успешно загружен: {file_name}\n\nОтправляю на обработку..."
            )

        # отправка на бэкэнд
        # await send_to_backend(file_path)

    except Exception as e:
        await error_handler(user_id, e)
        await message.reply("⚠ Произошла ошибка при обработке файла")


@router.message(F.text, StateFilter(supportState.message))
async def state_files(message: types.Message, state: FSMContext) -> None:
    try:
        message_id_to_reply = message.message_id
        message_text = message.text
        user_name = message.from_user.first_name
        user_id = message.from_user.id
        await bot.send_message(ADMIN_ID, f"<b>✉️ Пришло сообщение от </b>{user_name}\n\n<code>{message_text}</code>\n\nДля ответа на сообщение - ответьте на это сообщение\n\n#{message_id_to_reply}, #{user_id}")
        await message.answer("<b>⚡️ Сообщение отправлено.</b>\n\nСкоро ответим!")
    except Exception as e:
        await error_handler(user_id, e)


async def error_handler(user_id: int, e: str) -> None:
    print(f"Произошла ошибка у {user_id}\n{e}")
    await bot.send_message(user_id, "<b>🤪 Произошло ошибка в обработке вашего запроса</b>\n\nИспользуйте новое меню:", reply_markup=menu_keyboard())


@router.message(F.text)
async def handle_all_messages(message: types.Message):
    if str(message.from_user.id) == str(ADMIN_ID):
        if message.reply_to_message:
            try:
                reply_text = message.reply_to_message.text
                lines = reply_text.split('\n')
                last_line = lines[-1].strip()

                tags = last_line.split(', ')
                if len(tags) >= 2 and tags[0].startswith('#') and tags[1].startswith('#'):
                    original_message_id = int(tags[0][1:])
                    user_id = int(tags[1][1:])

                    await message.bot.send_message(
                        chat_id=user_id,
                        text=f"<b>📨 Ответ от поддержки:</b>\n\n{message.text}",
                        reply_to_message_id=original_message_id
                    )
                    await message.reply("✅ Ответ отправлен пользователю")
                else:
                    await message.reply("⚠ Не удалось распознать ID сообщения и пользователя")
            except Exception as e:
                await message.reply(f"⚠ Ошибка при отправке ответа: {str(e)}")
        else:
            pass
    else:
        message_id_to_reply = message.message_id
        message_text = message.text
        user_name = message.from_user.first_name
        user_id = message.from_user.id
        await bot.send_message(ADMIN_ID,
                               f"<b>✉️ Пришло сообщение от </b>{user_name}\n\n<code>{message_text}</code>\n\nДля ответа на сообщение - ответьте на это сообщение\n\n#{message_id_to_reply}, #{user_id}")
        await message.answer("<b>⚡️ Сообщение отправлено.</b>\n\nСкоро ответим!")