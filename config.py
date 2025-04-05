from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv, find_dotenv
import os


storage = MemoryStorage()
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')
IP = 'http://10.165.8.60:8080'
BASE_URL = IP+'/api/v1'

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

VERTICAL_TEMPLATE_FILE_ID = "BQACAgIAAxkBAAOjZ_EZ4z4F6-1ADoQGsh0Y0ZfDaHAAAttsAAJUqYlLcI92w9JO51Y2BA"
HORIZONTAL_TEMPLATE_FILE_ID = "BQACAgIAAxkBAAOlZ_EZ7TZHfaB0gokJ3MqfNKL2q9MAAtxsAAJUqYlLvB9lOjo9UD02BA"

bot = Bot(token=str(TELEGRAM_BOT_TOKEN), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=storage)