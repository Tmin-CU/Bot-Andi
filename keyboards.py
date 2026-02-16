from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

def get_services_kb(services):
    builder = InlineKeyboardBuilder()
    for s in services:
        builder.row(InlineKeyboardButton(
            text=f"{s['name']} - {s['price']} руб.", 
            callback_data=f"book_{s['id']}")
        )
    return builder.as_markup()

def admin_cancel_kb(appointment_id):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="❌ Отменить запись (Админ)", 
        callback_data=f"admin_cancel_{appointment_id}")
    )
    return builder.as_markup()

def user_cancel_kb(appointment_id):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="❌ Отменить мою запись", 
        callback_data=f"user_cancel_{appointment_id}")
    )
    return builder.as_markup()