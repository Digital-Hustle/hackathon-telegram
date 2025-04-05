from aiogram.fsm.state import State, StatesGroup


class supportState(StatesGroup):
    message = State()

class uploadFile(StatesGroup):
    message_id = State()
