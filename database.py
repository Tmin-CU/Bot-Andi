import aiomysql
import os
from dotenv import load_dotenv

load_dotenv()

async def get_db_connection():
    return await aiomysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        db=os.getenv("DB_NAME"),
        autocommit=True
    )

async def init_db():
    conn = await get_db_connection()
    async with conn.cursor() as cur:
        await cur.execute("""
            CREATE TABLE IF NOT EXISTS services (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                price INT
            )
        """)
        await cur.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id BIGINT,
                user_name VARCHAR(255),
                service_id INT,
                status VARCHAR(50) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (service_id) REFERENCES services(id)
            )
        """)
        await cur.execute("SELECT COUNT(*) FROM services")
        if (await cur.fetchone())[0] == 0:
            services = [('Стрижка', 1500), ('Маникюр', 2000), ('Окрашивание', 5000)]
            await cur.executemany("INSERT INTO services (name, price) VALUES (%s, %s)", services)
    conn.close()

async def get_services():
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cur:
        await cur.execute("SELECT * FROM services")
        return await cur.fetchall()

async def create_appointment(user_id, user_name, service_id):
    conn = await get_db_connection()
    async with conn.cursor() as cur:
        await cur.execute(
            "INSERT INTO appointments (user_id, user_name, service_id) VALUES (%s, %s, %s)",
            (user_id, user_name, service_id)
        )
        return cur.lastrowid

async def cancel_appointment(appointment_id):
    conn = await get_db_connection()
    async with conn.cursor() as cur:
        await cur.execute("UPDATE appointments SET status = 'cancelled' WHERE id = %s", (appointment_id,))
    conn.close()

async def get_appointment_info(appointment_id):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cur:
        await cur.execute("""
            SELECT a.*, s.name as service_name 
            FROM appointments a 
            JOIN services s ON a.service_id = s.id 
            WHERE a.id = %s
        """, (appointment_id,))
        return await cur.fetchone()