import aiosqlite
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = "salon_db.sqlite"

async def get_db_connection():
    return await aiosqlite.connect(DB_PATH)

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.execute("""
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price INTEGER NOT NULL
            )
        """
        )
        await db.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                user_name TEXT NOT NULL,
                service_id INTEGER NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (service_id) REFERENCES services(id)
            )
        """
        )
        async with db.execute("SELECT COUNT(*) as count FROM services") as cursor:
            row = await cursor.fetchone()
            if row['count'] == 0:
                services = [('Стрижка', 1500), ('Маникюр', 2000), ('Окрашивание', 5000)]
                await db.executemany("INSERT INTO services (name, price) VALUES (?, ?)", services)
        await db.commit()

async def get_services():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM services") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def create_appointment(user_id, user_name, service_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO appointments (user_id, user_name, service_id) VALUES (?, ?, ?)",
            (user_id, user_name, service_id)
        )
        last_id = cursor.lastrowid
        await db.commit()
        return last_id

async def cancel_appointment(appointment_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE appointments SET status = 'cancelled' WHERE id = ?", (appointment_id,))
        await db.commit()

async def get_appointment_info(appointment_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT a.*, s.name as service_name 
            FROM appointments a 
            JOIN services s ON a.service_id = s.id 
            WHERE a.id = ?
        """, (appointment_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
