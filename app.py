import logging
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import TelegramObject, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from typing import Callable, Dict, Any, Awaitable
import uvicorn
from aiogram.types import Update
from dotenv import load_dotenv

# Завантаження змінних середовища
load_dotenv()

# Меню-клавіатура
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Пошук🔍"), KeyboardButton(text="Список серіалів📺"), KeyboardButton(text="За жанром")],
        [KeyboardButton(text="Мультики👱‍♀️"), KeyboardButton(text="Фільми")],
        [KeyboardButton(text="Запросити друга🤜🤛")]
    ],
    resize_keyboard=True
)

API_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
GROUP_CHAT_ID = '-1002591662949'
GROUP_URL = 'https://t.me/proKinotochka'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
app = FastAPI()

subscribe_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔔 Підписатися на групу", url=GROUP_URL)]
])

async def check_subscription(user_id: int) -> bool:
    try:
        chat_member = await bot.get_chat_member(GROUP_CHAT_ID, user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as
