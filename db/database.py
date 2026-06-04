import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

pool = None

async def init_db():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL)

async def get_db():
    async with pool.acquire() as connection:
        yield connection

async def save_anomaly(transaction, explanation, risk_level):
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO transactions (user_id, amount, merchant, transaction_type, is_anomaly, explanation)
            VALUES ($1, $2, $3, $4, $5, $6)
        """,
        transaction["user_id"],
        float(transaction["amount"]),
        transaction["merchant"],
        transaction["transaction_type"],
        True,
        f"[{risk_level}] {explanation}"
        )