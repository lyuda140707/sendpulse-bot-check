import logging
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import TelegramObject, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from typing import Callable, Dict, Any, Awaitable
import uvicorn
from aiogram.types import Update
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Меню-клавіатура
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Пошук🔍"), KeyboardButton(text="Список серіалів📺"), KeyboardButton(text="За жанром")],
        [KeyboardButton(text="Мультики👧"), KeyboardButton(text="Фільми")],
        [KeyboardButton(text="Запросити друга🢜🢛")]
    ],
    resize_keyboard=True
)

# Змінні середовища
API_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
GROUP_CHAT_ID = '-1002564548405'
GROUP_URL = 'https://t.me/kinotochkanews'

# Список дозволених користувачів (заміни на свій ID)
allowed_users = [123456789]

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
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, types.Message):
            # ✨ Пропустити перевірку підписки для /my_status
            if event.text and event.text.startswith("/my_status"):
                return await handler(event, data)

            if not await check_subscription(event.from_user.id):
                await event.reply("❌ Щоб користуватись ботом, підпишіться на групу:", reply_markup=subscribe_kb)
                return
        return await handler(event, data)

dp.message.middleware(SubscriptionMiddleware())

# Обробники команд
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    if await check_subscription(message.from_user.id):
        await message.answer("✅ Ви підписані! Ласкаво просимо до бота!\nОбирай жанр, або натисни «Меню» 👇", reply_markup=main_menu)
    else:
        await message.answer("❌ Щоб користуватись ботом, підпишіться на групу:", reply_markup=subscribe_kb)

@dp.message(Command("help"))
async def help_handler(message: types.Message):
    await message.answer("❓ Натисніть /menu, щоб побачити всі доступні функції.", reply_markup=main_menu)

@dp.message(Command("id"))
async def get_id(message: types.Message):
    await message.answer(f"Ваш Telegram ID: {message.from_user.id}")
    
@dp.message(Command("my_status"))
async def my_status(message: types.Message):
    try:
        chat_member = await bot.get_chat_member(GROUP_CHAT_ID, message.from_user.id)
        await message.answer(f"📋 Ваш статус у групі: {chat_member.status}")
    except Exception as e:
        await message.answer(f"❌ Помилка перевірки: {e}")

@dp.message(F.text == "Меню")
@dp.message(Command("menu"))
async def menu_handler(message: types.Message):
    await message.answer("Ось ваше меню:", reply_markup=main_menu)

@dp.message(F.text == "Пошук🔍")
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
async def check_user(message: types.Message):
    if message.from_user.id not in allowed_users:
        await message.answer("⛔️ У вас немає доступу до цього бота.")
        return
    await message.reply("ℹ️ Невідома команда. Використовуйте меню або кнопки.")

@app.post("/sendpulse-webhook")
async def sendpulse_webhook_handler(request: Request):
    try:
        data = await request.json()
        logging.info(f"SendPulse webhook: {data}")

        if isinstance(data, list) and data:
            telegram_id = data[0].get("telegram_id")
        elif isinstance(data, dict):
            telegram_id = data.get("telegram_id")
        else:
            telegram_id = None

        if telegram_id:
            is_subscribed = await check_subscription(int(telegram_id))
            return JSONResponse(content={"allowed": is_subscribed})

        return JSONResponse(content={"allowed": False})
    except Exception as e:
        logging.error(f"SendPulse error: {e}")
        return JSONResponse(content={"allowed": False})
        
@dp.message(Command("get_chat_id"))
async def get_chat_id(message: types.Message):
    await message.answer(
        f"🆔 Chat ID: `{message.chat.id}`\n📌 Тип: {message.chat.type}\n📛 Назва: {message.chat.title}",
        parse_mode="Markdown"
    )


@app.post("/webhook")
async def telegram_webhook_handler(request: Request):
    try:
        data = await request.json()

        # Перевіряємо, чи це точно Telegram-оновлення
        if isinstance(data, dict) and "update_id" in data:
            update = Update.model_validate(data)
            await dp.feed_update(bot, update)
        else:
            logging.warning(f"❌ Отримано не Telegram-дані. Пропускаємо: {data}")
            
    except Exception as e:
        logging.error(f"Telegram Webhook error: {e}")
    
    return {"status": "ok"}

@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()

@app.get("/")
async def root():
    return {"status": "OK"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
