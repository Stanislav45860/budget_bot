import os
import sqlite3
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
import uvicorn

BOT_TOKEN = os.environ.get("BOT_TOKEN")
MY_USER_ID = int(os.environ.get("MY_USER_ID", 0))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
app = FastAPI()

def init_db():
    conn = sqlite3.connect("budget.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            category TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

@dp.message(Command("start"))
async def start(message: types.Message):
    if message.from_user.id != MY_USER_ID:
        return
    await message.answer("Бот работает! Пиши: /spend 50 Маркетплейсы наушники")

@dp.message(Command("spend"))
async def spend(message: types.Message):
    if message.from_user.id != MY_USER_ID:
        return
    
    parts = message.text.split(maxsplit=3)
    if len(parts) < 3:
        await message.answer("Формат: /spend <сумма> <категория> <описание>")
        return
    
    try:
        amount = float(parts[1])
    except ValueError:
        await message.answer("Сумма должна быть числом.")
        return
    
    category = parts[2]
    description = parts[3] if len(parts) > 3 else ""
    
    conn = sqlite3.connect("budget.db")
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO transactions (user_id, amount, category, description) VALUES (?, ?, ?, ?)",
        (message.from_user.id, amount, category, description)
    )
    conn.commit()
    conn.close()
    
    await message.answer(f"✅ Записано: {amount} BYN, {category}, {description}")

@dp.message(Command("history"))
async def history(message: types.Message):
    if message.from_user.id != MY_USER_ID:
        return
    
    conn = sqlite3.connect("budget.db")
    cur = conn.cursor()
    cur.execute("SELECT amount, category, description FROM transactions ORDER BY id DESC LIMIT 5")
    rows = cur.fetchall()
    conn.close()
    
    if not rows:
        await message.answer("Пока нет записей.")
        return
    
    lines = ["📋 Последние 5 трат:\n"]
    for row in rows:
        lines.append(f"• {row[0]} BYN — {row[1]} — {row[2]}")
    await message.answer("\n".join(lines))

@app.post("/webhook")
async def webhook(request: Request):
    update = types.Update(**await request.json())
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.on_event("startup")
async def on_startup():
    init_db()
    # Устанавливаем webhook
    await bot.set_webhook(WEBHOOK_URL)

@app.get("/")
async def root():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
