from aiogram import F, Router
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from states import *
from config import *
from keyboards import *
from funcs import *


router = Router()


@router.message(Command('start'))
async def start_handler(message: types.Message=None, callback_query: types.CallbackQuery=None, state: FSMContext=None,) -> None:
    try:
        await state.clear()
        caption = '<b>⌛️Экономьте как никогда раньше</b>\n\nБыстро рассчитайте нужные и максимально выгодные тарифы. Прощай волокита! 👋'
        if message:
            await message.delete()
            user_id = message.from_user.id
            await message.answer(caption, reply_markup=await menu_keyboard(user_id))
        if callback_query:
            user_id = callback_query.from_user.id
            await callback_query.message.edit_text(caption, reply_markup=await menu_keyboard(user_id))

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


@router.callback_query(lambda c: c.data == "profile")
async def profile_handler(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    try:
        if await check_login(callback_query.from_user.id):
            title = '<b>👤 Ваш профиль</b>\n\nЗдесь вы можете посмотреть историю своих расчетов.'
            is_login=True
        else:
            title = '<b>👤 Ваш профиль</b>\n\nПохоже вы еще не вошли в свой личный кабинет. Войдите, чтобы иметь возможность сохранять свои расчеты.'
            is_login=False

        await state.set_state(supportState.message)
        user_id = callback_query.from_user.id
        await callback_query.message.edit_text(title, reply_markup=profile_keyboard(is_login=is_login))
    except Exception as e:
        await error_handler(user_id, e)


@router.callback_query(lambda c: c.data == "register")
async def register_handler(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    try:
        await state.set_state(register.login)
        user_id = callback_query.from_user.id
        await callback_query.message.edit_text(
            "<b>🔐 Регистрация</b>\n\nВведите ваш логин:",
            reply_markup=auth_back_keyboard()
        )
        await state.update_data(message_id=callback_query.message.message_id)
    except Exception as e:
        await error_handler(user_id, e)


@router.message(StateFilter(register.login))
async def register_login_handler(message: types.Message, state: FSMContext) -> None:
    try:
        await state.update_data(login=message.text)
        await state.set_state(register.password)
        state_data = await state.get_data()
        message_id = state_data.get('message_id')
        await bot.edit_message_text(
            chat_id=message.from_user.id,
            message_id=message_id,
            text="<b>🔐 Регистрация</b>\n\nВведите ваш пароль:",
            reply_markup=auth_back_keyboard()
        )
        await message.delete()
    except Exception as e:
        await error_handler(message.from_user.id, e)


@router.message(StateFilter(register.password))
async def register_password_handler(message: types.Message, state: FSMContext) -> None:
    try:
        await state.update_data(password=message.text)
        await state.set_state(register.password_confirm)
        state_data = await state.get_data()
        message_id = state_data.get('message_id')
        await bot.edit_message_text(
            chat_id=message.from_user.id,
            message_id=message_id,
            text="<b>🔐 Регистрация</b>\n\nПовторите ваш пароль:",
            reply_markup=auth_back_keyboard()
        )
        await message.delete()
    except Exception as e:
        await error_handler(message.from_user.id, e)


@router.message(StateFilter(register.password_confirm))
async def register_password_confirm_handler(message: types.Message, state: FSMContext) -> None:
    try:
        await state.update_data(password_confirm=message.text)
        data = await state.get_data()
        message_id = data.get('message_id')

        if await register_user(data['login'], data['password'], message.text):
            await bot.edit_message_text(
                chat_id=message.from_user.id,
                message_id=message_id,
                text="<b>✅ Регистрация завершена!</b>\n\nДля входа используйте эти же данные.",
                reply_markup=await menu_keyboard(message.from_user.id)
            )
        else:
            await bot.edit_message_text(
                chat_id=message.from_user.id,
                message_id=message_id,
                text="<b>❌ Регистрация неуспешна!</b>\n\nПароль должен быть от 5 до 255 символов.",
                reply_markup=await menu_keyboard(message.from_user.id)
            )
        await state.clear()
    except Exception as e:
        await error_handler(message.from_user.id, e)


@router.callback_query(lambda c: c.data == "login")
async def login_handler(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    try:
        await state.set_state(login.login)
        user_id = callback_query.from_user.id
        await callback_query.message.edit_text(
            "<b>🔐 Вход в аккаунт</b>\n\nВведите ваш логин:",
            reply_markup=auth_back_keyboard()
        )
        await state.update_data(message_id=callback_query.message.message_id)
    except Exception as e:
        await error_handler(user_id, e)


@router.message(StateFilter(login.login))
async def login_login_handler(message: types.Message, state: FSMContext) -> None:
    try:
        await state.update_data(login=message.text)
        await state.set_state(login.password)
        state_data = await state.get_data()
        message_id = state_data.get('message_id')
        await bot.edit_message_text(
            chat_id=message.from_user.id,
            message_id=message_id,
            text="<b>🔐 Вход в аккаунт</b>\n\nВведите ваш пароль:",
            reply_markup=auth_back_keyboard()
        )
        await message.delete()
    except Exception as e:
        await error_handler(message.from_user.id, e)


@router.message(StateFilter(login.password))
async def login_password_handler(message: types.Message, state: FSMContext) -> None:
    try:
        await state.update_data(password=message.text)
        data = await state.get_data()
        message_id = data.get('message_id')

        if await auth_user(message.from_user.id, data['login'], data['password']):
            await bot.edit_message_text(
                chat_id=message.from_user.id,
                message_id=message_id,
                text="<b>✅ Вход успешен!</b>\n\nТеперь у вас открыты все возможности!",
                reply_markup=await menu_keyboard(message.from_user.id)
            )
        else:
            await bot.edit_message_text(
                chat_id=message.from_user.id,
                message_id=message_id,
                text="<b>❌ Вход неуспешен!</b>\n\nНеверный логин или пароль",
                reply_markup=await menu_keyboard(message.from_user.id)
            )
        await state.clear()
        await message.delete()
    except Exception as e:
        await error_handler(message.from_user.id, e)


@router.callback_query(lambda c: c.data == "logout")
async def logout_handler(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    try:
        user_id = callback_query.from_user.id
        await user_logout(user_id)
        await callback_query.message.edit_text(
            "<b>✅ Вы успешно вышли из аккаунта</b>\n\nЗаходите ещё.",
            reply_markup=auth_back_keyboard()
        )
    except Exception as e:
        await error_handler(user_id, e)


@router.callback_query(lambda c: c.data == "admin_panel")
async def admin_panel_handler(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    try:
        user_id = callback_query.from_user.id
        if await check_admin(user_id):
            await callback_query.message.edit_text("<b>Админ панель</b>\n\nЗдесь Вы можете назначать новых админов, а такжу загружать новые таблицы.", reply_markup=admin_panel_keyboard())
    except Exception as e:
        await error_handler(user_id, e)


@router.callback_query(lambda c: c.data == "admin_handler")
async def admin_handler(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    try:
        user_id = callback_query.from_user.id
        if await check_admin(user_id):
            await callback_query.message.edit_text("<b>✨ Назначение и удаление админов</b>\n\nВведите логин:", reply_markup=admin_panel_keyboard())
            await state.set_state(admin.message_id)
            await state.update_data(message_id=callback_query.message.message_id)
    except Exception as e:
        await error_handler(user_id, e)


# @router.message(F.text, StateFilter(admin.message_id))
# async def admin_role_handler(message: types.Message, state: FSMContext) -> None:
#     try:
#         if await check_admin(message.from_user.id):
#             # login = message.text
#             # запрос к бэкэнду для проверки текущего статуса
#             # status = ...
#             # state_data = await state.get_data()
#             # message_id = state_data.get('message_id')
#             # await bot.edit_message_text("<b>🎬 Выберите действие:</b>", reply_markup=admin_role_handler_handler(status))
#             # await state.clear()
#     except Exception as e:
#         await error_handler(user_id, e)


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
        try:
            if file_ext not in ALLOWED_EXTENSIONS:
                await bot.edit_message_text(chat_id=user_id, message_id=message_id, text="<b>❌ Ошибка: Недопустимый формат файла.</b>\n\nРазрешены только .xlsx и .xml. Попробуйте еще раз:", reply_markup=calculate_keyboard())
                return
        except:
            pass

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
        await bot.send_message(SUPPORT_CHAT_ID, f"<b>✉️ Пришло сообщение от </b>{user_name}\n\n<code>{message_text}</code>\n\nДля ответа на сообщение - ответьте на это сообщение\n\n#{message_id_to_reply}, #{user_id}")
        await message.answer("<b>⚡️ Сообщение отправлено.</b>\n\nСкоро ответим!")
    except Exception as e:
        await error_handler(user_id, e)


async def error_handler(user_id: int, e: str) -> None:
    print(f"Произошла ошибка у {user_id}\n{e}")
    await bot.send_message(user_id, "<b>🤪 Произошло ошибка в обработке вашего запроса</b>\n\nИспользуйте новое меню:", reply_markup=await menu_keyboard(user_id))


@router.message(F.text)
async def handle_all_messages(message: types.Message):
    if await check_admin(message.from_user.id):
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
        await bot.send_message(SUPPORT_CHAT_ID,
                               f"<b>✉️ Пришло сообщение от </b>{user_name}\n\n<code>{message_text}</code>\n\nДля ответа на сообщение - ответьте на это сообщение\n\n#{message_id_to_reply}, #{user_id}")
        await message.answer("<b>⚡️ Сообщение отправлено.</b>\n\nСкоро ответим!")