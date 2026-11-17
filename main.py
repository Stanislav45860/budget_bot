import os
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import uvicorn

from mainkb import get_main_menu

BOT_TOKEN = os.environ.get("BOT_TOKEN")
MY_USER_ID = int(os.environ.get("MY_USER_ID", 0))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
app = FastAPI()

@dp.message(Command("start"))
async def start(message: types.Message):
    if message.from_user.id != MY_USER_ID:
        return
    await message.answer(
        "Привет! Я твой финансовый помощник.\nВыбери действие на клавиатуре ниже:",
        reply_markup=get_main_menu()
    )

@dp.message(lambda message: message.text == "💸 Трата")
async def menu_spend(message: types.Message):
    if message.from_user.id != MY_USER_ID:
        return
    await message.answer("Тут будет запись трат. (Скоро добавим)")

@dp.message(lambda message: message.text == "📊 Бюджеты")
async def menu_budgets(message: types.Message):
    if message.from_user.id != MY_USER_ID:
        return
    await message.answer("Тут будет управление бюджетами. (Скоро добавим)")

@dp.message(lambda message: message.text == "📈 Аналитика")
async def menu_analytics(message: types.Message):
    if message.from_user.id != MY_USER_ID:
        return
    await message.answer("Тут будет аналитика и графики. (Скоро добавим)")

@app.post("/webhook")
async def webhook(request: Request):
    update = types.Update(**await request.json())
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.get("/")
async def root():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))