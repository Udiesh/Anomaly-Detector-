import redis
import os
import json
import joblib
import asyncio
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
from db.database import init_db, save_anomaly
import sys
from websocket_manager import manager

load_dotenv()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
r = redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)
model = joblib.load("model/anomaly_model.pkl")
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_explanation(transaction):
    prompt = f"""
A financial transaction was flagged as anomalous by an ML model.
Details:
- User: {transaction['user_id']}
- Amount: ₹{transaction['amount']}
- Merchant: {transaction['merchant']}
- Type: {transaction['transaction_type']}

Write 2 sentences explaining why this transaction is suspicious.
Only use the information provided above. Do NOT invent statistics, averages, or assumptions about the merchant type.
Focus on what's actually unusual: the amount size, transaction direction, or combination of factors.
Use ₹ symbol.
"""
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def update_risk_score(user_id, amount):
    key = f"risk:{user_id}"
    current = r.get(key)
    current = float(current) if current else 0.0
    
    if amount > 15000:
        current += 30
    elif amount > 10000:
        current += 20
    elif amount > 5000:
        current += 10
    
    r.set(key, current)
    return current

def get_risk_level(score):
    if score >= 50:
        return "HIGH"
    elif score >= 20:
        return "MEDIUM"
    else:
        return "LOW"

async def consume():
    await init_db()
    last_id = "0"
    while True:
        results = r.xread({"transactions": last_id}, block=1000, count=10)
        if results:
            for stream, messages in results:
                for msg_id, data in messages:
                    amount = float(data["amount"])
                    hour = datetime.now().hour
                    features = np.array([[amount, hour]])
                    prediction = model.predict(features)
                    is_anomaly = prediction[0] == -1
                    if is_anomaly:
                        explanation = get_explanation(data)
                        score = update_risk_score(data["user_id"], amount)
                        level = get_risk_level(score)
                        print(f"ANOMALY DETECTED: {data}")
                        print(f"Explanation: {explanation}")
                        print(f"Risk Level: {level} (score: {score})")
                        await save_anomaly(data, explanation, level)
                        await manager.broadcast(json.dumps({
                                "user_id": data["user_id"],
                                "amount": amount,
                                "merchant": data["merchant"],
                                "explanation": explanation,
                                "risk_level": level
                            }))
                    else:
                        print(f"Normal: {data}")
                    last_id = msg_id

if __name__ == "__main__":
    asyncio.run(consume())