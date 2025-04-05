from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from typing import Callable, Awaitable, Dict, Any
from cachetools import TTLCache
from funcs import insert_new_user

class AntiFloodMiddleware(BaseMiddleware):
    def __init__(self, time_limit: int = 5) -> None:
        self.limit = TTLCache(maxsize=10_000, ttl=time_limit)
        self.counter = TTLCache(maxsize=10_000, ttl=time_limit)

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, Message):
            chat_id = event.chat.id
        elif isinstance(event, CallbackQuery):
            chat_id = event.message.chat.id
        else:
            return await handler(event, data)

        if chat_id in self.limit:
            if self.counter[chat_id] >= 5:
                return
            else:
                self.counter[chat_id] += 1
        else:
            self.limit[chat_id] = None
            self.counter[chat_id] = 1

        return await handler(event, data)


class CheckNewUser(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]) -> Any:

        user_id = event.from_user.id
        is_it_new = await insert_new_user(user_id)
        data["is_it_new"] = is_it_new

        return await handler(event, data)