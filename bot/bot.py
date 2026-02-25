import os

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

from bot.qr import QR


class TelegramBot:
    def __init__(self):
        load_dotenv()
        token = os.getenv("BOT_TOKEN")
        if not token:
            raise "Get BOT_TOKEN error!"

        self.bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

        self.qr = QR(self.bot)
