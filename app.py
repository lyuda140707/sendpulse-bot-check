import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import TelegramObject, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from aiogram.filters import Command

# Токен та налаштування
API_TOKEN = '7460110326:AAFZirpV7YU5T-OxwDegP0EemKjX0HUV4Gw'
GROUP_CHAT_ID = '-1002591662949'
GROUP_URL = 'https://t.me/proKinotochka'

# Налаштування логування
logging.basicConfig(level=logging.INFO)

# Ініціалізація бота та диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Клавіатура для підписки
subscribe_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔔 Підписатися на групу", url=GROUP_URL)]
])

# Функція для перевірки підписки користувача
async def check_subscription(user_id: int) -> bool:
    try:
        chat_member = await bot.get_chat_member(GROUP_CHAT_ID, user_id)
        logging.info(f"User {user_id} status: {chat_member.status}")
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logging.error(f"Помилка перевірки підписки для {user_id}: {e}")
        return False

# Middleware для перевірки підписки
class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, types.Message):
            if not await check_subscription(event.from_user.id):
                await event.reply("🚫 Щоб користуватись ботом, підпишіться на групу:", reply_markup=subscribe_kb)
                return  # Не викликаємо наступний обробник
        return await handler(event, data)

# Реєстрація middleware
dp.message.middleware(SubscriptionMiddleware())

# Обробка команди /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("✅ Ви підписані! Ласкаво просимо до бота!")

# Інші обробники (Меню, Пошук, тощо) – без змін

@dp.message(F.text == "Меню")
async def menu_text_handler(message: types.Message):
    await message.reply("Ось ваше меню.")

@dp.message(Command("menu"))
async def menu_command_handler(message: types.Message):
    await message.reply("Ось ваше меню.")

@dp.message(F.text == "Пошук")
async def search_text_handler(message: types.Message):
    await message.reply("Функція пошуку.")

@dp.message(Command("poisk"))
async def search_command_handler(message: types.Message):
    await message.reply("Функція пошуку.")

@dp.message(F.text == "Список серіалів")
async def serials_text_handler(message: types.Message):
    await message.reply("Список серіалів.")

@dp.message(Command("serialiv"))
async def serials_command_handler(message: types.Message):
    await message.reply("Список серіалів.")

@dp.message(F.text == "За жанром")
async def genres_text_handler(message: types.Message):
    await message.reply("Серіали за жанром.")

@dp.message(Command("zhanrom"))
async def genres_command_handler(message: types.Message):
    await message.reply("Серіали за жанром.")

@dp.message(F.text == "Мультики")
async def cartoons_text_handler(message: types.Message):
    await message.reply("Мультики.")

@dp.message(Command("multik"))
async def cartoons_command_handler(message: types.Message):
    await message.reply("Мультики.")

@dp.message(F.text == "Фільми")
async def movies_text_handler(message: types.Message):
    await message.reply("Фільми.")

@dp.message(Command("filmi"))
async def movies_command_handler(message: types.Message):
    await message.reply("Фільми.")

@dp.message(F.text == "Запросити друга")
async def invite_text_handler(message: types.Message):
    await message.reply("Запросіть друга за цим посиланням...")

@dp.message(Command("zaprosy"))
async def invite_command_handler(message: types.Message):
    await message.reply("Запросіть друга за цим посиланням...")

@dp.message(Command("pereglyad"))
async def view_handler(message: types.Message):await message.reply("📺 Перегляд серіалів.")

@dp.message(F.text == "Перегляд")
async def view_text_handler(message: types.Message):
    await message.reply("📺 Перегляд серіалів.")

@dp.message()
async def fallback_handler(message: types.Message):
    await message.reply("ℹ️ Невідома команда. Використовуйте меню або кнопки.")

async def main():
    await dp.start_polling(bot)

# Запуск бота
if __name__ == '__main__':
    asyncio.run(dp.start_polling(bot))