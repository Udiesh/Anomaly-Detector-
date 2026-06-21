# FTRACE — Financial Transaction Anomaly Detector

Real-time fraud detection pipeline. Streams synthetic transactions, scores them for anomalies using Isolation Forest, generates plain-English fraud explanations via LLM, and pushes results to a live dashboard over WebSockets.

## Why this exists

Most fraud-detection demos stop at "flag the anomaly." FTRACE goes one step further — every flagged transaction gets a natural-language explanation (deviation from user's average, merchant familiarity, likely fraud pattern) so the output is actually usable by a human reviewer, not just a score.

## Architecture

```
Producer → Redis Stream → Consumer → [Isolation Forest] → [Groq LLM] → Postgres
                                              ↓
                                        WebSocket → React Dashboard
```

- **Producer** generates synthetic transactions (90% normal, 10% anomalous amount ranges) and pushes to a Redis Stream.
- **Consumer** reads the stream, maintains a rolling per-user profile (average transaction amount, known merchants) in Redis, scores each transaction with a pre-trained Isolation Forest model, and — if flagged — calls Groq (`llama-3.1-8b-instant`) to generate a two-sentence explanation: the statistical deviation, and the closest-matching fraud pattern (account takeover, money laundering, card testing, social engineering).
- **Postgres** stores flagged transactions with risk level, confidence, and explanation.
- **FastAPI** exposes REST endpoints (`/anomalies`, `/risk/{user_id}`) and a WebSocket (`/ws`) for live broadcast.
- **React dashboard** (Recharts) renders incoming anomalies in real time, Bloomberg-terminal-styled.

## Stack

| Layer | Tech |
|---|---|
| Streaming | Redis Streams |
| ML scoring | scikit-learn (Isolation Forest) |
| Explanation | Groq API (Llama 3.1 8B) |
| Backend | FastAPI, asyncpg |
| Database | PostgreSQL |
| Frontend | React, Recharts, WebSockets |
| Infra | Docker, docker-compose |

## Key design decisions

- **Isolation Forest over supervised models** — no labeled fraud dataset available; Isolation Forest is unsupervised, fits the synthetic-stream setup, and is cheap enough to score in real time.
- **Redis Streams over Kafka** — single-node, low-throughput demo doesn't need Kafka's complexity; Streams give consumer groups and persistence with near-zero ops overhead.
- **Per-user rolling profile in Redis** — anomaly detection is relative to *each user's* normal behavior, not a global threshold. A ₹10,000 transaction means something different for different users.
- **LLM explanation is constrained, not freeform** — prompt forces exactly two sentences (deviation stated from data, fraud type picked from a fixed list) to keep output deterministic enough to display in a UI without surprises.

## Running locally

```bash
git clone <repo-url>
cd <repo-folder>
docker compose up --build
```

Create a `.env` file in the project root with:

```
DATABASE_URL=postgresql://ftrace:ftrace@postgres:5432/ftrace
REDIS_URL=redis://redis:6379
GROQ_API_KEY=your_groq_api_key
POSTGRES_DB=ftrace
POSTGRES_USER=ftrace
POSTGRES_PASSWORD=ftrace
```

Get a free Groq API key at [console.groq.com](https://console.groq.com).

- Dashboard: `http://localhost:3000`
- API: `http://localhost:8000/anomalies`

## What I'd improve next

- Replace synthetic producer with a real (anonymized) transaction dataset for more realistic anomaly distribution.
- Add Alembic migrations instead of inline `CREATE TABLE IF NOT EXISTS`.
- Move model retraining into a scheduled job instead of a static `.pkl`.
