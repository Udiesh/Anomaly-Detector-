from fastapi import APIRouter
from db.database import pool
import redis
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
r = redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)

def get_risk_level(score):
    if score >= 50:
        return "HIGH"
    elif score >= 20:
        return "MEDIUM"
    else:
        return "LOW"

@router.get("/anomalies")
async def get_anomalies():
    from db.database import pool
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM transactions WHERE is_anomaly = true ORDER BY timestamp DESC")
        return [dict(row) for row in rows]

@router.get("/risk/{user_id}")
async def get_risk(user_id: str):
    from db.database import pool
    score = r.get(f"risk:{user_id}")
    score = float(score) if score else 0.0
    return {"user_id": user_id, "score": score, "level": get_risk_level(score)}