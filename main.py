import logging
import sys
import asyncio

from aiogram.methods import DeleteWebhook
from handlers import router
from middlewares import *
from config import dp, bot, SUPPORT_CHAT_ID

dp.include_router(router)


async def main() -> None:
    dp.message.middleware(AntiFloodMiddleware())
    dp.callback_query.middleware(AntiFloodMiddleware())
    dp.message.middleware(CheckNewUser())
    dp.callback_query.middleware(CheckNewUser())

    try:
        await bot(DeleteWebhook(drop_pending_updates=True))
        await bot.send_message(chat_id=SUPPORT_CHAT_ID, text='<b>❇️ Бот включен.</b>')
        print("Бот успешно запустился")
        await dp.start_polling(bot, skip_updates=True)
    except Exception as e:
        logging.exception("Ошибка при запуске бота")
        await shutdown()
        raise


async def shutdown() -> None:
    try:
        await bot.send_message(chat_id=SUPPORT_CHAT_ID, text='<b>🚫 Бот выключен.</b>')
    except Exception as e:
        logging.warning(f"Не удалось отправить сообщение о выключении: {e}")

    try:
        await dp.stop_polling()
    except Exception as e:
        logging.warning(f"Ошибка при остановке polling: {e}")

    try:
        await bot.session.close()
    except Exception as e:
        logging.warning(f"Ошибка при закрытии сессии: {e}")

    print("Бот завершил работу.")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        asyncio.run(shutdown())
    except Exception as e:
        logging.exception("Необработанное исключение")
        asyncio.run(shutdown())