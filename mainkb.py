from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💸 Трата")],
            [KeyboardButton(text="📊 Бюджеты")],
            [KeyboardButton(text="📈 Аналитика")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери действие..."
    )
    return keyboard