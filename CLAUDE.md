# CLAUDE.md — Wati WhatsApp AI Bot

## Project Overview

A WhatsApp AI chatbot that:
1. Receives inbound messages via Wati webhook
2. Maintains per-conversation chat history (keyed by phone number)
3. Passes history as context to Claude (Anthropic API)
4. Sends Claude's response back via Wati's send message API

Primary use case: handling inbound replies from WhatsApp broadcast campaigns for VIE Collective (a luxury residential real estate project in New Cairo launching April 15th).

---

## Tech Stack

- **Python 3.11+**
- **FastAPI** — webhook server
- **uvicorn** — local ASGI server
- **httpx** — async HTTP client for Wati API calls
- **OpenAI SDK** — OpenAI API
- **ngrok** — local tunnel for webhook development
- **In-memory dict** — conversation history store (dev only)

---

## Project Structure

```
wati-ai-bot/
├── CLAUDE.md
├── .env
├── .env.example
├── requirements.txt
├── main.py              # FastAPI app entry point
├── webhook.py           # Webhook handler logic
├── wati.py              # Wati API client
├── ai.py                # Claude AI logic
├── history.py           # Conversation history store
└── config.py            # Settings loaded from .env
```

---

## Environment Variables

```env
ANTHROPIC_API_KEY=sk-ant-...
WATI_API_URL=https://live-mt-server.wati.io/{your-instance-id}
WATI_API_TOKEN=your-wati-bearer-token
SYSTEM_PROMPT_PATH=prompts/vie_agent.txt   # optional, or inline in config
```

Never commit `.env`. Always use `.env.example` with placeholder values.

---

## Core Logic

### Webhook flow (`webhook.py`)
1. Receive POST from Wati
2. Extract `waId` (phone number) and `text` from payload
3. Append user message to `chat_history[waId]`
4. Call `get_ai_response(waId, chat_history[waId])`
5. Append assistant response to history
6. Call `wati.send_message(waId, response)`
7. Return `200 OK` immediately (respond fast — Wati will retry on timeout)

### History store (`history.py`)
- Dev: plain Python dict `{ phone: [ {role, content}, ... ] }`
- Keep last N messages to avoid hitting context limits (default: 20 turns)
- Production: swap for Redis or Postgres without changing interface

### AI logic (`ai.py`)
- Use `claude-sonnet-4-20250514` model
- Always include system prompt describing the bot's persona and knowledge
- Pass full conversation history as `messages` array
- `max_tokens: 500` — keep replies concise for WhatsApp

### Wati client (`wati.py`)
- `send_message(phone, text)` — POST to `/api/v1/sendSessionMessage/{phone}`
- Use Bearer token auth header
- Handle 24hr session window — session messages are free; outside window requires a template

---

## System Prompt Guidelines

The agent should:
- Represent VIE Collective professionally
- Answer questions about the project (location, pricing, amenities, lifestyle)
- Qualify leads (budget, timeline, use case — own vs. invest)
- Collect contact info if not already known
- Escalate to human (David) when lead is hot or question is out of scope
- Stay concise — WhatsApp messages should be 2-4 sentences max
- Respond in the same language the user writes in (Arabic or English)

---

## Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --port 8000

# In a separate terminal, start ngrok
ngrok http 8000

# Paste the ngrok HTTPS URL into Wati dashboard:
# Settings → Webhooks → Message Received → https://xxxx.ngrok.io/webhook
```

---

## Key Constraints

- **Always return 200 quickly** — do AI call inside a background task if needed to avoid Wati timeout retries
- **Phone numbers** from Wati come as `waId` — typically in format `201001234567` (no + prefix)
- **Session window** — you can only reply with free-form text within 24hrs of user's last message; outside that window you need an approved template
- **Meta policy** — only structured business automation flows allowed; do not position the bot as a general-purpose AI assistant
- **No sensitive data in history** — don't log or persist payment info or personal ID numbers

---

## Production Checklist

- [ ] Swap in-memory history for Redis (use `redis-py` with TTL of 24hrs)
- [ ] Add request signature verification (Wati webhook secret)
- [ ] Add logging (structured JSON logs)
- [ ] Deploy to Railway (set env vars in Railway dashboard)
- [ ] Point Wati webhook to Railway URL
- [ ] Load test with a small broadcast before April 15th launch
