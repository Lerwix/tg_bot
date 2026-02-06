import asyncio
import json
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command
from aiogram.handlers import MessageHandler, CallbackQueryHandler
from config import BOT_TOKEN

JSON_FILE = "roles.json"


ROLE_BUTTONS = [
    ("media", "Медиа проекта"),
    ("developer", "Разработчик"),
    ("support", "Поддержка игроков"),
    ("tester", "Тестировщик"),
    ("builder", "Билдер"),
    ("moderator", "Модератор"),
]

def create_main_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=button, callback_data=f"role_{role}")]
            for role, button in ROLE_BUTTONS
        ]
    )
    return keyboard

def create_back_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="back")]]
    )

def load_applications_for_role(role_key):
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Ожидается структура: { "media": [...], "developer": [...], ... }
        return data.get(role_key, [])
    except Exception as e:
        return [f"Ошибка загрузки заявок: {e}"]

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "Выберите роль для просмотра заявок:",
        reply_markup=create_main_keyboard()
    )

@dp.callback_query()
async def callback_handler(callback: CallbackQuery):
    data = callback.data
    if data.startswith("role_"):
        role_key = data[5:]
        applications = load_applications_for_role(role_key)
        if not applications:
            text = "Заявок по этой роли нет."
        else:
            # Ожидается, что applications - список строк или словарей
            if isinstance(applications, list):
                app_list = []
                for i, app in enumerate(applications, 1):
                    if isinstance(app, dict):
                        # Просто объединим ключи: значения
                        app_text = "\n".join([f"<b>{k}</b>: {v}" for k, v in app.items()])
                    else:
                        app_text = str(app)
                    app_list.append(f"<b>Заявка {i}:</b>\n{app_text}")
                text = "\n\n".join(app_list)
            else:
                text = str(applications)

        # Отошлем заявки с кнопкой "Назад"
        await callback.message.edit_text(
            f"Заявки по выбранной роли:\n\n{text}",
            reply_markup=create_back_keyboard(),
            parse_mode=ParseMode.HTML,
        )
        await callback.answer()
    elif data == "back":
        # Назад к выбору ролей
        await callback.message.edit_text(
            "Выберите роль для просмотра заявок:",
            reply_markup=create_main_keyboard(),
        )
        await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())