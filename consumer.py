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


def update_user_profile(user_id, amount, merchant):
    """Update rolling average and merchant history for user."""
    r.incrbyfloat(f"user:{user_id}:total_amount", amount)
    r.incr(f"user:{user_id}:tx_count")
    r.sadd(f"user:{user_id}:merchants", merchant)


def get_user_context(user_id, amount, merchant):
    """Compute deviation from user average and merchant familiarity."""
    total = r.get(f"user:{user_id}:total_amount")
    count = r.get(f"user:{user_id}:tx_count")
    
    avg = float(total) / float(count) if total and count else None
    deviation = round((amount - avg) / avg * 100, 1) if avg else None
    is_new_merchant = not r.sismember(f"user:{user_id}:merchants", merchant)
    
    return {
        "avg_amount": round(avg, 2) if avg else None,
        "deviation_pct": deviation,
        "is_new_merchant": is_new_merchant
    }


def get_explanation(transaction, context):
    avg_line = (
        f"- User's average transaction: ₹{context['avg_amount']} "
        f"(this is {context['deviation_pct']}% {'above' if context['deviation_pct'] > 0 else 'below'} average)"
        if context["avg_amount"] else "- User's transaction history: insufficient data"
    )
    merchant_line = (
        "- Merchant: NEVER seen before for this user"
        if context["is_new_merchant"]
        else "- Merchant: previously transacted with"
    )

    prompt = f"""You are a fraud analyst. One sentence only per instruction.

    Transaction:
    - User: {transaction['user_id']}
    - Amount: ₹{transaction['amount']}
    - Type: {transaction['transaction_type']}
    {avg_line}
    {merchant_line}

    Sentence 1: State the numerical deviation or merchant status from the data above only.
    Sentence 2: Name one specific fraud type this pattern matches:
- account takeover: large unusual DEBIT, possible stolen credentials
- money laundering: large unusual CREDIT/deposit from unknown source  
- card testing: multiple small transactions to verify card
- social engineering: manipulated user into initiating transaction
Pick based on transaction type and amount. One sentence only."""

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
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


def get_confidence(features):
    raw_score = model.decision_function(features)[0]
    confidence = round(min(max(-raw_score / 0.3 * 100, 0), 100), 1)  # 0.5 → 0.3
    return raw_score, confidence


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

                    # update profile BEFORE context fetch so merchant history is current
                    update_user_profile(data["user_id"], amount, data["merchant"])
                    context = get_user_context(data["user_id"], amount, data["merchant"])

                    raw_score, confidence = get_confidence(features)
                    is_anomaly = raw_score < 0

                    if is_anomaly:
                        explanation = get_explanation(data, context)
                        score = update_risk_score(data["user_id"], amount)
                        level = get_risk_level(score)

                        print(f"ANOMALY: {data} | confidence: {confidence}% | risk: {level}")
                        print(f"Explanation: {explanation}")

                        await save_anomaly(data, explanation, level, confidence)
                        await manager.broadcast(json.dumps({
                            "user_id": data["user_id"],
                            "amount": amount,
                            "merchant": data["merchant"],
                            "transaction_type": data["transaction_type"],
                            "explanation": explanation,
                            "risk_level": level,
                            "confidence": confidence
                        }))
                    else:
                        print(f"Normal: {data}")

                    last_id = msg_id


if __name__ == "__main__":
    asyncio.run(consume())