import os
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
import database as db
import keyboards as kb

router = Router()
ADMIN_ID = int(os.getenv("ADMIN_ID"))

@router.message(Command("start"))
async def start(message: Message):
    services = await db.get_services()
    await message.answer(
        "Добро пожаловать в наш салон! Выберите услугу для записи:",
        reply_markup=kb.get_services_kb(services)
    )

@router.callback_query(F.data.startswith("book_"))
async def process_booking(callback: CallbackQuery, bot: Bot):
    service_id = int(callback.data.split("_")[1])
    app_id = await db.create_appointment(
        callback.from_user.id, 
        callback.from_user.full_name, 
        service_id
    )
    
    app_info = await db.get_appointment_info(app_id)
    
    await callback.message.edit_text(
        f"✅ Вы успешно записаны на: {app_info['service_name']}\nID записи: {app_id}",
        reply_markup=kb.user_cancel_kb(app_id)
    )
    
    await bot.send_message(
        ADMIN_ID,
        f"🔔 Новая заявка #{app_id}!\nКлиент: {callback.from_user.full_name}\nУслуга: {app_info['service_name']}",
        reply_markup=kb.admin_cancel_kb(app_id)
    )

@router.callback_query(F.data.startswith("user_cancel_"))
async def user_cancel(callback: CallbackQuery, bot: Bot):
    app_id = int(callback.data.split("_")[2])
    await db.cancel_appointment(app_id)
    await callback.message.edit_text("❌ Вы отменили свою запись.")
    await bot.send_message(
        ADMIN_ID,
        f"⚠️ Клиент {callback.from_user.full_name} отменил запись #{app_id}"
    )

@router.callback_query(F.data.startswith("admin_cancel_"))
async def admin_cancel(callback: CallbackQuery, bot: Bot):
    app_id = int(callback.data.split("_")[2])
    app_info = await db.get_appointment_info(app_id)
    await db.cancel_appointment(app_id)
    await callback.message.answer(f"✅ Запись #{app_id} отменена админом.")
    try:
        await bot.send_message(
            app_info['user_id'],
            f"К сожалению, ваша запись #{app_id} на '{app_info['service_name']}' была отменена администратором."
        )
    except Exception:
        pass