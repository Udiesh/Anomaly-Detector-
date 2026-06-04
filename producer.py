import redis
import os
import json
import random
import time
from dotenv import load_dotenv

load_dotenv()

r = redis.from_url(os.getenv("REDIS_URL"), socket_connect_timeout=5)

def generate_transaction():
    return{
        "user_id":random.choice(["user1", "user2", "user3", "user4", "user5"]),
        "amount": str(round(random.uniform(10, 500) if random.random() < 0.9 else random.uniform(5000, 20000), 2)),
        "merchant":random.choice(["Merchant A", "Merchant B", "Merchant C", "Merchant D", "Merchant E"]),
        "transaction_type":random.choice(['debit', 'credit'])

    }

def produce():
    while True:
        transaction = generate_transaction()
        r.xadd("transactions", transaction)
  
        print(f"Produced: {transaction}")
        time.sleep(1)

if __name__ == "__main__":
    produce()