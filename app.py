import logging
import os
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import TelegramObject, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from typing import Callable, Dict, Any, Awaitable
import uvicorn

# Змінні середовища
API_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
GROUP_CHAT_ID = '-1002591662949'
GROUP_URL = 'https://t.me/proKinotochka'

# Логування
logging.basicConfig(level=logging.INFO)

# Ініціалізація
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
app = FastAPI()

# Клавіатура
subscribe_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔔 Підписатися на групу", url=GROUP_URL)]
])

# Перевірка підписки
async def check_subscription(user_id: int) -> bool:
    try:
        chat_member = await bot.get_chat_member(GROUP_CHAT_ID, user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logging.error(f"Помилка перевірки підписки: {e}")
        return False

# Middleware
class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject, data: Dict[str, Any]) -> Any:
        if isinstance(event, types.Message):
            if not await check_subscription(event.from_user.id):
                await event.reply("🚫 Щоб користуватись ботом, підпишіться на групу:", reply_markup=subscribe_kb)
                return
        return await handler(event, data)

dp.message.middleware(SubscriptionMiddleware())

# Обробники команд
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("✅ Ви підписані! Ласкаво просимо до бота!")

@dp.message(F.text == "Меню")
@dp.message(Command("menu"))
async def menu_handler(message: types.Message):
    await message.reply("Ось ваше меню.")

@dp.message(F.text == "Пошук")
@dp.message(Command("poisk"))
async def search_handler(message: types.Message):
    await message.reply("Функція пошуку.")

@dp.message(F.text == "Список серіалів")
@dp.message(Command("serialiv"))
async def serials_handler(message: types.Message):
    await message.reply("Список серіалів.")

@dp.message(F.text == "За жанром")
@dp.message(Command("zhanrom"))
async def genres_handler(message: types.Message):
    await message.reply("Серіали за жанром.")

@dp.message(F.text == "Мультики")
@dp.message(Command("multik"))
async def cartoons_handler(message: types.Message):
    await message.reply("Мультики.")

@dp.message(F.text == "Фільми")
@dp.message(Command("filmi"))
async def movies_handler(message: types.Message):
    await message.reply("Фільми.")

@dp.message(F.text == "Запросити друга")
@dp.message(Command("zaprosy"))
async def invite_handler(message: types.Message):
    await message.reply("Запросіть друга за цим посиланням...")

@dp.message(F.text == "Перегляд")
@dp.message(Command("pereglyad"))
async def view_handler(message: types.Message):
    await message.reply("📺 Перегляд серіалів.")

@dp.message()
async def fallback_handler(message: types.Message):
    await message.reply("ℹ️ Невідома команда. Використовуйте меню або кнопки.")

# FastAPI endpoints
@app.post("/webhook")
async def webhook_handler(request: Request):
    data = await request.json()
    update = TelegramObject.model_validate(data)
    await dp.feed_update(bot, update)
    return {"status": "ok"}

@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()

# Запуск
if __name__ == "__main__":
uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))