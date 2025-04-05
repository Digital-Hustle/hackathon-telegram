from aiogram.fsm.state import State, StatesGroup


class supportState(StatesGroup):
    message = State()

class uploadFile(StatesGroup):
    message_id = State()

class register(StatesGroup):
    login = State()
    password = State()
    password_confirm = State()

class login(StatesGroup):
    login = State()
    password = State()

class admin(StatesGroup):
    message_id = State()